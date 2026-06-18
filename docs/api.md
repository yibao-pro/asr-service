# ASR Service gRPC API

服务名：

```text
asr.v1.AsrService
```

## Healthz

RPC：

```text
Healthz(HealthzRequest) returns (HealthzResponse)
```

成功响应字段：

- `status`
- `device`
- `compute_type`
- `asr_model_root`
- `asr_model_size`
- `asr_model_path`

## Transcribe

RPC：

```text
Transcribe(TranscribeRequest) returns (TranscribeResponse)
```

请求字段：

- `audio_bytes`: 必填，音频二进制内容
- `filename`: 选填，文件名，默认 `audio.wav`
- `lang`: 选填，默认 `zh`

请求示例：

```python
from pathlib import Path
import grpc
from src.generated import asr_pb2, asr_pb2_grpc

audio_path = Path("./test/assets/zero_shot_prompt.wav")

with audio_path.open("rb") as fh, grpc.insecure_channel("127.0.0.1:8032") as channel:
    stub = asr_pb2_grpc.AsrServiceStub(channel)
    response = stub.Transcribe(
        asr_pb2.TranscribeRequest(
            audio_bytes=fh.read(),
            filename=audio_path.name,
            lang="zh",
        )
    )
    print(response.text)
```

成功响应字段：

- `text`

失败时常见 gRPC code：

- `INVALID_ARGUMENT`: `audio_bytes` 为空
- `INTERNAL`: 转写失败

典型失败原因：

- 模型路径不存在
- 音频格式不可解析
- GPU 模式下 CUDA 运行环境不可用
