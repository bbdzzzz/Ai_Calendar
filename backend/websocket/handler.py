import json
import logging
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from backend.agent import adapter, prompts
from backend.core.database import SessionLocal
from backend.models.models import Conversation, Event
from backend.schemas.agent import AgentAction
from backend.services import asr_service, event_engine, tts_service

logger = logging.getLogger(__name__)


class WSHandler:
    def __init__(self, websocket: WebSocket, user_id: int):
        self.ws = websocket
        self.user_id = user_id
        self.asr_stream: asr_service.ASRStream | None = None

    async def run(self):
        await self.ws.accept()
        logger.info("WebSocket连接建立: user_id=%s", self.user_id)
        try:
            while True:
                msg = await self.ws.receive()
                if "text" in msg:
                    await self._handle_text(json.loads(msg["text"]))
                elif "bytes" in msg:
                    await self._handle_binary(msg["bytes"])
        except WebSocketDisconnect:
            logger.info("WebSocket断开: user_id=%s", self.user_id)
        except Exception as e:
            logger.error("WebSocket异常: %s", e)

    async def _handle_text(self, data: dict):
        msg_type = data.get("type")
        if msg_type == "audio_start":
            self.asr_stream = asr_service.create_stream()
            logger.info("开始录音: user_id=%s", self.user_id)
        elif msg_type == "audio_end":
            await self._on_audio_end()
        elif msg_type == "event_confirm":
            await self._on_event_confirm(data.get("payload", {}))
        elif msg_type == "text_message":
            await self._on_text_message(data.get("payload", {}))
        else:
            logger.warning("未知信令类型: %s", msg_type)

    async def _handle_binary(self, audio_bytes: bytes):
        if self.asr_stream:
            self.asr_stream.feed(audio_bytes)
            partial = self.asr_stream.get_partial()
            if partial:
                await self.ws.send_json({"type": "asr_partial", "payload": {"text": partial}})

    async def _on_audio_end(self):
        if not self.asr_stream:
            return
        final_text = self.asr_stream.finalize()
        self.asr_stream = None
        await self.ws.send_json({"type": "asr_final", "payload": {"text": final_text}})
        logger.info("ASR最终结果: user_id=%s, text=%s", self.user_id, final_text)

        if not final_text.strip():
            return

        db = SessionLocal()
        try:
            db.add(Conversation(user_id=self.user_id, role="user", content=final_text))
            db.commit()

            agent_input = prompts.build_agent_input(db, self.user_id, final_text)
            agent_output = await adapter.run(agent_input, db=db)

            self._save_conversation_history(db, agent_input, agent_output)

            if agent_output.action_type in ("create_event", "update_event") and agent_output.event_data:
                await self._send_event_upsert(agent_output.event_data)

            if agent_output.text_response:
                await self.ws.send_json({"type": "agent_text_delta", "payload": {"delta": agent_output.text_response}})
                async for audio_chunk in tts_service.stream_tts(agent_output.text_response):
                    await self.ws.send_bytes(audio_chunk)
                await self.ws.send_json({"type": "agent_audio_done"})
        finally:
            db.close()

    def _save_conversation_history(self, db: Session, agent_input, agent_output: AgentAction):
        for msg in agent_output.new_messages:
            role = msg.get("role")
            content = msg.get("content", "")
            tool_calls = None

            if role == "assistant" and msg.get("tool_calls"):
                tool_calls = msg["tool_calls"]
            elif role == "tool":
                tool_calls = {"tool_call_id": msg.get("tool_call_id", "")}

            db.add(Conversation(
                user_id=self.user_id,
                role=role,
                content=content,
                tool_calls=tool_calls,
            ))

        db.commit()

    async def _send_event_upsert(self, event_data: dict):
        payload = {
            **event_data,
            "temp_id": str(event_data.get("id", "pending")),
            "status": event_data.get("status", "tentative"),
        }
        await self.ws.send_json({"type": "event_upsert", "payload": payload})

    async def _on_event_confirm(self, payload: dict):
        temp_id = payload.get("temp_id")
        confirmed = payload.get("confirmed", False)
        db = SessionLocal()
        try:
            event = db.query(Event).filter(Event.id == int(temp_id), Event.user_id == self.user_id).first()
            if event:
                event.status = "confirmed" if confirmed else "cancelled"
                db.commit()
        finally:
            db.close()
        logger.info("行程确认: temp_id=%s, confirmed=%s", temp_id, confirmed)

    async def _on_text_message(self, payload: dict):
        text = payload.get("text", "").strip()
        if not text:
            return

        db = SessionLocal()
        try:
            db.add(Conversation(user_id=self.user_id, role="user", content=text))
            db.commit()

            agent_input = prompts.build_agent_input(db, self.user_id, text)
            agent_output = await adapter.run(agent_input, db=db)

            self._save_conversation_history(db, agent_input, agent_output)

            if agent_output.action_type in ("create_event", "update_event") and agent_output.event_data:
                await self._send_event_upsert(agent_output.event_data)

            if agent_output.text_response:
                await self.ws.send_json({"type": "agent_text_delta", "payload": {"delta": agent_output.text_response}})
                async for audio_chunk in tts_service.stream_tts(agent_output.text_response):
                    await self.ws.send_bytes(audio_chunk)
                await self.ws.send_json({"type": "agent_audio_done"})
        finally:
            db.close()
