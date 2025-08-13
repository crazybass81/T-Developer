import asyncio
from typing import Any, Dict, List, Union

from .multimodal_processor import MultiModalProcessor


class UnifiedMultiModalAPI:
    """통합 멀티모달 API"""

    def __init__(self):
        self.processor = MultiModalProcessor()

    async def process_single(
        self, data: Union[str, bytes], data_type: str, options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """단일 모달 데이터 처리"""
        if options is None:
            options = {}

        result = await self.processor.process(data, data_type, options)

        return {
            "type": data_type,
            "result": result,
            "insights": self._extract_insights(result, data_type),
            "confidence": self._calculate_confidence(result, data_type),
        }

    async def process_batch(self, inputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """배치 처리"""
        tasks = []
        for input_item in inputs:
            task = self.process_single(
                input_item["data"], input_item["type"], input_item.get("options", {})
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        return {
            "results": results,
            "combined_insights": self._combine_insights(results),
            "overall_confidence": self._calculate_overall_confidence(results),
        }

    def _extract_insights(self, result: Dict[str, Any], data_type: str) -> List[str]:
        """결과에서 인사이트 추출"""
        insights = []

        if data_type == "text":
            if result.get("token_count", 0) > 100:
                insights.append("Long text content detected")
            if result.get("chunks"):
                insights.append(f'Text split into {len(result["chunks"])} chunks')

        elif data_type == "image":
            metadata = result.get("metadata", {})
            if metadata.get("width", 0) > 1920:
                insights.append("High resolution image")
            if result.get("extracted_text"):
                insights.append("Text found in image")

        elif data_type == "audio":
            if result.get("transcript"):
                insights.append("Speech detected and transcribed")
            if result.get("duration", 0) > 300:
                insights.append("Long audio content")

        return insights

    def _calculate_confidence(self, result: Dict[str, Any], data_type: str) -> float:
        """신뢰도 계산"""
        if data_type == "text":
            return 0.95  # 텍스트 처리는 일반적으로 높은 신뢰도
        elif data_type == "image":
            return 0.85  # 이미지 처리
        elif data_type in ["audio", "video"]:
            return 0.80  # 오디오/비디오 처리
        return 0.75

    def _combine_insights(self, results: List[Dict[str, Any]]) -> List[str]:
        """여러 결과의 인사이트 결합"""
        all_insights = []
        for result in results:
            all_insights.extend(result.get("insights", []))

        # 중복 제거
        return list(set(all_insights))

    def _calculate_overall_confidence(self, results: List[Dict[str, Any]]) -> float:
        """전체 신뢰도 계산"""
        if not results:
            return 0.0

        confidences = [r.get("confidence", 0.0) for r in results]
        return sum(confidences) / len(confidences)
