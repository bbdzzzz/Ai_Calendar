"""
测试4: 行程CRUD API
运行: uv run python tests/test_04_events_api.py
前提: 服务已启动, 且test_03_auth_api.py已通过 (有可用token)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx

BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {"username": "test_auth_user", "password": "testpass123"}


def get_token() -> str | None:
    r = httpx.post(f"{BASE_URL}/auth/login", json=TEST_USER)
    if r.status_code == 200:
        return r.json()["access_token"]
    httpx.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    r = httpx.post(f"{BASE_URL}/auth/login", json=TEST_USER)
    return r.json()["access_token"] if r.status_code == 200 else None


def headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_event(token: str):
    print("=== 测试创建行程 ===")
    event_data = {
        "title": "项目会议",
        "description": "讨论Q3计划",
        "start_time": "2026-05-20T15:00:00",
        "end_time": "2026-05-20T16:00:00",
        "location": "3号会议室",
        "category": "work",
        "priority": "high",
        "status": "confirmed",
        "source": "manual",
    }
    r = httpx.post(f"{BASE_URL}/events", json=event_data, headers=headers(token))
    if r.status_code == 201:
        data = r.json()
        print(f"[PASS] 创建行程: id={data['id']}, title={data['title']}")
        return data["id"]
    else:
        print(f"[FAIL] 创建行程失败: {r.status_code} {r.text}")
        return None


def test_list_events(token: str):
    print("=== 测试获取行程列表 ===")
    r = httpx.get(f"{BASE_URL}/events", headers=headers(token))
    if r.status_code == 200:
        data = r.json()
        print(f"[PASS] 获取行程列表: 共{len(data)}条")
        return True
    else:
        print(f"[FAIL] 获取行程列表失败: {r.status_code} {r.text}")
        return False


def test_get_event(token: str, event_id: int):
    print("=== 测试获取单个行程 ===")
    r = httpx.get(f"{BASE_URL}/events/{event_id}", headers=headers(token))
    if r.status_code == 200:
        data = r.json()
        print(f"[PASS] 获取行程: title={data['title']}")
        return True
    else:
        print(f"[FAIL] 获取行程失败: {r.status_code} {r.text}")
        return False


def test_update_event(token: str, event_id: int):
    print("=== 测试更新行程 ===")
    r = httpx.put(f"{BASE_URL}/events/{event_id}", json={"title": "项目会议(已更新)"}, headers=headers(token))
    if r.status_code == 200:
        data = r.json()
        print(f"[PASS] 更新行程: title={data['title']}")
        return True
    else:
        print(f"[FAIL] 更新行程失败: {r.status_code} {r.text}")
        return False


def test_delete_event(token: str, event_id: int):
    print("=== 测试删除行程 ===")
    r = httpx.delete(f"{BASE_URL}/events/{event_id}", headers=headers(token))
    if r.status_code == 204:
        print("[PASS] 删除行程成功")
        return True
    else:
        print(f"[FAIL] 删除行程失败: {r.status_code} {r.text}")
        return False


def test_filter_events(token: str):
    print("=== 测试行程筛选 ===")
    r = httpx.get(
        f"{BASE_URL}/events",
        params={"start": "2026-05-01T00:00:00", "end": "2026-05-31T23:59:59", "category": "work"},
        headers=headers(token),
    )
    if r.status_code == 200:
        print(f"[PASS] 筛选行程: {len(r.json())}条")
        return True
    else:
        print(f"[FAIL] 筛选行程失败: {r.status_code}")
        return False


if __name__ == "__main__":
    token = get_token()
    if not token:
        print("[FAIL] 无法获取token, 请先运行test_03")
        exit(1)

    results = []
    event_id = test_create_event(token)
    results.append(bool(event_id))
    results.append(test_list_events(token))
    if event_id:
        results.append(test_get_event(token, event_id))
        results.append(test_update_event(token, event_id))
        results.append(test_filter_events(token))
        results.append(test_delete_event(token, event_id))
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
