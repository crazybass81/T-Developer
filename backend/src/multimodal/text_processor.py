from typing import Dict, List, Any
import re

class MultiModalTextProcessor:
    """멀티모달 텍스트 처리기"""
    
    def __init__(self):
        self.max_chunk_size = 4096
        
    async def process_text(self, text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """텍스트 처리 파이프라인"""
        
        # 전처리
        cleaned_text = await self.preprocess(text, options)
        
        # 토큰화
        tokens = self.tokenize(cleaned_text)
        
        # 청킹
        chunks = self.chunk_text(cleaned_text, options.get('max_tokens', self.max_chunk_size))
        
        # 임베딩 (선택적)
        embeddings = None
        if options.get('generate_embeddings'):
            embeddings = await self.generate_embeddings(chunks)
        
        return {
            'original': text,
            'processed': cleaned_text,
            'tokens': tokens,
            'token_count': len(tokens),
            'chunks': chunks,
            'embeddings': embeddings
        }
    
    async def preprocess(self, text: str, options: Dict[str, Any]) -> str:
        """텍스트 전처리"""
        processed = text
        
        # 정규화
        if options.get('normalize'):
            processed = self.normalize_text(processed)
        
        # PII 마스킹
        if options.get('mask_pii'):
            processed = self.mask_sensitive_info(processed)
        
        return processed
    
    def normalize_text(self, text: str) -> str:
        """텍스트 정규화"""
        # 공백 정규화
        text = re.sub(r'\s+', ' ', text)
        # 특수문자 정리
        text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        return text.strip()
    
    def mask_sensitive_info(self, text: str) -> str:
        """민감정보 마스킹"""
        # 이메일 마스킹
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        # 전화번호 마스킹
        text = re.sub(r'\b\d{3}-\d{3,4}-\d{4}\b', '[PHONE]', text)
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """간단한 토큰화"""
        return text.split()
    
    def chunk_text(self, text: str, max_tokens: int) -> List[str]:
        """텍스트 청킹"""
        tokens = self.tokenize(text)
        
        if len(tokens) <= max_tokens:
            return [text]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for token in tokens:
            if current_length + 1 > max_tokens and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [token]
                current_length = 1
            else:
                current_chunk.append(token)
                current_length += 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    async def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """임베딩 생성 (플레이스홀더)"""
        # 실제 구현에서는 OpenAI Embeddings, Sentence Transformers 등 사용
        return [[0.1] * 768 for _ in chunks]  # 768차원 더미 임베딩