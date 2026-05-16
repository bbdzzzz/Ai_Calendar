"""
测试9: 周报生成逻辑
运行: uv run python tests/test_09_report.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, datetime
from backend.core.database import SessionLocal, init_db
from backend.models.models import User, Event, Report
from backend.scheduler.report_cron import _generate_weekly_report
from backend.core.security import hash_password


def setup():
    init_db()
    db = SessionLocal()
    user = db.query(User).filter(User.username == "test_report_user").first()
    if not user:
        user = User(username="test_report_user", password_hash=hash_password("test"))
        db.add(user)
        db.commit()
        db.refresh(user)

    user_id = user.id

    db.query(Event).filter(Event.user_id == user_id).delete()
    db.query(Report).filter(Report.user_id == user_id).delete()
    db.commit()

    events_data = [
        {"title": "周会", "start_time": datetime(2026, 5, 11, 9, 0), "end_time": datetime(2026, 5, 11, 10, 0), "category": "work"},
        {"title": "跑步", "start_time": datetime(2026, 5, 12, 7, 0), "end_time": datetime(2026, 5, 12, 8, 0), "category": "health"},
        {"title": "客户拜访", "start_time": datetime(2026, 5, 13, 14, 0), "end_time": datetime(2026, 5, 13, 16, 0), "category": "work"},
    ]
    for ed in events_data:
        db.add(Event(user_id=user_id, status="confirmed", **ed))
    db.commit()
    db.close()
    return user_id


def test_weekly_report(user_id: int):
    print("=== 测试周报生成 ===")
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    result = _generate_weekly_report(db, user, date(2026, 5, 11), date(2026, 5, 18))

    assert result["summary"]
    assert result["statistics"]["total_events"] == 3
    assert "work" in result["statistics"]["category_breakdown"]
    print(f"[PASS] 周报生成: {result['statistics']['total_events']}项行程")
    print(f"  统计: {result['statistics']['category_breakdown']}")
    print(f"  摘要:\n{result['summary']}")
    db.close()
    return True


def test_save_report(user_id: int):
    print("=== 测试保存报告到数据库 ===")
    db = SessionLocal()
    db.query(Report).filter(Report.user_id == user_id).delete()
    db.commit()

    report = Report(
        user_id=user_id,
        report_type="weekly",
        start_date=date(2026, 5, 11),
        end_date=date(2026, 5, 18),
        summary="测试周报",
        statistics={"total_events": 3},
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    fetched = db.query(Report).filter(Report.id == report.id).first()
    assert fetched is not None
    print(f"[PASS] 报告保存: id={fetched.id}")
    db.close()
    return True


def cleanup(user_id: int):
    db = SessionLocal()
    db.query(Event).filter(Event.user_id == user_id).delete()
    db.query(Report).filter(Report.user_id == user_id).delete()
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    db.close()


if __name__ == "__main__":
    user_id = setup()
    results = []
    results.append(test_weekly_report(user_id))
    results.append(test_save_report(user_id))
    cleanup(user_id)
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
