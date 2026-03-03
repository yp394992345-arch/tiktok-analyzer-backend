# TikTok 视频智能拆解助手 - 后端

使用 FastAPI 构建的 TikTok 视频分析后端服务。

## 功能特性

- 📥 **TikTok视频下载** - 使用 TikWM API 下载无水印视频
- 🎙️ **语音转写** - 使用 Google Cloud Speech-to-Text 转写音频
- 🔍 **画面分析** - 使用阿里云视觉智能进行 OCR 和图像分析
- 🤖 **AI话术分析** - 使用通义千问分析带货话术和营销策略

## 环境要求

- Python 3.9+
- FFmpeg (用于视频处理)

## 安装

1. 克隆项目后，进入后端目录：
```bash
cd tiktok-analyzer-backend
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入以下 API 密钥：

#### TikWM API (视频下载)
- 注册地址: https://rapidapi.com/tikwm/api/tiktok-video-details
- 免费版: 每天 50 次

#### Google Cloud Speech-to-Text (语音转写)
- 注册地址: https://cloud.google.com/speech-to-text
- 免费版: 每月 60 分钟

#### 阿里云视觉智能 (OCR/图像分析)
- 注册地址: https://vision.aliyun.com
- 免费版: 每月 1000 次

#### 通义千问 (AI分析)
- 注册地址: https://dashscope.console.aliyun.com
- 免费版: 有一定免费额度

## 运行

开发模式：
```bash
uvicorn app.main:app --reload --port 8000
```

服务启动后，访问：
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc

## API 接口

### 分析视频
```bash
POST /api/analyze
{
    "url": "https://www.tiktok.com/@user/video/123456789",
    "language": "zh-CN"
}
```

### 查询进度
```bash
GET /api/task/{task_id}
```

### 获取视频信息
```bash
POST /api/video/info
{
    "url": "https://www.tiktok.com/@user/video/123456789"
}
```

## 项目结构

```
tiktok-analyzer-backend/
├── app/
│   ├── config.py          # 配置和API密钥
│   ├── main.py            # FastAPI应用入口
│   ├── routers/
│   │   └── analyze.py     # 分析API路由
│   └── services/
│       ├── tiktok_service.py    # TikTok视频下载
│       ├── speech_service.py    # 语音转写
│       ├── vision_service.py     # 视觉识别
│       └── analysis_service.py  # AI分析
├── temp/                  # 临时文件目录
├── uploads/               # 上传文件目录
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
└── README.md
```

## 常见问题

### 1. FFmpeg 未安装
Windows: 下载 https://ffmpeg.org/download.html
Mac: `brew install ffmpeg`
Linux: `sudo apt install ffmpeg`

### 2. Google Cloud 认证失败
确保 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量设置正确，需要是完整的 JSON 内容。

### 3. 阿里云服务区域
本项目使用阿里云华东2（上海）区域，如需更改请修改 `vision_service.py` 中的 endpoint。

## License

MIT License
