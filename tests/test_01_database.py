"""
测试1: 数据库连接与建表
运行: uv run python tests/test_01_database.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.core.database import engine, Base, SessionLocal
from backend.models.models import User, Event, Conversation, Report


def test_create_tables():
    print("=== 测试数据库建表 ===")
    try:
        Base.metadata.create_all(bind=engine)
        print("[PASS] 建表成功")
    except Exception as e:
        print(f"[FAIL] 建表失败: {e}")
        return False
    return True


def test_connection():
    print("=== 测试数据库连接 ===")
    try:
        db = SessionLocal()
        db.execute(User.__table__.select().limit(1))
        db.close()
        print("[PASS] 数据库连接正常")
        return True
    except Exception as e:
        print(f"[FAIL] 数据库连接失败: {e}")
        return False


def test_crud_user():
    print("=== 测试User CRUD ===")
    db = SessionLocal()
    try:
        db.query(User).filter(User.username == "test_db_user").delete()
        db.commit()

        user = User(username="test_db_user", password_hash="hash123")
        db.add(user)
        db.commit()
        db.refresh(user)
        assert user.id is not None
        print(f"[PASS] 创建用户: id={user.id}")

        fetched = db.query(User).filter(User.username == "test_db_user").first()
        assert fetched is not None
        print("[PASS] 查询用户")

        db.delete(fetched)
        db.commit()
        assert db.query(User).filter(User.username == "test_db_user").first() is None
        print("[PASS] 删除用户")
        return True
    except Exception as e:
        print(f"[FAIL] User CRUD失败: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    results = []
    results.append(test_create_tables())
    results.append(test_connection())
    results.append(test_crud_user())
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
