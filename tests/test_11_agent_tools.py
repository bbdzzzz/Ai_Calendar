"""
测试11: Agent工具定义验证
运行: uv run python tests/test_11_agent_tools.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.agent.tools import TOOLS


def test_tools_structure():
    print("=== 测试工具定义结构 ===")
    tool_names = [t["function"]["name"] for t in TOOLS]
    expected = ["query_events", "create_event", "update_event", "delete_event"]
    assert tool_names == expected, f"工具名不匹配: {tool_names}"
    print(f"[PASS] 4个工具定义完整: {tool_names}")

    for tool in TOOLS:
        func = tool["function"]
        assert func.get("name")
        assert func.get("description")
        assert func.get("parameters", {}).get("type") == "object"
        assert func["parameters"].get("properties")
        print(f"  - {func['name']}: {len(func['parameters']['properties'])}个参数, required={func['parameters'].get('required', [])}")
    return True


def test_tool_schema_valid():
    print("=== 测试工具JSON Schema有效性 ===")
    import json
    for tool in TOOLS:
        schema_str = json.dumps(tool, ensure_ascii=False)
        parsed = json.loads(schema_str)
        assert parsed["function"]["name"]
    print("[PASS] 所有工具Schema可序列化/反序列化")
    return True


if __name__ == "__main__":
    results = []
    results.append(test_tools_structure())
    results.append(test_tool_schema_valid())
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
