"""
TikTok视频下载服务
使用TikWM API获取无水印视频
"""
import httpx
import
import json
 reimport os
from typing import Optional, Dict, Any
from app.config import settings


class TikTokService:
    """TikTok视频下载服务"""

    def __init__(self):
        self.api_key = settings.TIKWM_API_KEY
        self.base_url = "https://tiktok-video-details.p.rapidapi.com"

    def extract_video_id(self, url: str) -> Optional[str]:
        """从URL中提取视频ID"""
        # 匹配模式: tiktok.com/@user/video/123456789 或 vm.tiktok.com/xxx
        patterns = [
            r'tiktok\.com/[@\w]+/video/(\d+)',
            r'vm\.tiktok\.com/(\w+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        获取视频信息（不下载）
        使用TikWM API
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError("无法从URL中提取视频ID")

        # 使用TikWM API获取视频信息
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "tiktok-video-details.p.rapidapi.com"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/video/info",
                params={"video_id": video_id},
                headers=headers,
                timeout=30.0
            )

        if response.status_code == 200:
            data = response.json()
            return self._parse_video_info(data)
        else:
            raise Exception(f"API请求失败: {response.status_code}")

    async def download_video(self, url: str, output_path: str) -> str:
        """
        下载视频到本地
        返回保存的文件路径
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError("无法从URL中提取视频ID")

        # 获取无水印视频链接
        video_url = await self._get_no_watermark_url(url)

        if not video_url:
            raise Exception("无法获取无水印视频链接")

        # 下载视频
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(video_url, timeout=60.0)

        if response.status_code == 200:
            # 保存视频文件
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return output_path
        else:
            raise Exception(f"视频下载失败: {response.status_code}")

    async def _get_no_watermark_url(self, url: str) -> Optional[str]:
        """获取无水印视频URL"""
        # 使用TikWM API的no-watermark端点
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "tiktok-video-details.p.rapidapi.com"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/video/no-watermark",
                params={"url": url},
                headers=headers,
                timeout=30.0
            )

        if response.status_code == 200:
            data = response.json()
            # 尝试多种可能的视频URL字段
            return (data.get("data", {}).get("play") or
                    data.get("data", {}).get("download") or
                    data.get("video_url"))
        return None

    def _parse_video_info(self, data: Dict) -> Dict[str, Any]:
        """解析API返回的视频信息"""
        try:
            video_data = data.get("data", {})
            return {
                "video_id": video_data.get("id"),
                "title": video_data.get("desc", ""),
                "author": video_data.get("author", {}).get("nickname", ""),
                "avatar": video_data.get("author", {}).get("avatar", ""),
                "duration": video_data.get("video", {}).get("duration", 0),
                "cover": video_data.get("video", {}).get("cover", ""),
                "like_count": video_data.get("stats", {}).get("diggCount", 0),
                "comment_count": video_data.get("stats", {}).get("commentCount", 0),
                "share_count": video_data.get("stats", {}).get("shareCount", 0),
                "play_count": video_data.get("stats", {}).get("playCount", 0),
                "download_count": video_data.get("stats", {}).get("downloadCount", 0),
                "create_time": video_data.get("createTime", ""),
            }
        except Exception as e:
            raise Exception(f"解析视频信息失败: {str(e)}")


# 导出服务实例
tiktok_service = TikTokService()
