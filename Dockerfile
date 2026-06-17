FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY src ./src
COPY scripts ./scripts
COPY main.py ./main.py

RUN chmod +x /app/scripts/docker_start.sh /app/scripts/start_asr_service.sh

EXPOSE 8002

CMD ["./scripts/docker_start.sh"]
