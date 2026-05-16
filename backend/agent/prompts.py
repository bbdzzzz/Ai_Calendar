import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.models import Conversation, Event, User
from backend.schemas.agent import AgentInput

logger = logging.getLogger(__name__)

WEEKDAYS_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def _parse_current_time(time_str: str) -> datetime:
    for sep in (" 星期一", " 星期二", " 星期三", " 星期四", " 星期五", " 星期六", " 星期日",
                " Monday", " Tuesday", " Wednesday", " Thursday", " Friday", " Saturday", " Sunday"):
        if sep in time_str:
            time_str = time_str[: time_str.index(sep)]
            break
    return datetime.fromisoformat(time_str)


def build_system_prompt(current_context: dict) -> str:
    now = _parse_current_time(current_context["current_time"])
    weekday = WEEKDAYS_CN[now.weekday()]
    time_str = now.strftime("%Y年%m月%d日 %H:%M") + f" {weekday}"

    user_prefs = current_context.get("user_preferences", {})
    work_start = user_prefs.get("work_start", "09:00")
    work_end = user_prefs.get("work_end", "18:00")

    upcoming = current_context.get("upcoming_events_summary", "无")

    return f"""你是智能日程助手，帮助用户管理日程安排。

【当前时间】{time_str}

【时间解析规则】
- "今天"={now.strftime('%Y-%m-%d')}，"明天"={(now + timedelta(days=1)).strftime('%Y-%m-%d')}，"后天"={(now + timedelta(days=2)).strftime('%Y-%m-%d')}
- 上午/下午/晚上对应: 上午=8-12点, 下午=12-18点, 晚上=18-22点
- "3点"默认指下午15:00，"早上9点"指09:00
- 未指定结束时间时，默认时长1小时
- "下周一"等相对日期需根据当前时间计算具体日期
- 所有时间输出必须为ISO 8601格式，如2025-05-21T15:00:00

【用户偏好】
- 工作时间: {work_start} - {work_end}
- 排程时尽量避开休息时段

【近期日程摘要】
{upcoming}

【行动约束】
1. 创建或修改日程前，务必先调用query_events探查时间冲突
2. 若有冲突，向用户说明冲突详情并建议替代时间，不要强行创建
3. 回复必须简短口语化，适合语音播报，禁止使用Markdown格式（如加粗、列表、代码块等）
4. 如果用户只是闲聊或提问（如"今天几号"），直接回复即可，无需调用工具
5. 修改日程时，需先通过query_events或上下文确认要修改的日程ID
6. 删除日程时，同样需先确认日程ID"""


def _estimate_chars(msg: dict) -> int:
    total = len(msg.get("content", ""))
    if msg.get("tool_calls"):
        total += len(json.dumps(msg["tool_calls"], ensure_ascii=False))
    if msg.get("reasoning_content"):
        total += len(msg["reasoning_content"])
    return total


def _truncate_history(messages: list[dict], max_chars: int) -> list[dict]:
    if not messages:
        return messages

    total = sum(_estimate_chars(m) for m in messages)
    if total <= max_chars:
        return messages

    logger.info("上下文超限: total=%d chars, max=%d chars, 开始截断", total, max_chars)

    while messages and total > max_chars:
        first = messages[0]
        drop_chars = _estimate_chars(first)
        total -= drop_chars
        messages = messages[1:]

        if first.get("role") == "assistant" and first.get("tool_calls"):
            tool_call_ids = {tc["id"] for tc in first["tool_calls"]}
            while messages and messages[0].get("role") == "tool" and messages[0].get("tool_call_id") in tool_call_ids:
                drop_tool_chars = _estimate_chars(messages[0])
                total -= drop_tool_chars
                messages = messages[1:]

    logger.info("截断后: %d条消息, %d chars", len(messages), total)
    return messages


def build_agent_input(db: Session, user_id: int, query: str) -> AgentInput:
    user = db.query(User).filter(User.id == user_id).first()
    user_preferences = {}
    if user and user.preferences:
        user_preferences = user.preferences

    window = timedelta(minutes=settings.LLM_HISTORY_WINDOW_MINUTES)
    cutoff = datetime.now() - window

    history_records = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id, Conversation.created_at >= cutoff)
        .order_by(Conversation.created_at.desc())
        .limit(40)
        .all()
    )

    conversation_history = []
    for r in reversed(history_records):
        msg = {"role": r.role, "content": r.content or ""}
        if r.role == "assistant" and r.tool_calls:
            msg["tool_calls"] = r.tool_calls
        if r.role == "tool" and r.tool_calls:
            tc = r.tool_calls
            if isinstance(tc, dict) and "tool_call_id" in tc:
                msg["tool_call_id"] = tc["tool_call_id"]
            elif isinstance(tc, str):
                msg["tool_call_id"] = tc
        conversation_history.append(msg)

    now = datetime.now()
    upcoming_events = (
        db.query(Event)
        .filter(Event.user_id == user_id, Event.start_time >= now, Event.start_time < now + timedelta(days=7))
        .order_by(Event.start_time)
        .limit(10)
        .all()
    )

    if upcoming_events:
        lines = []
        for e in upcoming_events:
            lines.append(f"- {e.start_time.strftime('%m/%d %H:%M')}-{e.end_time.strftime('%H:%M')} {e.title}({e.status})")
        upcoming_summary = "\n".join(lines)
    else:
        upcoming_summary = "无"

    current_context = {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S") + " " + WEEKDAYS_CN[now.weekday()],
        "user_preferences": user_preferences,
        "upcoming_events_summary": upcoming_summary,
    }

    return AgentInput(
        user_id=user_id,
        current_query=query,
        conversation_history=conversation_history,
        current_context=current_context,
    )


def build_messages(agent_input: AgentInput) -> list[dict]:
    system_prompt = build_system_prompt(agent_input.current_context)
    messages = [{"role": "system", "content": system_prompt}]

    history = []
    for msg in agent_input.conversation_history:
        role = msg.get("role")
        if role in ("user", "assistant"):
            entry = {"role": role, "content": msg.get("content", "")}
            if role == "assistant" and "tool_calls" in msg:
                entry["tool_calls"] = msg["tool_calls"]
            if "reasoning_content" in msg:
                entry["reasoning_content"] = msg["reasoning_content"]
            history.append(entry)
        elif role == "tool":
            entry = {"role": "tool", "content": msg.get("content", ""), "tool_call_id": msg.get("tool_call_id", "")}
            history.append(entry)

    history = _truncate_history(history, settings.LLM_MAX_HISTORY_CHARS)
    messages.extend(history)
    messages.append({"role": "user", "content": agent_input.current_query})
    return messages
