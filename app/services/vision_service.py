"""
视觉识别服务
使用阿里云视觉智能开放平台进行OCR识别和图像分析
"""
import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alivision20220629 import models as alivision_models
from alibabacloud_alivision20220629.client import Client as AliVisionClient
from app.config import settings


class VisionService:
    """视觉识别服务"""

    def __init__(self):
        self.access_key = settings.ALIYUN_VISION_ACCESS_KEY
        self.secret_key = settings.ALIYUN_VISION_SECRET_KEY
        self.client = None
        if self.access_key and self.access_key != "YOUR_ALIYUN_ACCESS_KEY":
            self._init_client()

    def _init_client(self):
        """初始化阿里云视觉客户端"""
        config = open_api_models.Config(
            access_key_id=self.access_key,
            access_key_secret=self.secret_key,
            endpoint: "aliyuncvc.cn-shanghai.aliyuncs.com",
            region_id="cn-shanghai"
        )
        self.client = AliVisionClient(config)

    async def extract_keyframes(self, video_path: str, interval: int = 3) -> List[str]:
        """
        从视频中提取关键帧

        Args:
            video_path: 视频文件路径
            interval: 提取间隔（秒）

        Returns:
            关键帧图片路径列表
        """
        import cv2

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * interval)

        keyframes = []
        frame_count = 0
        output_dir = "/tmp/keyframes"
        os.makedirs(output_dir, exist_ok=True)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                # 保存关键帧
                frame_path = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
                cv2.imwrite(frame_path, frame)
                keyframes.append(frame_path)

            frame_count += 1

        cap.release()
        return keyframes

    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        分析单张图片

        Args:
            image_path: 图片路径

        Returns:
            分析结果
        """
        if not self.client:
            raise Exception("阿里云视觉服务未初始化，请检查API密钥")

        # 读取图片
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # 调用通用图像识别API
        request = alivision_models.RecognizeImageRequest(
            image_base64=base64_image,
            recognizer='general_general'
        )

        try:
            response = await asyncio.to_thread(self.client.recognize_image, request)
            return self._parse_vision_response(response)
        except Exception as e:
            raise Exception(f"图像识别失败: {str(e)}")

    async def detect_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        检测图片中的文字 (OCR)

        Args:
            image_path: 图片路径

        Returns:
            文字检测结果列表
        """
        if not self.client:
            raise Exception("阿里云视觉服务未初始化，请检查API密钥")

        # 读取图片
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # 调用OCR识别
        request = alivision_models.RecognizeImageRequest(
            image_base64=base64_image,
            recognizer='ocrDocText'
        )

        try:
            response = await asyncio.to_thread(self.client.recognize_image, request)
            return self._parse_ocr_response(response)
        except Exception as e:
            raise Exception(f"OCR识别失败: {str(e)}")

    async def analyze_video_frames(self, video_path: str) -> Dict[str, Any]:
        """
        分析视频的所有关键帧

        Args:
            video_path: 视频文件路径

        Returns:
            汇总分析结果
        """
        # 提取关键帧
        keyframes = await self.extract_keyframes(video_path)

        all_texts = []
        all_objects = []
        frame_analyses = []

        for i, frame_path in enumerate(keyframes):
            try:
                # 文字检测
                texts = await self.detect_text(frame_path)
                all_texts.extend(texts)

                # 图像分析
                analysis = await self.analyze_image(frame_path)
                frame_analyses.append({
                    "frame_index": i,
                    "timestamp": i * 3,
                    "texts": texts,
                    "analysis": analysis
                })

                if "objects" in analysis:
                    all_objects.extend(analysis["objects"])

            except Exception as e:
                print(f"分析第{i}帧失败: {str(e)}")

        return {
            "total_frames": len(keyframes),
            "keyframes": keyframes,
            "all_texts": all_texts,
            "all_objects": all_objects,
            "frame_analyses": frame_analyses,
        }

    def _parse_vision_response(self, response) -> Dict[str, Any]:
        """解析视觉识别响应"""
        try:
            data = json.loads(response.body)
            return {
                "labels": data.get("data", {}).get("labels", []),
                "objects": data.get("data", {}).get("objects", []),
                "faces": data.get("data", {}).get("faces", []),
                "scenes": data.get("data", {}).get("scenes", []),
            }
        except:
            return {"raw": str(response)}

    def _parse_ocr_response(self, response) -> List[Dict[str, Any]]:
        """解析OCR响应"""
        try:
            data = json.loads(response.body)
            words = data.get("data", {}).get("words", [])
            return [
                {
                    "text": word.get("word", ""),
                    "confidence": word.get("confidence", 0),
                    "bbox": word.get("bbox", {})
                }
                for word in words
            ]
        except:
            return []


# 导出服务实例
vision_service = VisionService()
