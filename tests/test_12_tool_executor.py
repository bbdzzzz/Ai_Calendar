"""
测试12: Agent工具执行器 (本地业务逻辑)
运行: uv run python tests/test_12_tool_executor.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from datetime import datetime
from backend.core.database import SessionLocal, init_db
from backend.models.models import User, Event
from backend.agent.tool_executor import execute_tool
from backend.core.security import hash_password


def setup():
    init_db()
    db = SessionLocal()
    user = db.query(User).filter(User.username == "test_agent_tools_user").first()
    if not user:
        user = User(username="test_agent_tools_user", password_hash=hash_password("test"))
        db.add(user)
        db.commit()
        db.refresh(user)
    user_id = user.id

    db.query(Event).filter(Event.user_id == user_id).delete()
    db.commit()

    event = Event(
        user_id=user_id,
        title="已有会议",
        start_time=datetime(2026, 6, 15, 10, 0),
        end_time=datetime(2026, 6, 15, 11, 0),
        status="confirmed",
        source="manual",
    )
    db.add(event)
    db.commit()
    db.close()
    return user_id


def test_query_events(user_id: int):
    print("=== 测试query_events工具 ===")
    db = SessionLocal()
    result = execute_tool(db, user_id, "query_events", {
        "start_time": "2026-06-15T00:00:00",
        "end_time": "2026-06-15T23:59:59",
    })
    db.close()
    parsed = json.loads(result)
    assert parsed["status"] == "success"
    assert parsed["count"] >= 1
    print(f"[PASS] 查询到{parsed['count']}个日程")
    return True


def test_create_event_no_conflict(user_id: int):
    print("=== 测试create_event无冲突 ===")
    db = SessionLocal()
    result = execute_tool(db, user_id, "create_event", {
        "title": "新会议",
        "start_time": "2026-06-15T14:00:00",
        "end_time": "2026-06-15T15:00:00",
        "category": "meeting",
    })
    db.close()
    parsed = json.loads(result)
    assert parsed["status"] == "success", f"创建失败: {parsed}"
    assert parsed["event"]["title"] == "新会议"
    print(f"[PASS] 创建成功: id={parsed['event']['id']}, title={parsed['event']['title']}")
    return parsed["event"]["id"]


def test_create_event_conflict(user_id: int):
    print("=== 测试create_event有冲突 ===")
    db = SessionLocal()
    result = execute_tool(db, user_id, "create_event", {
        "title": "冲突会议",
        "start_time": "2026-06-15T10:30:00",
        "end_time": "2026-06-15T11:30:00",
    })
    db.close()
    parsed = json.loads(result)
    assert parsed["status"] == "conflict", f"应检测到冲突: {parsed}"
    print(f"[PASS] 检测到冲突: {parsed['message']}")
    return True


def test_update_event(user_id: int, event_id: int):
    print("=== 测试update_event工具 ===")
    db = SessionLocal()
    result = execute_tool(db, user_id, "update_event", {
        "event_id": event_id,
        "title": "新会议(已更新)",
    })
    db.close()
    parsed = json.loads(result)
    assert parsed["status"] == "success", f"更新失败: {parsed}"
    assert parsed["event"]["title"] == "新会议(已更新)"
    print(f"[PASS] 更新成功: title={parsed['event']['title']}")
    return True


def test_delete_event(user_id: int, event_id: int):
    print("=== 测试delete_event工具 ===")
    db = SessionLocal()
    result = execute_tool(db, user_id, "delete_event", {
        "event_id": event_id,
    })
    db.close()
    parsed = json.loads(result)
    assert parsed["status"] == "success", f"删除失败: {parsed}"
    print(f"[PASS] 删除成功: {parsed['message']}")
    return True


def test_unknown_tool(user_id: int):
    print("=== 测试未知工具 ===")
    db = SessionLocal()
    result = execute_tool(db, user_id, "unknown_tool", {})
    db.close()
    parsed = json.loads(result)
    assert parsed["status"] == "error"
    print(f"[PASS] 未知工具返回错误: {parsed['message']}")
    return True


def cleanup(user_id: int):
    db = SessionLocal()
    db.query(Event).filter(Event.user_id == user_id).delete()
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    db.close()


if __name__ == "__main__":
    user_id = setup()
    results = []
    results.append(test_query_events(user_id))
    new_event_id = test_create_event_no_conflict(user_id)
    results.append(bool(new_event_id))
    results.append(test_create_event_conflict(user_id))
    if new_event_id:
        results.append(test_update_event(user_id, new_event_id))
        results.append(test_delete_event(user_id, new_event_id))
    results.append(test_unknown_tool(user_id))
    cleanup(user_id)
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
