"""
一键运行所有测试
运行: uv run python tests/run_all_tests.py
"""
import subprocess
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

TESTS = [
    ("01_数据库", "tests/test_01_database.py", False),
    ("02_安全模块", "tests/test_02_security.py", False),
    ("03_认证API", "tests/test_03_auth_api.py", True),
    ("04_行程API", "tests/test_04_events_api.py", True),
    ("05_冲突检测", "tests/test_05_event_engine.py", False),
    ("06_TTS服务", "tests/test_06_tts.py", False),
    ("07_Agent桩", "tests/test_07_agent.py", False),
    ("08_WebSocket", "tests/test_08_websocket.py", True),
    ("09_周报生成", "tests/test_09_report.py", False),
    ("10_健康检查", "tests/test_10_health.py", True),
    ("11_Agent工具定义", "tests/test_11_agent_tools.py", False),
    ("12_工具执行器", "tests/test_12_tool_executor.py", False),
    ("13_AgentPrompt", "tests/test_13_agent_prompts.py", False),
    ("14_LLM客户端", "tests/test_14_agent_llm.py", False),
    ("15_AgentReAct", "tests/test_15_agent_react.py", False),
]


def main():
    print("=" * 60)
    print("AI语音日历系统 - 全量测试")
    print("=" * 60)

    need_server = [t for t in TESTS if t[2]]
    no_server = [t for t in TESTS if not t[2]]

    print("\n[阶段1] 无需服务器的测试")
    print("-" * 40)
    for name, script, _ in no_server:
        print(f"\n>>> 运行: {name}")
        result = subprocess.run([sys.executable, script], cwd=os.path.join(os.path.dirname(__file__), ".."))
        if result.returncode != 0:
            print(f"!!! {name} 执行出错")

    print("\n\n[阶段2] 需要服务器的测试")
    print("-" * 40)
    print("请确保服务已启动: uv run python main.py")
    input("按Enter继续...")

    for name, script, _ in need_server:
        print(f"\n>>> 运行: {name}")
        result = subprocess.run([sys.executable, script], cwd=os.path.join(os.path.dirname(__file__), ".."))
        if result.returncode != 0:
            print(f"!!! {name} 执行出错")

    print("\n" + "=" * 60)
    print("全部测试执行完毕")
    print("=" * 60)


if __name__ == "__main__":
    main()
