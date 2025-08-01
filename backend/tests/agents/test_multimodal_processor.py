import pytest
from unittest.mock import Mock, patch, AsyncMock
import io
from PIL import Image
from backend.src.agents.implementations.nl_input_multimodal import MultimodalInputProcessor
from backend.src.agents.implementations.nl_input_agent import NLInputAgent

class TestMultimodalInputProcessor:
    """멀티모달 입력 처리기 테스트"""

    @pytest.fixture
    def mock_nl_agent(self):
        return Mock(spec=NLInputAgent)

    @pytest.fixture
    def processor(self, mock_nl_agent):
        return MultimodalInputProcessor(mock_nl_agent)

    @pytest.fixture
    def sample_image_bytes(self):
        """테스트용 이미지 바이트 생성"""
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()

    @pytest.fixture
    def sample_pdf_bytes(self):
        """테스트용 PDF 바이트"""
        return b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF'

    def test_is_image_detection(self, processor, sample_image_bytes):
        """이미지 파일 감지 테스트"""
        assert processor._is_image(sample_image_bytes) == True
        assert processor._is_image(b'not an image') == False

    def test_is_document_detection(self, processor, sample_pdf_bytes):
        """문서 파일 감지 테스트"""
        assert processor._is_document(sample_pdf_bytes) == True
        assert processor._is_document(b'not a pdf') == False

    @pytest.mark.asyncio
    async def test_analyze_image(self, processor, sample_image_bytes):
        """이미지 분석 테스트"""
        with patch('pytesseract.image_to_string', return_value='Sample text from image'):
            result = await processor._analyze_image(sample_image_bytes)
            
            assert 'extracted_text' in result
            assert result['extracted_text'] == 'Sample text from image'
            assert 'contains_diagram' in result

    @pytest.mark.asyncio
    async def test_extract_document(self, processor):
        """문서 추출 테스트"""
        mock_pdf_data = b'mock pdf content'
        
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = 'Extracted PDF text'
            mock_reader.return_value.pages = [mock_page]
            
            result = await processor._extract_document(mock_pdf_data)
            
            assert result['text'] == 'Extracted PDF text'
            assert 'diagrams' in result

    def test_combine_extracted_info(self, processor):
        """정보 통합 테스트"""
        texts = ['Text 1', 'Text 2']
        diagrams = [
            {
                'type': 'flowchart',
                'description': 'Process flow',
                'components': ['start', 'process', 'end']
            }
        ]
        
        result = processor._combine_extracted_info(texts, diagrams)
        
        assert 'Text 1' in result
        assert 'Text 2' in result
        assert 'flowchart' in result
        assert 'start' in result

    @pytest.mark.asyncio
    async def test_process_multimodal_input_text_only(self, processor, mock_nl_agent):
        """텍스트만 있는 입력 처리 테스트"""
        inputs = ['Create a web application']
        
        mock_nl_agent.process_description = AsyncMock(return_value=Mock())
        
        await processor.process_multimodal_input(inputs)
        
        mock_nl_agent.process_description.assert_called_once()
        call_args = mock_nl_agent.process_description.call_args
        assert 'Create a web application' in call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_multimodal_input_with_image(self, processor, mock_nl_agent, sample_image_bytes):
        """이미지 포함 입력 처리 테스트"""
        inputs = ['Create a web app', sample_image_bytes]
        
        mock_nl_agent.process_description = AsyncMock(return_value=Mock())
        
        with patch.object(processor, '_analyze_image', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = {
                'extracted_text': 'UI mockup text',
                'contains_diagram': True,
                'diagram_type': 'wireframe'
            }
            
            with patch.object(processor.diagram_interpreter, 'interpret', new_callable=AsyncMock) as mock_interpret:
                mock_interpret.return_value = {
                    'type': 'wireframe',
                    'description': 'UI wireframe',
                    'components': ['header', 'content', 'footer']
                }
                
                await processor.process_multimodal_input(inputs)
                
                mock_nl_agent.process_description.assert_called_once()
                call_args = mock_nl_agent.process_description.call_args
                combined_text = call_args[0][0]
                
                assert 'Create a web app' in combined_text
                assert 'UI mockup text' in combined_text
                assert 'wireframe' in combined_text

    @pytest.mark.asyncio
    async def test_error_handling_invalid_image(self, processor):
        """잘못된 이미지 처리 오류 핸들링 테스트"""
        invalid_image_data = b'invalid image data'
        
        result = await processor._analyze_image(invalid_image_data)
        
        assert result['extracted_text'] == ''
        assert result['contains_diagram'] == False
        assert 'error' in result