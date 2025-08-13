import asyncio
from typing import Any, Dict, Union

from .audio_processor import AudioVideoProcessor
from .image_processor import MultiModalImageProcessor
from .text_processor import MultiModalTextProcessor


class MultiModalProcessor:
    """통합 멀티모달 처리기"""

    def __init__(self):
        self.text_processor = MultiModalTextProcessor()
        self.image_processor = MultiModalImageProcessor()
        self.audio_video_processor = AudioVideoProcessor()

    async def process(
        self, data: Union[str, bytes], data_type: str, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """멀티모달 데이터 처리"""

        if data_type == "text":
            return await self.text_processor.process_text(data, options)

        elif data_type == "image":
            return await self.image_processor.process_image(data, options)

        elif data_type == "audio":
            return await self.audio_video_processor.process_audio(data, options)

        elif data_type == "video":
            return await self.audio_video_processor.process_video(data, options)

        else:
            raise ValueError(f"Unsupported data type: {data_type}")

    async def process_mixed_content(self, content_list: list) -> Dict[str, Any]:
        """혼합 콘텐츠 처리"""
        results = {}

        tasks = []
        for item in content_list:
            task = self.process(item["data"], item["type"], item.get("options", {}))
            tasks.append(task)

        processed_results = await asyncio.gather(*tasks)

        for i, result in enumerate(processed_results):
            results[f"{content_list[i]['type']}_{i}"] = result

        return results
