"""
测试13: Agent Prompt构建 + 上下文管理
运行: uv run python tests/test_13_agent_prompts.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.agent.prompts import build_system_prompt, build_messages, _estimate_chars, _truncate_history
from backend.core.config import settings
from backend.schemas.agent import AgentInput


def test_system_prompt():
    print("=== 测试System Prompt生成 ===")
    context = {
        "current_time": "2026-05-20 10:30:00 星期二",
        "user_preferences": {"work_start": "09:00", "work_end": "18:00"},
        "upcoming_events_summary": "- 05/20 14:00-15:00 产品评审会(confirmed)",
    }
    prompt = build_system_prompt(context)

    assert "智能日程助手" in prompt
    assert "2026年05月20日" in prompt
    assert "09:00" in prompt
    assert "18:00" in prompt
    assert "产品评审会" in prompt
    assert "query_events" in prompt
    assert "冲突" in prompt
    print("[PASS] System Prompt包含所有必要模块")
    print(f"  Prompt长度: {len(prompt)}字符")
    return True


def test_build_messages():
    print("=== 测试消息列表构建 ===")
    agent_input = AgentInput(
        user_id=1,
        current_query="明天下午3点开会",
        conversation_history=[
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好，有什么可以帮你？"},
        ],
        current_context={
            "current_time": "2026-05-20 10:30:00 星期二",
            "user_preferences": {},
            "upcoming_events_summary": "无",
        },
    )
    messages = build_messages(agent_input)

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "你好"
    assert messages[2]["role"] == "assistant"
    assert messages[3]["role"] == "user"
    assert messages[3]["content"] == "明天下午3点开会"
    print(f"[PASS] 消息列表构建正确: {len(messages)}条消息")
    return True


def test_build_messages_with_tool_history():
    print("=== 测试带工具历史的消息构建 ===")
    agent_input = AgentInput(
        user_id=1,
        current_query="改到4点",
        conversation_history=[
            {"role": "user", "content": "明天下午3点开会"},
            {"role": "assistant", "content": "", "tool_calls": [
                {"id": "call_1", "type": "function", "function": {"name": "query_events", "arguments": "{}"}},
            ]},
            {"role": "tool", "tool_call_id": "call_1", "content": '{"status": "success", "events": []}'},
            {"role": "assistant", "content": "好的，已为您安排明天下午3点的会议。"},
        ],
        current_context={
            "current_time": "2026-05-20 10:30:00 星期二",
            "user_preferences": {},
            "upcoming_events_summary": "无",
        },
    )
    messages = build_messages(agent_input)

    tool_msg = [m for m in messages if m["role"] == "tool"]
    assert len(tool_msg) == 1
    assert tool_msg[0]["tool_call_id"] == "call_1"
    print(f"[PASS] 工具历史消息构建正确: {len(messages)}条消息, 含{len(tool_msg)}条tool消息")
    return True


def test_estimate_chars():
    print("=== 测试字符估算 ===")
    msg1 = {"role": "user", "content": "你好世界"}
    assert _estimate_chars(msg1) == 4

    msg2 = {"role": "assistant", "content": "ok", "tool_calls": [
        {"id": "call_1", "type": "function", "function": {"name": "query_events", "arguments": '{"start_time": "2025-01-01"}'}},
    ]}
    chars = _estimate_chars(msg2)
    assert chars > 2
    print(f"[PASS] 字符估算: 纯文本={_estimate_chars(msg1)}, 含tool_calls={chars}")
    return True


def test_truncate_history_no_overflow():
    print("=== 测试截断: 无溢出时不截断 ===")
    history = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好呀"},
    ]
    result = _truncate_history(history, 1000)
    assert len(result) == 2
    print("[PASS] 无溢出时保持原样")
    return True


def test_truncate_history_basic():
    print("=== 测试截断: 基本截断 ===")
    history = [
        {"role": "user", "content": "a" * 500},
        {"role": "assistant", "content": "b" * 500},
        {"role": "user", "content": "c" * 500},
        {"role": "assistant", "content": "d" * 100},
    ]
    result = _truncate_history(history, 700)
    assert len(result) < len(history)
    assert result[-1]["content"].startswith("d")
    print(f"[PASS] 基本截断: {len(history)}条 -> {len(result)}条")
    return True


def test_truncate_history_with_tool_calls():
    print("=== 测试截断: tool_calls成对丢弃 ===")
    history = [
        {"role": "user", "content": "a" * 500},
        {"role": "assistant", "content": "", "tool_calls": [
            {"id": "call_1", "type": "function", "function": {"name": "query_events", "arguments": "{}"}},
        ]},
        {"role": "tool", "tool_call_id": "call_1", "content": "x" * 500},
        {"role": "assistant", "content": "查询结果为空"},
        {"role": "user", "content": "c" * 100},
        {"role": "assistant", "content": "好的"},
    ]
    result = _truncate_history(history, 300)
    tool_msgs = [m for m in result if m["role"] == "tool"]
    assistant_with_tc = [m for m in result if m.get("tool_calls")]
    orphan_tools = [t for t in tool_msgs if t["tool_call_id"] not in {
        tc["id"] for a in assistant_with_tc for tc in a.get("tool_calls", [])
    }]
    assert len(orphan_tools) == 0, f"存在孤立的tool消息: {orphan_tools}"
    print(f"[PASS] tool_calls成对丢弃: {len(history)}条 -> {len(result)}条, 无孤立tool消息")
    return True


def test_truncate_history_empty():
    print("=== 测试截断: 空列表 ===")
    result = _truncate_history([], 100)
    assert result == []
    print("[PASS] 空列表不报错")
    return True


def test_config_values():
    print("=== 测试上下文管理配置 ===")
    print(f"  LLM_HISTORY_WINDOW_MINUTES = {settings.LLM_HISTORY_WINDOW_MINUTES}")
    print(f"  LLM_MAX_HISTORY_CHARS = {settings.LLM_MAX_HISTORY_CHARS}")
    assert settings.LLM_HISTORY_WINDOW_MINUTES > 0
    assert settings.LLM_MAX_HISTORY_CHARS > 0
    print("[PASS] 配置值有效")
    return True


if __name__ == "__main__":
    results = []
    results.append(test_system_prompt())
    results.append(test_build_messages())
    results.append(test_build_messages_with_tool_history())
    results.append(test_estimate_chars())
    results.append(test_truncate_history_no_overflow())
    results.append(test_truncate_history_basic())
    results.append(test_truncate_history_with_tool_calls())
    results.append(test_truncate_history_empty())
    results.append(test_config_values())
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
