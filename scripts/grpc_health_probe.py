from __future__ import annotations

import os
import sys

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc


def _bypass_proxy_for_local_target(target: str) -> None:
    host = target.rsplit(":", 1)[0]
    if host in {"127.0.0.1", "localhost"}:
        for key in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
            os.environ.pop(key, None)


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1:8032"
    service = sys.argv[2] if len(sys.argv) > 2 else "asr.v1.AsrService"
    _bypass_proxy_for_local_target(target)
    with grpc.insecure_channel(target) as channel:
        stub = health_pb2_grpc.HealthStub(channel)
        response = stub.Check(health_pb2.HealthCheckRequest(service=service), timeout=5)
    if response.status != health_pb2.HealthCheckResponse.SERVING:
        raise SystemExit(f"health status is {response.status}, expected SERVING")
    print("SERVING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
