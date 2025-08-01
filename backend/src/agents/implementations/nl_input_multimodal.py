from agno.tools import ImageAnalyzer, PDFExtractor
from typing import Union, List, Dict, Any
import base64
import io
from PIL import Image
import pytesseract
from .nl_input_agent import NLInputAgent, ProjectRequirements

class DiagramInterpreter:
    """다이어그램 해석기"""
    
    async def interpret(self, image_data: bytes, diagram_type: str) -> Dict[str, Any]:
        """다이어그램 해석"""
        return {
            'type': diagram_type,
            'description': f'{diagram_type} diagram detected',
            'components': ['component1', 'component2'],
            'relationships': ['connects to', 'inherits from']
        }

class MultimodalInputProcessor:
    """텍스트, 이미지, 문서 등 다양한 형식의 입력 처리"""

    def __init__(self, nl_agent: NLInputAgent):
        self.nl_agent = nl_agent
        self.image_analyzer = ImageAnalyzer()
        self.pdf_extractor = PDFExtractor()
        self.diagram_interpreter = DiagramInterpreter()

    async def process_multimodal_input(
        self,
        inputs: List[Union[str, bytes, 'UploadedFile']]
    ) -> ProjectRequirements:
        """멀티모달 입력 처리 및 통합"""

        extracted_texts = []
        diagrams = []

        for input_item in inputs:
            if isinstance(input_item, str):
                extracted_texts.append(input_item)

            elif self._is_image(input_item):
                # 이미지에서 다이어그램이나 UI 목업 분석
                analysis = await self._analyze_image(input_item)
                if analysis.get('contains_diagram'):
                    diagram_info = await self.diagram_interpreter.interpret(
                        input_item,
                        diagram_type=analysis.get('diagram_type', 'unknown')
                    )
                    diagrams.append(diagram_info)
                extracted_texts.append(analysis.get('extracted_text', ''))

            elif self._is_document(input_item):
                # PDF, Word 등 문서에서 텍스트 추출
                doc_content = await self._extract_document(input_item)
                extracted_texts.append(doc_content.get('text', ''))
                diagrams.extend(doc_content.get('diagrams', []))

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

    async def _analyze_image(self, image_data: Union[bytes, 'UploadedFile']) -> Dict[str, Any]:
        """이미지 분석"""
        try:
            # 이미지 데이터 준비
            if hasattr(image_data, 'read'):
                image_bytes = image_data.read()
            else:
                image_bytes = image_data
                
            # PIL로 이미지 열기
            image = Image.open(io.BytesIO(image_bytes))
            
            # OCR로 텍스트 추출
            extracted_text = pytesseract.image_to_string(image, lang='kor+eng')
            
            # 다이어그램 감지 (간단한 휴리스틱)
            contains_diagram = self._detect_diagram(extracted_text, image)
            
            return {
                'extracted_text': extracted_text,
                'contains_diagram': contains_diagram,
                'diagram_type': 'flowchart' if contains_diagram else None
            }
        except Exception as e:
            return {
                'extracted_text': '',
                'contains_diagram': False,
                'error': str(e)
            }

    async def _extract_document(self, doc_data: Union[bytes, 'UploadedFile']) -> Dict[str, Any]:
        """문서에서 텍스트 추출"""
        try:
            if hasattr(doc_data, 'read'):
                doc_bytes = doc_data.read()
            else:
                doc_bytes = doc_data
                
            # PDF 텍스트 추출 (간단한 구현)
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(doc_bytes))
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
                
            return {
                'text': text,
                'diagrams': []  # 실제로는 PDF에서 이미지 추출 필요
            }
        except Exception as e:
            return {
                'text': '',
                'diagrams': [],
                'error': str(e)
            }

    def _detect_diagram(self, text: str, image: Image.Image) -> bool:
        """다이어그램 감지"""
        # 키워드 기반 감지
        diagram_keywords = ['flowchart', 'diagram', '다이어그램', '플로우차트', 'wireframe']
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in diagram_keywords):
            return True
            
        # 이미지 특성 기반 감지 (간단한 휴리스틱)
        width, height = image.size
        aspect_ratio = width / height
        
        # 다이어그램은 보통 가로가 더 긴 경우가 많음
        if aspect_ratio > 1.2:
            return True
            
        return False

    def _combine_extracted_info(
        self,
        texts: List[str],
        diagrams: List[Dict]
    ) -> str:
        """추출된 정보를 통합하여 하나의 설명으로 만들기"""

        combined = "\n\n".join(filter(None, texts))

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
            return input_item.content_type in ['application/pdf', 'application/msword']
        # PDF 매직 바이트
        if isinstance(input_item, bytes):
            return input_item[:4] == b'%PDF'
        return False