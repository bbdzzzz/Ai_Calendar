"""
测试3: 认证API (注册/登录/获取用户信息)
运行: uv run python tests/test_03_auth_api.py
前提: 服务已启动 (uv run python main.py)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx

BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {"username": "test_auth_user", "password": "testpass123"}


def test_register():
    print("=== 测试注册 ===")
    r = httpx.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    if r.status_code == 201:
        data = r.json()
        print(f"[PASS] 注册成功: id={data['id']}, username={data['username']}")
        return True
    elif r.status_code == 400:
        print(f"[INFO] 用户已存在: {r.json()}")
        return True
    else:
        print(f"[FAIL] 注册失败: {r.status_code} {r.text}")
        return False


def test_login():
    print("=== 测试登录 ===")
    r = httpx.post(f"{BASE_URL}/auth/login", json=TEST_USER)
    if r.status_code == 200:
        data = r.json()
        token = data["access_token"]
        print(f"[PASS] 登录成功, token={token[:30]}...")
        return token
    else:
        print(f"[FAIL] 登录失败: {r.status_code} {r.text}")
        return None


def test_me(token: str):
    print("=== 测试获取当前用户 ===")
    r = httpx.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
    if r.status_code == 200:
        data = r.json()
        print(f"[PASS] 获取用户信息: username={data['username']}")
        return True
    else:
        print(f"[FAIL] 获取用户信息失败: {r.status_code} {r.text}")
        return False


def test_me_unauthorized():
    print("=== 测试未授权访问 ===")
    r = httpx.get(f"{BASE_URL}/auth/me")
    assert r.status_code in (401, 403)
    print("[PASS] 未授权访问被拒绝")
    return True


if __name__ == "__main__":
    results = []
    results.append(test_register())
    token = test_login()
    if token:
        results.append(bool(token))
        results.append(test_me(token))
    results.append(test_me_unauthorized())
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
