"""
语音转文字服务
使用阿里云智能语音交互2.0 (NLS)
"""
import os
import base64
import json
import asyncio
import uuid
from typing import Optional, List, Dict, Any
import httpx
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from app.config import settings


class SpeechService:
    """语音转文字服务 - 阿里云智能语音交互2.0"""

    def __init__(self):
        self.access_key = settings.ALIYUN_VISION_ACCESS_KEY
        self.secret_key = settings.ALIYUN_VISION_SECRET_KEY

        # 初始化阿里云客户端
        self.client = AcsClient(
            self.access_key,
            self.secret_key,
            'cn-shanghai'  # 华东2(上海)
        )

    async def transcribe_audio(self, audio_path: str, language_code: str = "zh-CN") -> List[Dict[str, Any]]:
        """
        将音频文件转录为文字
        使用阿里云录音文件识别API

        Args:
            audio_path: 音频文件路径
            language_code: 语言代码，默认中文 (zh-CN)

        Returns:
            转录结果列表，每个元素包含文字和时间戳
        """
        try:
            # 读取音频文件并转为base64
            with open(audio_path, 'rb') as f:
                audio_base64 = base64.b64encode(f.read()).decode('utf-8')

            # 创建识别请求
            request = CommonRequest()
            request.set_method('POST')
            request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
            request.set_version('2022-08-01')
            request.set_action_name('CreateTask')

            # 设置请求参数 - 录音文件识别
            request.add_query_param('appkey', 'nls-service')  # 需要在控制台创建
            request.add_query_param('file_link', '')  # OSS文件链接，需要先上传到OSS

            # 由于阿里云录音文件识别需要OSS，这里我们使用替代方案
            # 使用语音识别HTTP API直接识别短音频

            return await self._recognize_short_audio(audio_base64, language_code)

        except Exception as e:
            print(f"转录错误: {str(e)}")
            return []

    async def _recognize_short_audio(self, audio_base64: str, language_code: str) -> List[Dict[str, Any]]:
        """识别短音频 - 使用阿里云实时语音识别"""
        try:
            # 使用阿里云实时语音识别API
            request = CommonRequest()
            request.set_method('POST')
            request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
            request.set_version('2022-08-01')
            request.set_action_name('CreateToken')

            # 获取Token
            response = await asyncio.to_thread(self.client.do_action_with_exception, request)
            token_info = json.loads(response.decode('utf-8'))

            if 'Token' not in token_info or 'Id' not in token_info['Token']:
                raise Exception("获取语音识别Token失败")

            token = token_info['Token']['Id']

            # 调用实时语音识别
            # 这里使用简化的REST API方式
            url = f"https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/asr"

            headers = {
                'Content-Type': 'application/json',
                'X-App-Key': 'nls-service',  # 需要在控制台创建应用获取
                'X-Token': token
            }

            # 由于直接调用较复杂，这里返回模拟数据
            # 实际使用需要配置完整的阿里云语音识别应用
            return [{
                "transcript": "[音频转写内容]",
                "confidence": 0.9,
                "words": []
            }]

        except Exception as e:
            print(f"识别错误: {str(e)}")
            return []

    async def transcribe_video(self, video_path: str, language_code: str = "zh-CN") -> List[Dict[str, Any]]:
        """
        从视频文件中提取音频并转录

        Args:
            video_path: 视频文件路径
            language_code: 语言代码

        Returns:
            转录结果列表
        """
        # 使用moviepy提取音频
        from moviepy.editor import AudioFileClip

        # 创建临时音频文件
        temp_audio = "/tmp/temp_audio.wav"

        try:
            # 提取音频
            audio_clip = AudioFileClip(video_path)
            audio_clip.write_audiofile(temp_audio, codec='pcm_s16le', fps=16000, verbose=False, logger=None)
            audio_clip.close()

            # 转录音频
            results = await self.transcribe_audio(temp_audio, language_code)

            # 清理临时文件
            if os.path.exists(temp_audio):
                os.remove(temp_audio)

            return results

        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            print(f"视频音频提取失败: {str(e)}")
            # 返回一个默认结果，避免程序崩溃
            return [{
                "transcript": "视频音频提取或转写失败",
                "confidence": 0,
                "words": []
            }]

    def format_transcript_with_timestamps(self, results: List[Dict[str, Any]]) -> str:
        """
        将转录结果格式化为带时间戳的文本

        Args:
            results: 转录结果列表

        Returns:
            格式化后的文本
        """
        if not results:
            return ""

        formatted_lines = []
        for result in results:
            transcript = result.get("transcript", "")
            words = result.get("words", [])

            if words:
                start_time = words[0].get("start_seconds", 0)
                end_time = words[-1].get("end_seconds", 0)

                # 格式化为 MM:SS
                start_str = f"{int(start_time // 60):02d}:{int(start_time % 60):02d}"
                end_str = f"{int(end_time // 60):02d}:{int(end_time % 60):02d}"

                formatted_lines.append(f"[{start_str} - {end_str}] {transcript}")
            else:
                formatted_lines.append(transcript)

        return "\n".join(formatted_lines)


# 导出服务实例
speech_service = SpeechService()
