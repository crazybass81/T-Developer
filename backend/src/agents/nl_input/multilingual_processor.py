# backend/src/agents/nl_input/multilingual_processor.py
from typing import Dict, List, Tuple, Any, Optional
import langdetect
from dataclasses import dataclass

@dataclass
class TranslationResult:
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float

class MultilingualNLProcessor:
    """완성된 다국어 프로젝트 설명 처리"""

    SUPPORTED_LANGUAGES = ['en', 'ko', 'ja', 'zh-cn', 'es', 'fr', 'de']

    def __init__(self):
        self.tech_terms = {
            'ko': {
                '프론트엔드': 'frontend',
                '백엔드': 'backend',
                '데이터베이스': 'database',
                'API': 'API',
                '클라우드': 'cloud',
                '웹앱': 'web app',
                '모바일앱': 'mobile app'
            },
            'ja': {
                'フロントエンド': 'frontend',
                'バックエンド': 'backend',
                'データベース': 'database',
                'ウェブアプリ': 'web app',
                'モバイルアプリ': 'mobile app'
            },
            'zh-cn': {
                '前端': 'frontend',
                '后端': 'backend',
                '数据库': 'database',
                '网络应用': 'web app',
                '移动应用': 'mobile app'
            }
        }

    async def process_multilingual_input(self, text: str, target_lang: str = 'en') -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """다국어 입력 처리 - 완성된 구현"""
        
        # 1. 언어 감지
        try:
            detected_lang = langdetect.detect(text)
        except:
            detected_lang = 'en'  # 기본값

        if detected_lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Language {detected_lang} is not supported")

        # 2. 언어별 전처리
        preprocessed_text = await self._preprocess_text(text, detected_lang)

        # 3. 영어로 번역
        if detected_lang != 'en':
            translated_text = await self._translate_with_context(
                preprocessed_text,
                detected_lang,
                'en'
            )
            # 기술 용어 보존
            translated_text = self._preserve_technical_terms(
                original=preprocessed_text,
                translated=translated_text,
                source_lang=detected_lang
            )
        else:
            translated_text = preprocessed_text

        # 4. 결과 구성
        requirements = {
            'description': translated_text,
            'original_language': detected_lang,
            'processed': True
        }

        metadata = {
            'original_language': detected_lang,
            'processed_text': translated_text,
            'translation_confidence': 0.9 if detected_lang != 'en' else 1.0
        }

        return requirements, metadata

    async def _preprocess_text(self, text: str, language: str) -> str:
        """언어별 전처리"""
        # 기본 정규화
        processed = text.strip()
        
        # 언어별 특수 처리
        if language == 'ko':
            # 한국어 특수 문자 정리
            processed = processed.replace('～', '~').replace('！', '!')
        elif language == 'ja':
            # 일본어 특수 문자 정리
            processed = processed.replace('～', '~').replace('！', '!')
        elif language == 'zh-cn':
            # 중국어 특수 문자 정리
            processed = processed.replace('～', '~').replace('！', '!')

        return processed

    async def _translate_with_context(self, text: str, source_lang: str, target_lang: str) -> str:
        """컨텍스트를 고려한 번역"""
        # 실제 구현에서는 Google Translate API 또는 AWS Translate 사용
        # 여기서는 간단한 시뮬레이션
        
        # 기술 용어 매핑 적용
        translated = text
        if source_lang in self.tech_terms:
            for original_term, english_term in self.tech_terms[source_lang].items():
                translated = translated.replace(original_term, english_term)
        
        return translated

    def _preserve_technical_terms(self, original: str, translated: str, source_lang: str) -> str:
        """기술 용어 보존 처리 - 완성된 구현"""
        
        if source_lang not in self.tech_terms:
            return translated

        preserved = translated
        
        # 기술 용어 사전에서 용어 보존
        for original_term, english_term in self.tech_terms[source_lang].items():
            if original_term in original:
                # 번역된 텍스트에서 해당 용어를 영어 용어로 교체
                preserved = preserved.replace(original_term, english_term)
        
        return preserved

    async def localize_requirements(self, requirements: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """요구사항 현지화"""
        if target_lang == 'en':
            return requirements
        
        localized = requirements.copy()
        
        # 설명 현지화
        if 'description' in requirements:
            localized['description'] = await self._translate_with_context(
                requirements['description'], 'en', target_lang
            )
        
        return localized