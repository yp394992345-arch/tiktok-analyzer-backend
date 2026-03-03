"""
分析API路由 - 支持视频文件上传分析
"""
import os
import uuid
import asyncio
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.services import speech_service, vision_service, analysis_service


router = APIRouter(prefix="/api", tags=["分析"])


# ==================== 请求/响应模型 ====================

class AnalyzeRequest(BaseModel):
    """分析请求 - 支持URL或手动输入信息"""
    url: Optional[str] = None  # TikTok视频链接（可选）
    title: Optional[str] = "视频分析"  # 视频标题
    author: Optional[str] = "未知作者"  # 作者
    language: Optional[str] = "zh-CN"  # 语音语言


class VideoInfo(BaseModel):
    """视频信息"""
    video_id: str
    title: str
    author: str
    duration: int


class ProgressResponse(BaseModel):
    """进度响应"""
    task_id: str
    status: str
    progress: int
    message: str


# ==================== 任务管理 ====================

# 存储任务状态（生产环境应使用Redis）
tasks = {}


@router.post("/analyze/upload", response_model=dict)
async def analyze_video_upload(
    file: UploadFile = File(..., description="视频文件 (mp4, mov, avi)"),
    title: str = "视频分析",
    author: str = "未知作者",
    language: str = "zh-CN"
):
    """
    上传视频文件进行分析

    完整的分析流程：
    1. 保存上传的视频文件
    2. 提取音频并转写
    3. 分析关键帧（OCR）
    4. AI话术分析
    """
    task_id = str(uuid.uuid4())

    # 验证文件类型
    allowed_types = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska"]
    if file.content_type not in allowed_types:
        # 尝试根据扩展名判断
        if not file.filename.endswith(('.mp4', '.mov', '.avi', '.mkv')):
            raise HTTPException(status_code=400, detail="不支持的视频格式，请上传 mp4, mov, avi 或 mkv 格式")

    try:
        # 更新任务状态
        tasks[task_id] = {
            "status": "processing",
            "progress": 0,
            "message": "正在保存视频文件..."
        }

        # 1. 保存上传的视频文件
        video_path = f"/tmp/{task_id}_{file.filename}"
        content = await file.read()

        # 限制文件大小 (100MB)
        if len(content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="视频文件过大，请压缩后上传 (最大100MB)")

        with open(video_path, "wb") as f:
            f.write(content)

        tasks[task_id]["progress"] = 10
        tasks[task_id]["message"] = "视频文件保存成功"

        # 获取视频时长
        duration = 0
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if fps > 0:
                duration = int(frame_count / fps)
            cap.release()
        except:
            duration = 0

        # 构建视频信息
        video_info = {
            "video_id": task_id,
            "title": title,
            "author": author,
            "duration": duration,
            "cover": "",
        }

        # 2. 语音转写
        tasks[task_id]["message"] = "正在提取音频并转写..."
        transcript_results = await speech_service.transcribe_video(
            video_path,
            language
        )
        transcript = speech_service.format_transcript_with_timestamps(transcript_results)
        tasks[task_id]["progress"] = 40
        tasks[task_id]["message"] = "语音转写完成"

        # 3. 关键帧提取和OCR
        tasks[task_id]["message"] = "正在分析画面..."
        ocr_texts = []
        frame_analyses = {"error": "阿里云视觉服务配置中..."}

        try:
            # 尝试使用阿里云视觉服务
            frame_analyses = await vision_service.analyze_video_frames(video_path)
            for frame in frame_analyses.get("frame_analyses", []):
                for text in frame.get("texts", []):
                    ocr_texts.append(text.get("text", ""))
        except Exception as e:
            print(f"OCR分析失败: {str(e)}")
            frame_analyses = {"error": str(e)}

        tasks[task_id]["progress"] = 70
        tasks[task_id]["message"] = "画面分析完成"

        # 4. AI话术分析 (使用通义千问)
        tasks[task_id]["message"] = "正在进行AI话术分析..."
        try:
            script_analysis = await analysis_service.analyze_script(
                transcript,
                video_info,
                ocr_texts
            )
        except Exception as e:
            print(f"AI分析失败: {str(e)}")
            script_analysis = {
                "script_structure": [],
                "marketing_strategy": {"error": str(e)},
                "keywords": [],
                "suggestions": ["请检查通义千问API配置"]
            }

        # 5. 画面元素分析
        try:
            visual_analysis = await analysis_service.analyze_visual_elements(
                frame_analyses.get("frame_analyses", []),
                duration
            )
        except Exception as e:
            visual_analysis = {"error": str(e)}

        tasks[task_id]["progress"] = 90
        tasks[task_id]["message"] = "AI分析完成"

        # 清理临时文件
        if os.path.exists(video_path):
            os.remove(video_path)

        # 完成
        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["message"] = "分析完成"

        return {
            "task_id": task_id,
            "status": "completed",
            "video_info": video_info,
            "transcript": transcript,
            "analysis": {
                "script_structure": script_analysis.get("script_structure", []),
                "marketing_strategy": script_analysis.get("marketing_strategy", {}),
                "keywords": script_analysis.get("keywords", []),
                "suggestions": script_analysis.get("suggestions", []),
                "visual_analysis": visual_analysis
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}", response_model=ProgressResponse)
async def get_task_progress(task_id: str):
    """获取任务进度"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks[task_id]
    return ProgressResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"]
    )


@router.post("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "services": {
            "tongyi": "configured" if settings.TONGYI_QIANWEN_API_KEY and settings.TONGYI_QIANWEN_API_KEY != "YOUR_TONGYI_QIANWEN_API_KEY" else "not_configured",
            "aliyun_vision": "configured" if settings.ALIYUN_VISION_ACCESS_KEY and settings.ALIYUN_VISION_ACCESS_KEY != "YOUR_ALIYUN_ACCESS_KEY" else "not_configured",
        }
    }
