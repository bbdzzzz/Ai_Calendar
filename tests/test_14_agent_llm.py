"""
测试14: Agent LLM客户端
运行: uv run python tests/test_14_agent_llm.py
注意: 需要配置LLM_API_KEY才能测试真实调用
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.core.config import settings
from backend.agent.llm_client import get_llm_client


def test_llm_client_init():
    print("=== 测试LLM客户端初始化 ===")
    client = get_llm_client()
    assert client is not None
    print(f"[PASS] 客户端初始化成功: base_url={settings.LLM_BASE_URL}, model={settings.LLM_MODEL}")
    return True


def test_llm_config():
    print("=== 测试LLM配置项 ===")
    print(f"  LLM_API_KEY: {'已配置' if settings.LLM_API_KEY else '未配置'}")
    print(f"  LLM_BASE_URL: {settings.LLM_BASE_URL}")
    print(f"  LLM_MODEL: {settings.LLM_MODEL}")
    print(f"  LLM_MAX_TOOL_ROUNDS: {settings.LLM_MAX_TOOL_ROUNDS}")
    print(f"  LLM_TEMPERATURE: {settings.LLM_TEMPERATURE}")
    print(f"  LLM_MAX_TOKENS: {settings.LLM_MAX_TOKENS}")
    print("[PASS] 配置项读取正常")
    return True


async def test_llm_real_call():
    print("=== 测试LLM真实调用 ===")
    if not settings.LLM_API_KEY:
        print("[SKIP] LLM_API_KEY未配置, 跳过真实调用测试")
        print("  请在.env文件中设置: LLM_API_KEY=your-api-key")
        return True

    from backend.agent.llm_client import chat_completion
    messages = [
        {"role": "system", "content": "你是测试助手，只回复OK"},
        {"role": "user", "content": "你好"},
    ]
    try:
        response = await chat_completion(messages=messages)
        content = response.choices[0].message.content
        print(f"[PASS] LLM调用成功: {content[:50]}")
        return True
    except Exception as e:
        print(f"[FAIL] LLM调用失败: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    results = []
    results.append(test_llm_client_init())
    results.append(test_llm_config())
    results.append(asyncio.run(test_llm_real_call()))
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
