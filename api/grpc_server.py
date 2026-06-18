from __future__ import annotations

import os
from concurrent import futures
from pathlib import Path

import grpc
import torch
from grpc import StatusCode
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from src.asr_engine import ASRConfig, ASREngine
from src.generated import asr_pb2, asr_pb2_grpc

SERVICE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = SERVICE_ROOT / "model" / "Belle-faster-whisper-large-v3-zh-punct"
SERVICE_NAME = "asr.v1.AsrService"


def build_engine() -> ASREngine:
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


engine = build_engine()
engine.load()


class AsrServiceServicer(asr_pb2_grpc.AsrServiceServicer):
    def Healthz(self, request: asr_pb2.HealthzRequest, context: grpc.ServicerContext) -> asr_pb2.HealthzResponse:
        return asr_pb2.HealthzResponse(
            status="ok",
            device=engine.cfg.device,
            compute_type=engine.cfg.compute_type,
            asr_model_root=engine.cfg.asr_model_root,
            asr_model_size=engine.cfg.asr_model_size,
            asr_model_path=engine.cfg.asr_model_path,
        )

    def Transcribe(
        self, request: asr_pb2.TranscribeRequest, context: grpc.ServicerContext
    ) -> asr_pb2.TranscribeResponse:
        if not request.audio_bytes:
            context.abort(StatusCode.INVALID_ARGUMENT, "audio_bytes is required")
        filename = request.filename or "audio.wav"
        lang = request.lang or "zh"
        try:
            text = engine.transcribe_bytes(request.audio_bytes, filename=filename, lang=lang)
        except Exception as exc:  # pragma: no cover
            context.abort(StatusCode.INTERNAL, f"ASR failed: {exc}")
        return asr_pb2.TranscribeResponse(text=text)


def serve() -> None:
    host = os.getenv("ASR_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("ASR_SERVICE_PORT", "8032"))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    asr_pb2_grpc.add_AsrServiceServicer_to_server(AsrServiceServicer(), server)

    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set(SERVICE_NAME, health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("grpc.health.v1.Health", health_pb2.HealthCheckResponse.SERVING)

    server.add_insecure_port(f"{host}:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
