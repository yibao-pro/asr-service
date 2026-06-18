from pathlib import Path
import os

import grpc

from src.generated import asr_pb2, asr_pb2_grpc

ASR_TARGET = "127.0.0.1:8032"
audio_path = Path(__file__).resolve().parent / "assets" / "zero_shot_prompt.wav"

if not audio_path.exists():
    raise FileNotFoundError(f"文件不存在: {audio_path.resolve()}")

for key in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(key, None)

with open(audio_path, "rb") as audio_file:
    with grpc.insecure_channel(ASR_TARGET) as channel:
        stub = asr_pb2_grpc.AsrServiceStub(channel)
        response = stub.Transcribe(
            asr_pb2.TranscribeRequest(
                audio_bytes=audio_file.read(),
                filename=audio_path.name,
                lang="zh",
            )
        )

print("========== ASR 输出 ==========")
print(response.text)
