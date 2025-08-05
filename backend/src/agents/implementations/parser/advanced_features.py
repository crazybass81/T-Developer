"""
Parser Agent - Advanced Features Implementation
Task 4.26: 다국어 지원, 실시간 협업, 대용량 처리
"""

from typing import Dict, List, Any, Optional, AsyncGenerator
import asyncio
import aiofiles
from dataclasses import dataclass
import langdetect
from googletrans import Translator
import json
import hashlib
from datetime import datetime

@dataclass
class MultilingualRequirement:
    original_text: str
    original_language: str
    translated_text: str
    confidence: float
    preserved_terms: Dict[str, str]

class MultilingualParser:
    """다국어 요구사항 파싱 지원"""
    
    SUPPORTED_LANGUAGES = ['en', 'ko', 'ja', 'zh-cn', 'es', 'fr', 'de']
    
    def __init__(self):
        self.translator = Translator()
        self.tech_terms = self._load_tech_terms()
    
    async def process_multilingual_input(
        self, text: str, target_lang: str = 'en'
    ) -> MultilingualRequirement:
        """다국어 입력 처리"""
        
        # 언어 감지
        detected_lang = langdetect.detect(text)
        
        if detected_lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {detected_lang}")
        
        # 기술 용어 보존
        preserved_terms = self._preserve_technical_terms(text, detected_lang)
        
        # 번역 (필요시)
        if detected_lang != target_lang:
            translated_text = await self._translate_with_context(
                text, detected_lang, target_lang, preserved_terms
            )
        else:
            translated_text = text
        
        return MultilingualRequirement(
            original_text=text,
            original_language=detected_lang,
            translated_text=translated_text,
            confidence=0.9,
            preserved_terms=preserved_terms
        )
    
    def _load_tech_terms(self) -> Dict[str, Dict[str, str]]:
        """기술 용어 사전 로드"""
        return {
            'ko': {
                '프론트엔드': 'frontend',
                '백엔드': 'backend', 
                '데이터베이스': 'database',
                'API': 'API',
                '사용자': 'user'
            },
            'ja': {
                'フロントエンド': 'frontend',
                'バックエンド': 'backend',
                'データベース': 'database'
            }
        }
    
    def _preserve_technical_terms(self, text: str, lang: str) -> Dict[str, str]:
        """기술 용어 보존"""
        preserved = {}
        if lang in self.tech_terms:
            for original, english in self.tech_terms[lang].items():
                if original in text:
                    preserved[original] = english
        return preserved
    
    async def _translate_with_context(
        self, text: str, source_lang: str, target_lang: str, 
        preserved_terms: Dict[str, str]
    ) -> str:
        """컨텍스트 보존 번역"""
        
        # 기술 용어를 임시 토큰으로 대체
        temp_text = text
        token_map = {}
        
        for i, (original, english) in enumerate(preserved_terms.items()):
            token = f"__TECH_TERM_{i}__"
            temp_text = temp_text.replace(original, token)
            token_map[token] = english
        
        # 번역 실행
        translated = self.translator.translate(
            temp_text, src=source_lang, dest=target_lang
        ).text
        
        # 기술 용어 복원
        for token, english_term in token_map.items():
            translated = translated.replace(token, english_term)
        
        return translated


class RealtimeCollaborativeParser:
    """실시간 협업 파싱"""
    
    def __init__(self):
        self.active_sessions = {}
        self.change_log = []
    
    async def start_collaborative_session(
        self, session_id: str, initial_text: str
    ) -> Dict[str, Any]:
        """협업 세션 시작"""
        
        self.active_sessions[session_id] = {
            'text': initial_text,
            'participants': [],
            'last_update': datetime.utcnow(),
            'version': 1,
            'changes': []
        }
        
        return {
            'session_id': session_id,
            'status': 'active',
            'version': 1
        }
    
    async def apply_change(
        self, session_id: str, user_id: str, change: Dict[str, Any]
    ) -> Dict[str, Any]:
        """변경사항 적용"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # 변경사항 적용
        if change['type'] == 'insert':
            session['text'] = (
                session['text'][:change['position']] + 
                change['content'] + 
                session['text'][change['position']:]
            )
        elif change['type'] == 'delete':
            session['text'] = (
                session['text'][:change['start']] + 
                session['text'][change['end']:]
            )
        elif change['type'] == 'replace':
            session['text'] = (
                session['text'][:change['start']] + 
                change['content'] + 
                session['text'][change['end']:]
            )
        
        # 메타데이터 업데이트
        session['version'] += 1
        session['last_update'] = datetime.utcnow()
        session['changes'].append({
            'user_id': user_id,
            'change': change,
            'timestamp': datetime.utcnow().isoformat(),
            'version': session['version']
        })
        
        return {
            'session_id': session_id,
            'version': session['version'],
            'status': 'updated'
        }
    
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """세션 상태 조회"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        return {
            'session_id': session_id,
            'text': session['text'],
            'version': session['version'],
            'last_update': session['last_update'].isoformat(),
            'participants': session['participants'],
            'change_count': len(session['changes'])
        }


class LargeDocumentProcessor:
    """대용량 문서 처리 최적화"""
    
    def __init__(self, chunk_size: int = 5000):
        self.chunk_size = chunk_size
        self.processing_cache = {}
    
    async def process_large_document(
        self, file_path: str, parser_agent
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """대용량 문서 스트리밍 처리"""
        
        # 파일 크기 확인
        file_size = await self._get_file_size(file_path)
        
        if file_size < 50000:  # 50KB 미만은 일반 처리
            content = await self._read_file(file_path)
            result = await parser_agent.parse_requirements(content)
            yield {'type': 'complete', 'data': result, 'progress': 100}
            return
        
        # 청크 단위 처리
        chunk_count = 0
        total_chunks = (file_size // self.chunk_size) + 1
        
        async for chunk in self._read_file_chunks(file_path):
            chunk_count += 1
            
            # 청크 처리
            chunk_result = await self._process_chunk(chunk, parser_agent)
            
            progress = (chunk_count / total_chunks) * 100
            
            yield {
                'type': 'chunk_processed',
                'data': chunk_result,
                'progress': progress,
                'chunk': chunk_count,
                'total_chunks': total_chunks
            }
        
        # 최종 병합
        final_result = await self._merge_chunk_results()
        yield {'type': 'complete', 'data': final_result, 'progress': 100}
    
    async def _read_file_chunks(self, file_path: str) -> AsyncGenerator[str, None]:
        """파일을 청크 단위로 읽기"""
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            while True:
                chunk = await file.read(self.chunk_size)
                if not chunk:
                    break
                
                # 문장 경계에서 자르기
                if len(chunk) == self.chunk_size:
                    last_period = chunk.rfind('.')
                    if last_period > self.chunk_size * 0.8:  # 80% 이상 위치에 있으면
                        yield chunk[:last_period + 1]
                        # 나머지는 다음 청크에 포함
                        await file.seek(file.tell() - (len(chunk) - last_period - 1))
                    else:
                        yield chunk
                else:
                    yield chunk
    
    async def _process_chunk(self, chunk: str, parser_agent) -> Dict[str, Any]:
        """청크 처리"""
        
        # 청크 해시로 캐시 확인
        chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
        
        if chunk_hash in self.processing_cache:
            return self.processing_cache[chunk_hash]
        
        # 청크 파싱
        try:
            result = await parser_agent.parse_requirements(chunk)
            self.processing_cache[chunk_hash] = result
            return result
        except Exception as e:
            return {'error': str(e), 'chunk_hash': chunk_hash}
    
    async def _merge_chunk_results(self) -> Dict[str, Any]:
        """청크 결과 병합"""
        
        merged_result = {
            'functional_requirements': [],
            'non_functional_requirements': [],
            'technical_requirements': [],
            'user_stories': [],
            'data_models': [],
            'api_specifications': []
        }
        
        # 캐시된 결과들을 병합
        for result in self.processing_cache.values():
            if 'error' not in result:
                for key in merged_result.keys():
                    if hasattr(result, key):
                        merged_result[key].extend(getattr(result, key, []))
        
        return merged_result
    
    async def _get_file_size(self, file_path: str) -> int:
        """파일 크기 조회"""
        import os
        return os.path.getsize(file_path)
    
    async def _read_file(self, file_path: str) -> str:
        """전체 파일 읽기"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            return await file.read()


class AdvancedParserFeatures:
    """고급 파서 기능 통합"""
    
    def __init__(self, parser_agent):
        self.parser_agent = parser_agent
        self.multilingual_parser = MultilingualParser()
        self.collaborative_parser = RealtimeCollaborativeParser()
        self.large_doc_processor = LargeDocumentProcessor()
    
    async def parse_multilingual_requirements(
        self, text: str, source_lang: Optional[str] = None
    ) -> Dict[str, Any]:
        """다국어 요구사항 파싱"""
        
        # 다국어 처리
        multilingual_req = await self.multilingual_parser.process_multilingual_input(
            text, target_lang='en'
        )
        
        # 번역된 텍스트로 파싱
        parsed_result = await self.parser_agent.parse_requirements(
            multilingual_req.translated_text
        )
        
        return {
            'original_language': multilingual_req.original_language,
            'translated_text': multilingual_req.translated_text,
            'preserved_terms': multilingual_req.preserved_terms,
            'parsed_result': parsed_result
        }
    
    async def start_collaborative_parsing(
        self, session_id: str, initial_text: str
    ) -> Dict[str, Any]:
        """협업 파싱 세션 시작"""
        
        session = await self.collaborative_parser.start_collaborative_session(
            session_id, initial_text
        )
        
        # 초기 파싱 실행
        initial_parse = await self.parser_agent.parse_requirements(initial_text)
        
        return {
            'session': session,
            'initial_parse': initial_parse
        }
    
    async def process_large_document_stream(
        self, file_path: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """대용량 문서 스트리밍 처리"""
        
        async for result in self.large_doc_processor.process_large_document(
            file_path, self.parser_agent
        ):
            yield result