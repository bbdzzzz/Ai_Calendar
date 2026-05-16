import json
import logging
from typing import Any

from openai import BadRequestError

from backend.agent.llm_client import chat_completion
from backend.agent.prompts import build_messages, _estimate_chars, _truncate_history
from backend.agent.tools import TOOLS
from backend.agent.tool_executor import execute_tool
from backend.core.config import settings
from backend.schemas.agent import AgentAction, AgentInput

logger = logging.getLogger(__name__)

_FALLBACK_ACTION = AgentAction(
    action_type="text_reply",
    text_response="抱歉，我没听懂，能再说一遍吗？",
    event_data=None,
    new_messages=[],
)


def _extract_last_event_tool_call(messages: list[dict]) -> dict | None:
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                func_name = tc.get("function", {}).get("name", "")
                if func_name in ("create_event", "update_event"):
                    try:
                        args = json.loads(tc["function"]["arguments"])
                        return {"action_type": func_name, "event_data": args}
                    except (json.JSONDecodeError, KeyError):
                        continue
    return None


def _parse_tool_calls_from_response(choice: Any) -> list[dict]:
    message = choice.message
    if not message.tool_calls:
        return []

    result = []
    for tc in message.tool_calls:
        result.append({
            "id": tc.id,
            "type": "function",
            "function": {
                "name": tc.function.name,
                "arguments": tc.function.arguments,
            },
        })
    return result


def _build_assistant_msg(message: Any, tool_calls_parsed: list[dict] | None = None) -> dict:
    msg: dict = {"role": "assistant", "content": message.content or ""}
    reasoning = getattr(message, "reasoning_content", None)
    if reasoning:
        msg["reasoning_content"] = reasoning
    if tool_calls_parsed:
        msg["tool_calls"] = tool_calls_parsed
    return msg


def _is_context_too_long_error(exc: Exception) -> bool:
    if isinstance(exc, BadRequestError):
        msg = str(exc).lower()
        return any(kw in msg for kw in ("context_length", "maximum context", "too many tokens", "token limit"))
    return False


def _emergency_truncate(messages: list[dict]) -> list[dict]:
    if len(messages) <= 2:
        return messages

    system_msg = messages[0]
    last_user_msg = messages[-1]
    history = messages[1:-1]

    half = len(history) // 2
    truncated = history[half:]

    while truncated:
        first = truncated[0]
        if first.get("role") == "assistant" and first.get("tool_calls"):
            tool_call_ids = {tc["id"] for tc in first["tool_calls"]}
            truncated = truncated[1:]
            while truncated and truncated[0].get("role") == "tool" and truncated[0].get("tool_call_id") in tool_call_ids:
                truncated = truncated[1:]
        else:
            truncated = truncated[1:]
        break

    result = [system_msg] + truncated + [last_user_msg]
    logger.warning("紧急截断: %d条 -> %d条", len(messages), len(result))
    return result


async def run(agent_input: AgentInput, db: Any = None) -> AgentAction:
    logger.info("Agent收到请求: user_id=%s, query=%s", agent_input.user_id, agent_input.current_query)

    if not settings.LLM_API_KEY:
        return AgentAction(
            action_type="text_reply",
            text_response=f"收到您的指令：{agent_input.current_query}。LLM未配置API Key，请在.env中设置LLM_API_KEY。",
            event_data=None,
            new_messages=[],
        )

    messages = build_messages(agent_input)
    new_messages: list[dict] = []
    truncated_once = False

    for round_num in range(settings.LLM_MAX_TOOL_ROUNDS):
        logger.info("Agent ReAct第%d轮, messages数=%d", round_num + 1, len(messages))

        try:
            response = await chat_completion(messages=messages, tools=TOOLS)
        except BadRequestError as e:
            if _is_context_too_long_error(e) and not truncated_once:
                logger.warning("上下文溢出, 尝试紧急截断重试: %s", str(e)[:100])
                messages = _emergency_truncate(messages)
                truncated_once = True
                try:
                    response = await chat_completion(messages=messages, tools=TOOLS)
                except Exception as retry_exc:
                    logger.error("截断重试仍失败: %s", retry_exc)
                    return AgentAction(
                        action_type="text_reply",
                        text_response="抱歉，对话太长了，请重新开始吧。",
                        event_data=None,
                        new_messages=[],
                    )
            else:
                logger.error("LLM调用异常: %s", e)
                return AgentAction(
                    action_type="text_reply",
                    text_response="抱歉，AI服务暂时不可用，请稍后再试。",
                    event_data=None,
                    new_messages=new_messages,
                )
        except Exception as e:
            logger.error("LLM调用异常: %s", e)
            return AgentAction(
                action_type="text_reply",
                text_response="抱歉，AI服务暂时不可用，请稍后再试。",
                event_data=None,
                new_messages=new_messages,
            )

        if not response.choices:
            logger.warning("LLM返回空choices")
            return AgentAction(
                action_type="text_reply",
                text_response=_FALLBACK_ACTION.text_response,
                event_data=None,
                new_messages=new_messages,
            )

        choice = response.choices[0]
        message = choice.message

        if not message.tool_calls:
            text_response = message.content or ""
            final_assistant_msg = _build_assistant_msg(message)
            new_messages.append(final_assistant_msg)

            event_info = _extract_last_event_tool_call(messages)

            action_type = "text_reply"
            event_data = None
            if event_info:
                action_type = event_info["action_type"]
                event_data = event_info["event_data"]

            logger.info("Agent最终回复: action_type=%s, text=%s", action_type, text_response[:50])
            return AgentAction(
                action_type=action_type,
                text_response=text_response,
                event_data=event_data,
                new_messages=new_messages,
            )

        tool_calls_parsed = _parse_tool_calls_from_response(choice)
        assistant_msg = _build_assistant_msg(message, tool_calls_parsed)
        messages.append(assistant_msg)
        new_messages.append(assistant_msg)

        for tc in tool_calls_parsed:
            tool_name = tc["function"]["name"]
            tool_args_str = tc["function"]["arguments"]
            tool_call_id = tc["id"]

            try:
                tool_args = json.loads(tool_args_str)
            except json.JSONDecodeError:
                tool_args = {}

            logger.info("工具调用: %s(%s)", tool_name, tool_args_str[:100])

            if db is not None:
                tool_result = execute_tool(db, agent_input.user_id, tool_name, tool_args)
            else:
                tool_result = json.dumps({"status": "error", "message": "数据库会话不可用"}, ensure_ascii=False)

            logger.info("工具结果: %s", tool_result[:100])

            tool_msg = {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_result,
            }
            messages.append(tool_msg)
            new_messages.append(tool_msg)

    logger.warning("Agent达到最大工具调用轮数(%d)", settings.LLM_MAX_TOOL_ROUNDS)
    last_text = ""
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and msg.get("content"):
            last_text = msg["content"]
            break

    return AgentAction(
        action_type="text_reply",
        text_response=last_text or "抱歉，处理过程过于复杂，请简化您的需求。",
        event_data=None,
        new_messages=new_messages,
    )
