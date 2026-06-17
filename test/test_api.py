# test_api.py
from pathlib import Path

import requests

ASR_URL = "http://127.0.0.1:8002/stt"
audio_path = Path(__file__).resolve().parent / "assets" / "zero_shot_prompt.wav"

if not audio_path.exists():
    raise FileNotFoundError(f"文件不存在: {audio_path.resolve()}")

with open(audio_path, "rb") as audio_file:
    files = {"file": (audio_path.name, audio_file, "audio/wav")}
    data = {"lang": "zh"}
    resp = requests.post(ASR_URL, files=files, data=data)

if resp.status_code == 200:
    result = resp.json()
    print("========== ASR 输出 ==========")
    print(result.get("text", ""))
else:
    print(f"请求失败: {resp.status_code} {resp.text}")
