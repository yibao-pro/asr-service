from __future__ import annotations

import os
from pathlib import Path

from src.asr_engine import ASRConfig, ASREngine


def test_faster_whisper_model_transcribes_test_audio() -> None:
    service_root = Path(__file__).resolve().parents[1]
    model_path = Path(
        os.getenv(
            "ASR_MODEL_PATH",
            service_root / "model" / "Belle-faster-whisper-large-v3-zh-punct",
        )
    )
    audio_path = Path(__file__).resolve().parent / "assets" / "zero_shot_prompt.wav"

    engine = ASREngine(
        ASRConfig(
            asr_model_root=str(model_path.parent),
            asr_model_size=model_path.name,
            asr_model_path=str(model_path),
            device=os.getenv("ASR_DEVICE", "cpu"),
            compute_type=os.getenv("ASR_COMPUTE_TYPE", "int8"),
        )
    )

    text = engine.transcribe_file(str(audio_path), lang="zh")

    assert text.strip()
