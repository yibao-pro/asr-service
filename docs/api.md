# ASR Service API

Base URL:

```text
/
```

公共约定：

- 健康检查使用 `GET /healthz`
- 识别接口使用 `POST /stt`
- `/stt` 使用 `multipart/form-data`

## Health Check

`GET /healthz`

成功响应示例：

```json
{
  "status": "ok",
  "device": "cuda",
  "compute_type": "float16",
  "asr_model_root": "/app/model",
  "asr_model_size": "Belle-faster-whisper-large-v3-zh-punct",
  "asr_model_path": "/app/model/Belle-faster-whisper-large-v3-zh-punct"
}
```

字段说明：

- `status`: 固定为 `ok`
- `device`: 当前加载模型使用的设备
- `compute_type`: 当前推理精度
- `asr_model_root`: 模型根目录
- `asr_model_size`: 模型目录名
- `asr_model_path`: 实际模型路径

## Speech To Text

`POST /stt`

请求格式：

```text
Content-Type: multipart/form-data
```

表单字段：

- `file`: 必填，音频文件
- `lang`: 选填，默认 `zh`

请求示例：

```bash
curl --noproxy '*' -X POST \
  -F 'file=@./test/assets/zero_shot_prompt.wav' \
  -F 'lang=zh' \
  http://127.0.0.1:8032/stt
```

成功响应示例：

```json
{
  "text": "这是一条测试语音。"
}
```

失败响应示例：

```json
{
  "detail": "ASR failed: <error message>"
}
```

典型失败原因：

- 模型路径不存在
- 音频格式不可解析
- GPU 模式下 CUDA 运行环境不可用
