"""
测试6: TTS服务 (edge-tts)
运行: uv run python tests/test_06_tts.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
from backend.services.tts_service import stream_tts


async def test_tts_basic():
    print("=== 测试TTS基本功能 ===")
    text = "你好，这是一个语音日历系统测试。"
    chunks = []
    async for chunk in stream_tts(text):
        chunks.append(chunk)

    total_bytes = sum(len(c) for c in chunks)
    if total_bytes > 0:
        print(f"[PASS] TTS生成音频: {len(chunks)}个分块, 共{total_bytes}字节")
        return True
    else:
        print("[FAIL] TTS未生成音频数据")
        return False


async def test_tts_save_file():
    print("=== 测试TTS保存文件 ===")
    text = "明天下午三点开会。"
    output_path = os.path.join(os.path.dirname(__file__), "test_tts_output.mp3")
    with open(output_path, "wb") as f:
        async for chunk in stream_tts(text):
            f.write(chunk)

    file_size = os.path.getsize(output_path)
    if file_size > 0:
        print(f"[PASS] TTS保存文件: {output_path}, {file_size}字节")
        os.remove(output_path)
        return True
    else:
        print("[FAIL] TTS文件为空")
        os.remove(output_path)
        return False


async def main():
    results = []
    results.append(await test_tts_basic())
    results.append(await test_tts_save_file())
    print(f"\n结果: {sum(results)}/{len(results)} 通过")


if __name__ == "__main__":
    asyncio.run(main())
