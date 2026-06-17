# ASR Service

一个独立部署的语音识别服务，基于 `FastAPI + faster-whisper` 实现。

## 目录结构

```text
asr-service/
├── api/
├── docs/
├── model/
├── scripts/
├── src/
├── test/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── main.py
├── requirements.txt
└── README.md
```

## 核心能力

- `GET /healthz` 健康检查
- `POST /stt` 音频转文本
- 同时支持 CPU 和 GPU 推理
- 使用本地模型目录运行，不依赖 `./yibao-pro`

## 环境变量

服务监听地址：

```bash
ASR_SERVICE_HOST
ASR_SERVICE_PORT
```

模型配置：

```bash
ASR_MODEL_PATH
ASR_MODEL_SIZE
```

推理配置：

```bash
ASR_DEVICE
ASR_COMPUTE_TYPE
```

推荐值：

- CPU:
  - `ASR_DEVICE=cpu`
  - `ASR_COMPUTE_TYPE=int8`
- GPU:
  - `ASR_DEVICE=cuda`
  - `ASR_COMPUTE_TYPE=float16`

## 本地启动

安装依赖：

```bash
pip install -r requirements.txt
```

CPU 启动：

```bash
ASR_DEVICE=cpu ASR_COMPUTE_TYPE=int8 ./scripts/start_asr_service.sh
```

GPU 启动：

```bash
ASR_DEVICE=cuda ASR_COMPUTE_TYPE=float16 ./scripts/start_asr_service.sh
```

默认端口：

```text
8032
```

当前仓库和 GitHub Actions 默认使用 `8032` 作为正式服务端口、`18032` 作为 candidate 检查端口。
这样可以避开目标机器上已有的 `8002` 宿主机监听进程，减少部署冲突。

## 测试

引擎测试：

```bash
ASR_DEVICE=cpu ASR_COMPUTE_TYPE=int8 pytest -q test/test_asr_engine.py
```

接口测试：

```bash
python test/test_api.py
```

测试资源位于：

- `test/assets/zero_shot_prompt.wav`

## Docker

镜像默认不内置模型权重目录，运行时通过 volume 挂载 `./model`：

```bash
cp .env.example .env
docker compose up -d --build
```

`docker-compose.yml` 默认会挂载：

```text
./model:/app/model:ro
```

如果你在容器里跑 GPU 推理，还需要宿主机具备：

- NVIDIA 驱动
- NVIDIA Container Toolkit

并在运行时为容器提供 GPU 访问能力。

镜像地址：

```text
ghcr.io/yibao-pro/asr-service:latest
```

## GitHub Actions

工作流文件：

- [docker-image.yml](./.github/workflows/docker-image.yml)

当前流程：

- `docker-image`：构建并推送 `ghcr.io/yibao-pro/asr-service:latest`
- `deploy`：SSH 到目标服务器，先启动 candidate 容器做健康检查，再替换正式容器

部署所需 GitHub Secrets：

- `SERVER_HOST`
- `SERVER_USER`
- `SERVER_SSH_KEY`

服务器部署约定：

- 部署目录：`/data/yibao-agent-platform/asr-service`
- 环境文件：`/data/yibao-agent-platform/asr-service/.env`
- 模型目录：`/data/yibao-agent-platform/asr-service/model`
- 正式容器名：`yibao-asr-service`
- 候选容器名：`yibao-asr-service-candidate`
- candidate 端口：`18032`
- 生产端口：`8032`

## 新机器部署

### 1. 准备模型目录

确保目标机器存在模型目录，例如：

```text
/data/yibao-agent-platform/asr-service/model/Belle-faster-whisper-large-v3-zh-punct
```

### 2. 准备 `.env`

```bash
cp .env.example .env
```

CPU 示例：

```bash
ASR_SERVICE_HOST=0.0.0.0
ASR_SERVICE_PORT=8032
ASR_MODEL_PATH=/app/model/Belle-faster-whisper-large-v3-zh-punct
ASR_MODEL_SIZE=Belle-faster-whisper-large-v3-zh-punct
ASR_DEVICE=cpu
ASR_COMPUTE_TYPE=int8
```

GPU 示例：

```bash
ASR_SERVICE_HOST=0.0.0.0
ASR_SERVICE_PORT=8032
ASR_MODEL_PATH=/app/model/Belle-faster-whisper-large-v3-zh-punct
ASR_MODEL_SIZE=Belle-faster-whisper-large-v3-zh-punct
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16
```

### 3. 启动容器

CPU：

```bash
docker run -d \
  --name yibao-asr-service \
  --restart unless-stopped \
  --env-file /data/yibao-agent-platform/asr-service/.env \
  -v /data/yibao-agent-platform/asr-service/model:/app/model:ro \
  -p 8032:8032 \
  asr-service:latest
```

GPU：

```bash
docker run -d \
  --name yibao-asr-service \
  --restart unless-stopped \
  --gpus all \
  --env-file /data/yibao-agent-platform/asr-service/.env \
  -v /data/yibao-agent-platform/asr-service/model:/app/model:ro \
  -p 8032:8032 \
  asr-service:latest
```

### 4. 健康检查

```bash
curl --noproxy '*' http://127.0.0.1:8032/healthz
```

### 5. 请求识别接口

```bash
curl --noproxy '*' -X POST \
  -F 'file=@./test/assets/zero_shot_prompt.wav' \
  -F 'lang=zh' \
  http://127.0.0.1:8032/stt
```

## 接口

- `GET /healthz`
- `POST /stt`

详细接口文档见：

- [docs/api.md](./docs/api.md)

## 说明

- 当前服务目录不依赖 `./yibao-pro` 运行时代码
- 模型路径默认基于当前仓库目录解析
- 当前仓库已经同步使用 `test/assets` 作为测试音频目录
