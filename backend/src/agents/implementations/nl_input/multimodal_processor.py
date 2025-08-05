"""
T-Developer MVP - Multimodal Input Processor

텍스트, 이미지, 문서 등 다양한 형식의 입력 처리
"""

from typing import Union, List, Dict, Any
import base64
import asyncio
from pathlib import Path

from agno.tools import ImageAnalyzer, PDFExtractor

class MultimodalInputProcessor:
    """텍스트, 이미지, 문서 등 다양한 형식의 입력 처리"""

    def __init__(self, nl_agent):
        self.nl_agent = nl_agent
        self.image_analyzer = ImageAnalyzer()
        self.pdf_extractor = PDFExtractor()
        self.diagram_interpreter = DiagramInterpreter()

    async def process_multimodal_input(
        self,
        inputs: List[Union[str, bytes, 'UploadedFile']]
    ) -> 'ProjectRequirements':
        """멀티모달 입력 처리 및 통합"""

        extracted_texts = []
        diagrams = []

        for input_item in inputs:
            if isinstance(input_item, str):
                extracted_texts.append(input_item)

            elif self._is_image(input_item):
                # 이미지에서 다이어그램이나 UI 목업 분석
                analysis = await self.image_analyzer.analyze(input_item)
                if analysis.contains_diagram:
                    diagram_info = await self.diagram_interpreter.interpret(
                        input_item,
                        diagram_type=analysis.diagram_type
                    )
                    diagrams.append(diagram_info)
                extracted_texts.append(analysis.extracted_text)

            elif self._is_document(input_item):
                # PDF, Word 등 문서에서 텍스트 추출
                doc_content = await self.pdf_extractor.extract(input_item)
                extracted_texts.append(doc_content.text)
                diagrams.extend(doc_content.diagrams)

        # 모든 추출된 정보 통합
        combined_description = self._combine_extracted_info(
            texts=extracted_texts,
            diagrams=diagrams
        )

        # NL 에이전트로 처리
        return await self.nl_agent.process_description(
            combined_description,
            context={"has_diagrams": len(diagrams) > 0}
        )

    def _combine_extracted_info(
        self,
        texts: List[str],
        diagrams: List[Dict]
    ) -> str:
        """추출된 정보를 통합하여 하나의 설명으로 만들기"""

        combined = "\n\n".join(texts)

        if diagrams:
            combined += "\n\n### 다이어그램 정보:\n"
            for i, diagram in enumerate(diagrams):
                combined += f"\n{i+1}. {diagram['type']}: {diagram['description']}"
                if 'components' in diagram:
                    combined += f"\n   컴포넌트: {', '.join(diagram['components'])}"
                if 'relationships' in diagram:
                    combined += f"\n   관계: {', '.join(diagram['relationships'])}"

        return combined

    def _is_image(self, input_item: Union[bytes, 'UploadedFile']) -> bool:
        """이미지 파일 여부 확인"""
        if hasattr(input_item, 'content_type'):
            return input_item.content_type.startswith('image/')
        
        # 매직 바이트 확인
        if isinstance(input_item, bytes):
            return (input_item[:4] == b'\xff\xd8\xff\xe0' or  # JPEG
                   input_item[:8] == b'\x89PNG\r\n\x1a\n')    # PNG
        return False

    def _is_document(self, input_item: Union[bytes, 'UploadedFile']) -> bool:
        """문서 파일 여부 확인"""
        if hasattr(input_item, 'content_type'):
            return input_item.content_type in [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
        
        # 매직 바이트 확인
        if isinstance(input_item, bytes):
            return input_item[:4] == b'%PDF'  # PDF
        return False

class DiagramInterpreter:
    """다이어그램 해석기"""
    
    async def interpret(self, image_data: bytes, diagram_type: str) -> Dict[str, Any]:
        """다이어그램 해석"""
        
        # 다이어그램 타입별 해석
        if diagram_type == 'flowchart':
            return await self._interpret_flowchart(image_data)
        elif diagram_type == 'wireframe':
            return await self._interpret_wireframe(image_data)
        elif diagram_type == 'architecture':
            return await self._interpret_architecture(image_data)
        else:
            return await self._interpret_generic(image_data)
    
    async def _interpret_flowchart(self, image_data: bytes) -> Dict[str, Any]:
        """플로우차트 해석"""
        return {
            'type': 'flowchart',
            'description': '사용자 플로우 다이어그램',
            'components': ['시작', '로그인', '메인페이지', '종료'],
            'relationships': ['시작->로그인', '로그인->메인페이지']
        }
    
    async def _interpret_wireframe(self, image_data: bytes) -> Dict[str, Any]:
        """와이어프레임 해석"""
        return {
            'type': 'wireframe',
            'description': 'UI 와이어프레임',
            'components': ['헤더', '네비게이션', '메인컨텐츠', '푸터'],
            'relationships': ['헤더-네비게이션 연결', '메인컨텐츠 중앙배치']
        }
    
    async def _interpret_architecture(self, image_data: bytes) -> Dict[str, Any]:
        """아키텍처 다이어그램 해석"""
        return {
            'type': 'architecture',
            'description': '시스템 아키텍처',
            'components': ['프론트엔드', '백엔드', '데이터베이스'],
            'relationships': ['프론트엔드-백엔드 API 통신', '백엔드-데이터베이스 연결']
        }
    
    async def _interpret_generic(self, image_data: bytes) -> Dict[str, Any]:
        """일반 다이어그램 해석"""
        return {
            'type': 'generic',
            'description': '일반 다이어그램',
            'components': [],
            'relationships': []
        }