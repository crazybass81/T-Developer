"""
Multilingual Processor Module
Handles language detection and translation
"""

from typing import Tuple
import re


class MultilingualProcessor:
    """Processes multilingual input"""
    
    def __init__(self):
        self.language_patterns = {
            'ko': re.compile(r'[\u3131-\u3163\uac00-\ud7a3]+'),
            'ja': re.compile(r'[\u3040-\u309f\u30a0-\u30ff]+'),
            'zh': re.compile(r'[\u4e00-\u9fff]+'),
            'ar': re.compile(r'[\u0600-\u06ff]+'),
            'ru': re.compile(r'[\u0400-\u04ff]+')
        }
        
        self.common_translations = {
            'ko': {
                '만들어': 'create',
                '개발': 'develop',
                '앱': 'app',
                '웹사이트': 'website',
                '로그인': 'login',
                '데이터베이스': 'database',
                '빠른': 'fast',
                '간단한': 'simple'
            },
            'ja': {
                '作成': 'create',
                '開発': 'develop',
                'アプリ': 'app',
                'ウェブサイト': 'website',
                'ログイン': 'login',
                'データベース': 'database'
            }
        }
    
    async def initialize(self):
        """Initialize language models if needed"""
        # Placeholder for future ML model initialization
        pass
    
    async def process(self, text: str, target_language: str = 'en') -> Tuple[str, str]:
        """
        Process multilingual text
        
        Args:
            text: Input text
            target_language: Target language for translation
            
        Returns:
            Tuple of (detected_language, processed_text)
        """
        detected_language = self._detect_language(text)
        
        if detected_language == target_language or detected_language == 'en':
            return detected_language, text
        
        # Simple translation for common terms
        translated = self._simple_translate(text, detected_language, target_language)
        
        return detected_language, translated
    
    def _detect_language(self, text: str) -> str:
        """Detect the primary language of the text"""
        for lang, pattern in self.language_patterns.items():
            if pattern.search(text):
                return lang
        
        return 'en'  # Default to English
    
    def _simple_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Simple word-based translation for common terms"""
        if source_lang not in self.common_translations:
            return text
        
        translated = text
        translations = self.common_translations[source_lang]
        
        for source_word, target_word in translations.items():
            translated = translated.replace(source_word, target_word)
        
        return translated
    
    def get_language_info(self, language_code: str) -> dict:
        """Get information about a language"""
        language_info = {
            'en': {'name': 'English', 'rtl': False},
            'ko': {'name': 'Korean', 'rtl': False},
            'ja': {'name': 'Japanese', 'rtl': False},
            'zh': {'name': 'Chinese', 'rtl': False},
            'ar': {'name': 'Arabic', 'rtl': True},
            'ru': {'name': 'Russian', 'rtl': False}
        }
        
        return language_info.get(language_code, {'name': 'Unknown', 'rtl': False})