"""
TikTok视频智能拆解助手 - 后端服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import analyze


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    yield
    # 关闭时
    print("👋 应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 功能介绍

TikTok带货视频智能拆解助手，可以帮助你：

- 📥 **视频下载**: 输入TikTok链接，自动下载无水印视频
- 🎙️ **语音转写**: 提取视频音频，转换为带时间戳的文字
- 🔍 **画面分析**: 提取关键帧，识别画面文字
- 🤖 **AI话术分析**: 使用AI分析带货脚本、话术结构、营销策略
- 💡 **优化建议**: 提供改进建议

## API使用流程

1. 调用 `/api/analyze` 开始分析视频
2. 通过 `/api/task/{task_id}` 查询进度
3. 获取完整分析结果
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(analyze.router)


@app.get("/")
async def root():
    """根路由"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
