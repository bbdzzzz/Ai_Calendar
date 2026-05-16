"""
测试5: 行程冲突检测引擎
运行: uv run python tests/test_05_event_engine.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from backend.core.database import SessionLocal, init_db
from backend.models.models import User, Event
from backend.services.event_engine import check_conflict
from backend.core.security import hash_password


def setup_test_data():
    db = SessionLocal()
    user = db.query(User).filter(User.username == "test_conflict_user").first()
    if not user:
        user = User(username="test_conflict_user", password_hash=hash_password("test"))
        db.add(user)
        db.commit()
        db.refresh(user)

    user_id = user.id

    db.query(Event).filter(Event.user_id == user_id).delete()
    db.commit()

    event = Event(
        user_id=user_id,
        title="已有会议",
        start_time=datetime(2026, 6, 1, 10, 0),
        end_time=datetime(2026, 6, 1, 11, 0),
        status="confirmed",
    )
    db.add(event)
    db.commit()
    db.close()
    return user_id


def test_no_conflict(user_id: int):
    print("=== 测试无冲突场景 ===")
    db = SessionLocal()
    conflicts = check_conflict(
        db, user_id,
        datetime(2026, 6, 1, 11, 0),
        datetime(2026, 6, 1, 12, 0),
    )
    db.close()
    assert len(conflicts) == 0
    print("[PASS] 无冲突: 11:00-12:00 不与 10:00-11:00 冲突")
    return True


def test_overlap_conflict(user_id: int):
    print("=== 测试重叠冲突场景 ===")
    db = SessionLocal()
    conflicts = check_conflict(
        db, user_id,
        datetime(2026, 6, 1, 10, 30),
        datetime(2026, 6, 1, 11, 30),
    )
    db.close()
    assert len(conflicts) > 0
    print(f"[PASS] 检测到冲突: {conflicts[0].title}")
    return True


def test_contained_conflict(user_id: int):
    print("=== 测试包含冲突场景 ===")
    db = SessionLocal()
    conflicts = check_conflict(
        db, user_id,
        datetime(2026, 6, 1, 9, 30),
        datetime(2026, 6, 1, 11, 30),
    )
    db.close()
    assert len(conflicts) > 0
    print(f"[PASS] 检测到包含冲突: {conflicts[0].title}")
    return True


def test_exclude_self(user_id: int):
    print("=== 测试排除自身 ===")
    db = SessionLocal()
    event = db.query(Event).filter(Event.user_id == user_id).first()
    conflicts = check_conflict(
        db, user_id,
        datetime(2026, 6, 1, 10, 0),
        datetime(2026, 6, 1, 11, 0),
        exclude_id=event.id,
    )
    db.close()
    assert len(conflicts) == 0
    print("[PASS] 排除自身后无冲突")
    return True


def cleanup(user_id: int):
    db = SessionLocal()
    db.query(Event).filter(Event.user_id == user_id).delete()
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    db.close()


if __name__ == "__main__":
    init_db()
    user_id = setup_test_data()
    results = []
    results.append(test_no_conflict(user_id))
    results.append(test_overlap_conflict(user_id))
    results.append(test_contained_conflict(user_id))
    results.append(test_exclude_self(user_id))
    cleanup(user_id)
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
