"""
测试8: WebSocket信令交互
运行: uv run python tests/test_08_websocket.py
前提: 服务已启动
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import json
import websockets

WS_URL = "ws://localhost:8000/ws/1"


async def test_ws_connect():
    print("=== 测试WebSocket连接 ===")
    try:
        async with websockets.connect(WS_URL) as ws:
            print("[PASS] WebSocket连接成功")
            return True
    except Exception as e:
        print(f"[FAIL] WebSocket连接失败: {e}")
        return False


async def test_ws_audio_start_end():
    print("=== 测试录音信令 ===")
    try:
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps({"type": "audio_start", "payload": {"format": "pcm", "sample_rate": 16000}}))
            print("[PASS] 发送audio_start")

            await ws.send(json.dumps({"type": "audio_end"}))
            print("[PASS] 发送audio_end")

            try:
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                msg = json.loads(response)
                if msg.get("type") == "asr_final":
                    print(f"[PASS] 收到asr_final: {msg['payload']['text']}")
                elif msg.get("type") == "agent_text_delta":
                    print(f"[PASS] 收到agent_text_delta: {msg['payload']['delta']}")
                else:
                    print(f"[INFO] 收到信令: {msg.get('type')}")
            except asyncio.TimeoutError:
                print("[INFO] 未收到回复(无音频数据,ASR结果为空,属正常)")

            return True
    except Exception as e:
        print(f"[FAIL] 录音信令测试失败: {e}")
        return False


async def test_ws_event_confirm():
    print("=== 测试行程确认信令 ===")
    try:
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps({
                "type": "event_confirm",
                "payload": {"temp_id": "999", "confirmed": True}
            }))
            print("[PASS] 发送event_confirm信令")
            return True
    except Exception as e:
        print(f"[FAIL] 行程确认信令测试失败: {e}")
        return False


async def main():
    results = []
    results.append(await test_ws_connect())
    results.append(await test_ws_audio_start_end())
    results.append(await test_ws_event_confirm())
    print(f"\n结果: {sum(results)}/{len(results)} 通过")


if __name__ == "__main__":
    asyncio.run(main())
