from typing import Dict, List, Tuple, Optional
import langdetect
from googletrans import Translator
from .nl_input_agent import NLInputAgent, ProjectRequirements

class KoreanProcessor:
    """한국어 전처리기"""
    
    def preprocess(self, text: str) -> str:
        # 한국어 특수 처리
        text = text.replace('웹앱', 'web application')
        text = text.replace('모바일앱', 'mobile application')
        return text

class JapaneseProcessor:
    """일본어 전처리기"""
    
    def preprocess(self, text: str) -> str:
        # 일본어 특수 처리
        text = text.replace('ウェブアプリ', 'web application')
        text = text.replace('モバイルアプリ', 'mobile application')
        return text

class ChineseProcessor:
    """중국어 전처리기"""
    
    def preprocess(self, text: str) -> str:
        # 중국어 특수 처리
        text = text.replace('网络应用', 'web application')
        text = text.replace('移动应用', 'mobile application')
        return text

class UnsupportedLanguageError(Exception):
    """지원하지 않는 언어 오류"""
    pass

class MultilingualNLProcessor:
    """다국어 프로젝트 설명 처리"""

    SUPPORTED_LANGUAGES = ['en', 'ko', 'ja', 'zh-cn', 'es', 'fr', 'de']

    def __init__(self, nl_agent: NLInputAgent):
        self.nl_agent = nl_agent
        self.translator = Translator()
        self.language_specific_processors = {
            'ko': KoreanProcessor(),
            'ja': JapaneseProcessor(),
            'zh-cn': ChineseProcessor()
        }

    async def process_multilingual_input(
        self,
        text: str,
        target_lang: str = 'en'
    ) -> Tuple[ProjectRequirements, Dict[str, any]]:
        """다국어 입력 처리"""

        # 1. 언어 감지
        try:
            detected_lang = langdetect.detect(text)
        except:
            detected_lang = 'en'  # 기본값

        if detected_lang not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(f"Language {detected_lang} is not supported")

        # 2. 언어별 전처리
        if detected_lang in self.language_specific_processors:
            preprocessed_text = self.language_specific_processors[
                detected_lang
            ].preprocess(text)
        else:
            preprocessed_text = text

        # 3. 영어로 번역 (NL Agent는 영어로 학습됨)
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

        # 4. NL Agent 처리
        requirements = await self.nl_agent.process_description(translated_text)

        # 5. 결과를 원래 언어로 역번역 (선택적)
        localized_requirements = await self._localize_requirements(
            requirements,
            target_lang=detected_lang
        )

        return requirements, {
            "original_language": detected_lang,
            "processed_text": translated_text,
            "localized_output": localized_requirements
        }

    async def _translate_with_context(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """컨텍스트를 고려한 번역"""
        
        try:
            # Google Translate 사용
            result = self.translator.translate(
                text,
                src=source_lang,
                dest=target_lang
            )
            return result.text
        except Exception as e:
            # 번역 실패 시 원본 반환
            print(f"Translation failed: {e}")
            return text

    def _preserve_technical_terms(
        self,
        original: str,
        translated: str,
        source_lang: str
    ) -> str:
        """기술 용어 보존 처리"""

        # 언어별 기술 용어 사전
        tech_terms = {
            'ko': {
                '프론트엔드': 'frontend',
                '백엔드': 'backend',
                '데이터베이스': 'database',
                'API': 'API',
                '클라우드': 'cloud',
                '리액트': 'React',
                '뷰': 'Vue',
                '앵귤러': 'Angular'
            },
            'ja': {
                'フロントエンド': 'frontend',
                'バックエンド': 'backend',
                'データベース': 'database',
                'リアクト': 'React'
            },
            'zh-cn': {
                '前端': 'frontend',
                '后端': 'backend',
                '数据库': 'database'
            }
        }

        if source_lang in tech_terms:
            for original_term, english_term in tech_terms[source_lang].items():
                if original_term in original:
                    # 번역된 텍스트에서 해당 용어를 영어로 교체
                    translated = self._smart_replace(
                        translated,
                        original_term,
                        english_term
                    )

        return translated

    def _smart_replace(
        self,
        text: str,
        search_term: str,
        replace_term: str
    ) -> str:
        """스마트 용어 교체"""
        
        # 간단한 교체 (실제로는 더 정교한 로직 필요)
        return text.replace(search_term, replace_term)

    async def _localize_requirements(
        self,
        requirements: ProjectRequirements,
        target_lang: str
    ) -> Dict[str, any]:
        """요구사항을 대상 언어로 현지화"""
        
        if target_lang == 'en':
            return requirements.__dict__

        try:
            # 주요 필드만 번역
            localized = {
                'description': await self._translate_with_context(
                    requirements.description, 'en', target_lang
                ),
                'project_type': requirements.project_type,  # 유지
                'technical_requirements': [
                    await self._translate_with_context(req, 'en', target_lang)
                    for req in requirements.technical_requirements
                ],
                'technology_preferences': requirements.technology_preferences  # 유지
            }
            
            return localized
            
        except Exception as e:
            print(f"Localization failed: {e}")
            return requirements.__dict__

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """지원 언어 목록 반환"""
        
        language_names = {
            'en': 'English',
            'ko': '한국어',
            'ja': '日本語',
            'zh-cn': '中文',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch'
        }
        
        return [
            {'code': code, 'name': language_names[code]}
            for code in self.SUPPORTED_LANGUAGES
        ]