from __future__ import annotations

from api.app import app


def main() -> None:
    print("asr-service build smoke check passed")
    print(f"title={app.title}")


if __name__ == "__main__":
    main()
