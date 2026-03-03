"""
配置文件 - 在此处填入你的API密钥
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # ==================== API密钥配置 ====================
    # 请在这里填入你的API密钥，或设置环境变量

    # TikWM API - TikTok视频下载
    # 获取地址: https://rapidapi.com/tikwm/api/tiktok-video-details
    TIKWM_API_KEY: str = "YOUR_TIKWM_API_KEY"

    # Google Cloud Speech-to-Text - 语音转文字
    # 获取地址: https://cloud.google.com/speech-to-text
    # 需要先创建Google Cloud项目，启用Speech-to-Text API
    # 然后下载服务账号JSON密钥文件，将内容设置为环境变量
    GOOGLE_APPLICATION_CREDENTIALS: str = "YOUR_GOOGLE_CREDENTIALS_JSON"

    # 阿里云视觉智能 - OCR识别和画面分析
    # 获取地址: https://vision.aliyun.com
    # 请在服务器上设置环境变量 ALIYUN_VISION_ACCESS_KEY 和 ALIYUN_VISION_SECRET_KEY
    ALIYUN_VISION_ACCESS_KEY: str = ""
    ALIYUN_VISION_SECRET_KEY: str = ""

    # 通义千问 - 大语言模型话术分析
    # 获取地址: https://dashscope.console.aliyun.com
    # 请在服务器上设置环境变量 TONGYI_QIANWEN_API_KEY
    TONGYI_QIANWEN_API_KEY: str = ""

    # ==================== 应用配置 ====================
    APP_NAME: str = "TikTok视频智能拆解助手"
    APP_VERSION: str = "1.0.0"

    # 文件存储路径
    TEMP_DIR: str = "temp"
    UPLOAD_DIR: str = "uploads"

    # 最大上传文件大小 (MB)
    MAX_FILE_SIZE: int = 100

    # CORS设置
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
