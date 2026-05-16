"""
测试7: Agent适配器桩
运行: uv run python tests/test_07_agent.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
from backend.agent.adapter import run
from backend.schemas.agent import AgentInput


async def test_agent_text_reply():
    print("=== 测试Agent文本回复 ===")
    agent_input = AgentInput(
        user_id=1,
        current_query="明天下午3点开会",
        conversation_history=[],
        current_context={"time": "2026-05-15T10:00:00", "events": []},
    )
    output = await run(agent_input)
    assert output.action_type == "text_reply"
    assert output.text_response
    print(f"[PASS] Agent回复: {output.text_response}")
    return True


async def test_agent_with_history():
    print("=== 测试Agent带上下文 ===")
    agent_input = AgentInput(
        user_id=1,
        current_query="改到4点",
        conversation_history=[
            {"role": "user", "content": "明天下午3点开会"},
            {"role": "assistant", "content": "好的，已安排明天下午3点开会"},
        ],
        current_context={"time": "2026-05-15T10:00:00", "events": []},
    )
    output = await run(agent_input)
    assert output.text_response
    print(f"[PASS] Agent带上下文回复: {output.text_response}")
    return True


async def main():
    results = []
    results.append(await test_agent_text_reply())
    results.append(await test_agent_with_history())
    print(f"\n结果: {sum(results)}/{len(results)} 通过")


if __name__ == "__main__":
    asyncio.run(main())
