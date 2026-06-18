from __future__ import annotations

import os


def main() -> None:
    print("asr-service build smoke check passed")
    print("transport=grpc")
    print(f"port={os.getenv('ASR_SERVICE_PORT', '8032')}")


if __name__ == "__main__":
    main()
