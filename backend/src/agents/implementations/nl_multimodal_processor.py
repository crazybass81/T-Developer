# Task 4.1.2: Multimodal Input Processing System
from agno.tools import ImageAnalyzer, PDFExtractor
from typing import Union, List, Dict, Any
import base64
import asyncio

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
    ) -> Dict[str, Any]:
        """멀티모달 입력 처리 및 통합"""

        extracted_texts = []
        diagrams = []

        for input_item in inputs:
            if isinstance(input_item, str):
                extracted_texts.append(input_item)
            elif self._is_image(input_item):
                analysis = await self.image_analyzer.analyze(input_item)
                if analysis.contains_diagram:
                    diagram_info = await self.diagram_interpreter.interpret(
                        input_item, diagram_type=analysis.diagram_type
                    )
                    diagrams.append(diagram_info)
                extracted_texts.append(analysis.extracted_text)
            elif self._is_document(input_item):
                doc_content = await self.pdf_extractor.extract(input_item)
                extracted_texts.append(doc_content.text)
                diagrams.extend(doc_content.diagrams)

        combined_description = self._combine_extracted_info(
            texts=extracted_texts, diagrams=diagrams
        )

        return await self.nl_agent.process_description(
            combined_description,
            context={"has_diagrams": len(diagrams) > 0}
        )

    def _is_image(self, input_item: Union[bytes, 'UploadedFile']) -> bool:
        if hasattr(input_item, 'content_type'):
            return input_item.content_type.startswith('image/')
        if isinstance(input_item, bytes):
            return (input_item[:4] == b'\xff\xd8\xff\xe0' or  # JPEG
                   input_item[:8] == b'\x89PNG\r\n\x1a\n')    # PNG
        return False

    def _is_document(self, input_item: Union[bytes, 'UploadedFile']) -> bool:
        if hasattr(input_item, 'content_type'):
            return input_item.content_type == 'application/pdf'
        return False

    def _combine_extracted_info(self, texts: List[str], diagrams: List[Dict]) -> str:
        combined = "\n\n".join(texts)
        if diagrams:
            combined += "\n\n### 다이어그램 정보:\n"
            for i, diagram in enumerate(diagrams):
                combined += f"\n{i+1}. {diagram['type']}: {diagram['description']}"
                if 'components' in diagram:
                    combined += f"\n   컴포넌트: {', '.join(diagram['components'])}"
        return combined

class DiagramInterpreter:
    async def interpret(self, image_data, diagram_type):
        return {
            'type': diagram_type,
            'description': 'System architecture diagram',
            'components': ['Frontend', 'Backend', 'Database'],
            'relationships': ['Frontend -> Backend', 'Backend -> Database']
        }