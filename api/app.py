# app.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from src.asr_engine import ASRConfig, ASREngine


SERVICE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = SERVICE_ROOT / "model" / "Belle-faster-whisper-large-v3-zh-punct"


def _safe_unlink(path: str | Path) -> None:
    try:
        Path(path).unlink(missing_ok=True)
    except Exception:
        pass


def _build_engine() -> ASREngine:
    model_path = Path(os.getenv("ASR_MODEL_PATH", str(DEFAULT_MODEL_PATH))).expanduser().resolve()
    model_root = str(model_path.parent)
    model_size = os.getenv("ASR_MODEL_SIZE", model_path.name)
    device = os.getenv("ASR_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
    compute_type = os.getenv("ASR_COMPUTE_TYPE", "float16" if device.startswith("cuda") else "int8")

    if not model_path.exists():
        raise RuntimeError(f"ASR model path does not exist: {model_path}")

    cfg = ASRConfig(
        asr_model_root=model_root,
        asr_model_size=model_size,
        asr_model_path=str(model_path),
        device=device,
        compute_type=compute_type,
        to_simplified=True,
    )
    return ASREngine(cfg)


engine = _build_engine()
engine.load()

app = FastAPI(title="ASR Service (faster-whisper)")


class STTOut(BaseModel):
    text: str


@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "device": engine.cfg.device,
        "compute_type": engine.cfg.compute_type,
        "asr_model_root": engine.cfg.asr_model_root,
        "asr_model_size": engine.cfg.asr_model_size,
        "asr_model_path": engine.cfg.asr_model_path,
    }


@app.post("/stt", response_model=STTOut)
async def stt(
    file: UploadFile = File(...),
    lang: Optional[str] = Form("zh"),
):
    suffix = Path(file.filename or "audio.webm").suffix or ".webm"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        engine.load()
        text = engine.transcribe_file(tmp_path, lang=lang)
        return STTOut(text=text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ASR failed: {exc}") from exc
    finally:
        if tmp_path:
            _safe_unlink(tmp_path)
