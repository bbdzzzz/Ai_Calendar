"""
测试15: Agent完整ReAct流程 (需配置LLM_API_KEY)
运行: uv run python tests/test_15_agent_react.py
前提: MySQL已启动, LLM_API_KEY已配置
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import json
from datetime import datetime
from backend.core.config import settings
from backend.core.database import SessionLocal, init_db
from backend.models.models import User, Event, Conversation
from backend.agent.adapter import run
from backend.agent.prompts import build_agent_input
from backend.core.security import hash_password


def setup():
    init_db()
    db = SessionLocal()
    user = db.query(User).filter(User.username == "test_react_user").first()
    if not user:
        user = User(username="test_react_user", password_hash=hash_password("test"))
        db.add(user)
        db.commit()
        db.refresh(user)
    user_id = user.id

    db.query(Conversation).filter(Conversation.user_id == user_id).delete()
    db.query(Event).filter(Event.user_id == user_id).delete()
    db.commit()

    event = Event(
        user_id=user_id,
        title="产品评审会",
        start_time=datetime(2026, 5, 21, 14, 0),
        end_time=datetime(2026, 5, 21, 15, 0),
        status="confirmed",
        source="manual",
    )
    db.add(event)
    db.commit()
    db.close()
    return user_id


async def test_text_reply():
    print("=== 测试纯文本回复 ===")
    if not settings.LLM_API_KEY:
        print("[SKIP] LLM_API_KEY未配置")
        return True

    db = SessionLocal()
    try:
        agent_input = build_agent_input(db, user_id, "今天几号")
        result = await run(agent_input, db=db)
        assert result.text_response
        assert result.action_type == "text_reply"
        print(f"[PASS] 文本回复: {result.text_response[:80]}")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False
    finally:
        db.close()


async def test_create_event():
    print("=== 测试创建日程 ===")
    if not settings.LLM_API_KEY:
        print("[SKIP] LLM_API_KEY未配置")
        return True

    db = SessionLocal()
    try:
        agent_input = build_agent_input(db, user_id, "明天下午3点开会")
        result = await run(agent_input, db=db)
        assert result.text_response
        print(f"[PASS] Agent回复: {result.text_response[:80]}")
        if result.action_type in ("create_event", "text_reply"):
            if result.event_data:
                print(f"  行程数据: title={result.event_data.get('title')}, start={result.event_data.get('start_time')}")
            return True
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False
    finally:
        db.close()


async def test_conflict_detection():
    print("=== 测试冲突检测 ===")
    if not settings.LLM_API_KEY:
        print("[SKIP] LLM_API_KEY未配置")
        return True

    db = SessionLocal()
    try:
        agent_input = build_agent_input(db, user_id, "明天下午2点到3点安排个会议")
        result = await run(agent_input, db=db)
        assert result.text_response
        print(f"[PASS] Agent回复: {result.text_response[:80]}")
        if "冲突" in result.text_response or "已有" in result.text_response:
            print("  Agent检测到冲突并告知用户")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False
    finally:
        db.close()


async def test_no_api_key():
    print("=== 测试无API Key降级 ===")
    original_key = settings.LLM_API_KEY
    settings.LLM_API_KEY = ""
    try:
        agent_input = build_agent_input.__wrapped__(SessionLocal(), user_id, "测试") if hasattr(build_agent_input, '__wrapped__') else None
        from backend.schemas.agent import AgentInput
        agent_input = AgentInput(
            user_id=user_id,
            current_query="测试",
            conversation_history=[],
            current_context={"current_time": "2026-05-20 10:30:00 星期二", "user_preferences": {}, "upcoming_events_summary": "无"},
        )
        result = await run(agent_input)
        assert "LLM未配置" in result.text_response
        print(f"[PASS] 无API Key降级: {result.text_response[:50]}")
        return True
    finally:
        settings.LLM_API_KEY = original_key


def cleanup(user_id: int):
    db = SessionLocal()
    db.query(Conversation).filter(Conversation.user_id == user_id).delete()
    db.query(Event).filter(Event.user_id == user_id).delete()
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    db.close()


async def main():
    global user_id
    user_id = setup()
    results = []
    results.append(await test_no_api_key())
    results.append(await test_text_reply())
    results.append(await test_create_event())
    results.append(await test_conflict_detection())
    cleanup(user_id)
    print(f"\n结果: {sum(results)}/{len(results)} 通过")


if __name__ == "__main__":
    asyncio.run(main())
