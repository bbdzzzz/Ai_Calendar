"""
测试10: 健康检查与API文档
运行: uv run python tests/test_10_health.py
前提: 服务已启动
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx

BASE_URL = "http://localhost:8000"


def test_health():
    print("=== 测试健康检查 ===")
    r = httpx.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    print("[PASS] 健康检查正常")
    return True


def test_docs():
    print("=== 测试API文档 ===")
    r = httpx.get(f"{BASE_URL}/docs")
    assert r.status_code == 200
    print("[PASS] Swagger文档可访问")
    return True


def test_openapi():
    print("=== 测试OpenAPI规范 ===")
    r = httpx.get(f"{BASE_URL}/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    paths = list(schema.get("paths", {}).keys())
    print(f"[PASS] OpenAPI规范: {len(paths)}个端点")
    for p in paths:
        print(f"  - {p}")
    return True


if __name__ == "__main__":
    results = []
    results.append(test_health())
    results.append(test_docs())
    results.append(test_openapi())
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
