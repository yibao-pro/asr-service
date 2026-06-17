# asr_engine.py
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import torch
from faster_whisper import WhisperModel

try:
    from opencc import OpenCC
except ImportError:
    OpenCC = None


@dataclass(frozen=True)
class ASRConfig:
    asr_model_root: str
    asr_model_size: str
    asr_model_path: str
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type: str = "float16" if torch.cuda.is_available() else "int8"
    to_simplified: bool = True


class ASREngine:
    """纯 ASR 引擎：懒加载 faster-whisper + 文件转写。"""

    def __init__(self, cfg: ASRConfig):
        self.cfg = cfg
        self.device = cfg.device
        self._model = None
        self._opencc = OpenCC("t2s") if (cfg.to_simplified and OpenCC) else None

    def load(self) -> None:
        if self._model is not None:
            return
        self._model = WhisperModel(
            self.cfg.asr_model_path,
            device=self.device,
            compute_type=self.cfg.compute_type,
            local_files_only=Path(self.cfg.asr_model_path).exists(),
        )

    def _convert_to_simplified(self, text: str) -> str:
        if not text:
            return text
        if self._opencc:
            try:
                return self._opencc.convert(text)
            except Exception:
                return text
        return text

    def transcribe_file(self, audio_path: str, lang: Optional[str] = "zh") -> str:
        if self._model is None:
            self.load()
        segments, _info = self._model.transcribe(
            audio_path,
            language=lang,
            beam_size=5,
            vad_filter=True,
        )
        segment_list = list(segments)
        text = "".join((segment.text or "") for segment in segment_list).strip()
        return self._convert_to_simplified(text)

    def transcribe_bytes(self, audio_bytes: bytes, filename: str = "audio.wav", lang: Optional[str] = "zh") -> str:
        import tempfile

        suffix = Path(filename).suffix or ".wav"
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            return self.transcribe_file(tmp_path, lang=lang)
        finally:
            if tmp_path:
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except Exception:
                    pass
