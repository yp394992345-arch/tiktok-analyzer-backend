"""
话术分析服务
使用通义千问进行AI话术分析和策略解读
"""
import json
import asyncio
from typing import List, Dict, Any, Optional
import dashscope
from dashscope import Generation
from app.config import settings


class AnalysisService:
    """AI分析服务"""

    def __init__(self):
        self.api_key = settings.TONGYI_QIANWEN_API_KEY
        if self.api_key:
            dashscope.api_key = self.api_key

    def _build_analysis_prompt(
        self,
        transcript: str,
        video_info: Dict[str, Any],
        ocr_texts: List[str]
    ) -> str:
        """构建分析提示词"""
        prompt = f"""
你是一位专业的短视频带货分析师，擅长分析TikTok/抖音等平台的带货视频。

## 视频信息
- 视频标题: {video_info.get('title', '')}
- 视频作者: {video_info.get('author', '')}
- 视频时长: {video_info.get('duration', 0)}秒

## 语音转写内容
{transcript}

## 画面文字识别结果 (OCR)
{chr(10).join(ocr_texts) if ocr_texts else '无文字识别结果'}

## 请分析以下内容

### 1. 话术结构拆解
请将视频内容拆解为以下阶段：
- 黄金3秒 (Hook): 开头吸引用户注意力的内容
- 痛点引入: 描述目标用户痛点场景
- 产品展示: 产品介绍和展示
- 信任背书: 建立信任的内容
- 效果对比: 展示使用效果对比
- 促销逼单: 价格优惠、限时限量等
- CTA引导: 行动号召，引导购买

### 2. 营销策略分析
分析视频使用的营销技巧：
- 情绪价值: 视频传递了什么情绪
- 信任建立: 如何建立用户信任
- 转化技巧: 用了哪些转化技巧
- 互动设计: 是否有互动引导

### 3. 关键词提取
提取视频中的关键词和热词

### 4. 优化建议
给出改进建议

请以JSON格式输出，格式如下：
```json
{{
    "script_structure": [
        {{
            "time_range": "0:00-0:03",
            "type": "黄金3秒",
            "content": "具体话术内容",
            "strategy": "使用的策略说明"
        }}
    ],
    "marketing_strategy": {{
        "emotional_value": "情绪价值分析",
        "trust_building": "信任建立方式",
        "conversion_techniques": "转化技巧分析",
        "interaction_design": "互动设计分析"
    }},
    "keywords": ["关键词1", "关键词2"],
    "suggestions": ["建议1", "建议2"]
}}
```
"""
        return prompt

    async def analyze_script(
        self,
        transcript: str,
        video_info: Dict[str, Any],
        ocr_texts: List[str]
    ) -> Dict[str, Any]:
        """
        使用通义千问分析视频话术

        Args:
            transcript: 语音转写文本
            video_info: 视频信息
            ocr_texts: OCR识别出的文字列表

        Returns:
            分析结果
        """
        if not self.api_key or self.api_key == "YOUR_TONGYI_QIANWEN_API_KEY":
            raise Exception("通义千问API未配置，请检查API密钥")

        prompt = self._build_analysis_prompt(transcript, video_info, ocr_texts)

        try:
            # 调用通义千问API
            response = await asyncio.to_thread(
                Generation.call,
                model=Generation.Models.QWEN_TURBO,
                prompt=prompt,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # 尝试解析JSON
                return self._parse_analysis_result(content)
            else:
                raise Exception(f"API调用失败: {response.code} - {response.message}")

        except Exception as e:
            raise Exception(f"话术分析失败: {str(e)}")

    def _parse_analysis_result(self, content: str) -> Dict[str, Any]:
        """解析分析结果"""
        try:
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            return {"raw_content": content}
        except json.JSONDecodeError:
            return {"raw_content": content, "error": "JSON解析失败"}

    async def analyze_visual_elements(
        self,
        frame_analyses: List[Dict[str, Any]],
        video_duration: int
    ) -> Dict[str, Any]:
        """
        分析画面元素和节奏

        Args:
            frame_analyses: 关键帧分析结果列表
            video_duration: 视频总时长

        Returns:
            画面分析结果
        """
        if not self.api_key or self.api_key == "YOUR_TONGYI_QIANWEN_API_KEY":
            raise Exception("通义千问API未配置，请检查API密钥")

        prompt = f"""
分析以下视频关键帧的画面特点和节奏：

视频时长: {video_duration}秒
关键帧数量: {len(frame_analyses)}

关键帧文字内容:
{chr(10).join([
    f"第{frame.get('timestamp', 0)}秒: {', '.join([t.get('text', '') for t in frame.get('texts', [])])}"
    for frame in frame_analyses
])}

请分析：
1. 镜头景别变化（特写、近景、全景等）
2. 镜头运动方式（固定、推近、摇镜等）
3. 文字/贴纸出现时机
4. 整体节奏把控

以JSON格式输出：
```json
{{
    "shot_composition": {{
        "close_up": "特写占比和内容",
        "medium_shot": "近景占比和内容",
        "wide_shot": "全景占比和内容"
    }},
    "camera_movement": {{
        "static": "固定镜头",
        "push": "推近镜头",
        "pan": "摇镜镜头"
    }},
    "text_timing": [
        {{"time": "0:00", "content": "文字内容", "type": "开场文字"}}
    ],
    "rhythm": "节奏分析"
}}
```
"""
        try:
            response = await asyncio.to_thread(
                Generation.call,
                model=Generation.Models.QWEN_TURBO,
                prompt=prompt,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    return json.loads(json_match.group())
                return {"raw_content": content}
            else:
                return {"error": f"API调用失败: {response.code}"}

        except Exception as e:
            return {"error": str(e)}


# 导出服务实例
analysis_service = AnalysisService()
