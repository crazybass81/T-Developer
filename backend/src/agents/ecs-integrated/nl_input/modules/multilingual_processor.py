"""
Multilingual Processor Module
Handles language detection and translation
"""

from typing import Tuple, Optional
import re

class MultilingualProcessor:
    """Processes multilingual input and translates to target language"""
    
    def __init__(self):
        self.language_indicators = {
            "en": ["the", "and", "is", "for", "with", "application", "website"],
            "es": ["el", "la", "para", "con", "aplicación", "sitio web"],
            "fr": ["le", "la", "pour", "avec", "application", "site web"],
            "de": ["der", "die", "das", "für", "mit", "anwendung"],
            "pt": ["o", "a", "para", "com", "aplicação", "site"],
            "it": ["il", "la", "per", "con", "applicazione", "sito"],
            "ja": ["です", "ます", "アプリ", "サイト", "システム"],
            "ko": ["입니다", "앱", "웹사이트", "시스템", "애플리케이션"],
            "zh": ["的", "是", "应用", "网站", "系统"]
        }
        
        self.common_translations = {
            "es": {
                "aplicación": "application",
                "sitio web": "website",
                "móvil": "mobile",
                "base de datos": "database",
                "usuario": "user"
            },
            "fr": {
                "application": "application",
                "site web": "website",
                "mobile": "mobile",
                "base de données": "database",
                "utilisateur": "user"
            },
            "de": {
                "anwendung": "application",
                "webseite": "website",
                "mobil": "mobile",
                "datenbank": "database",
                "benutzer": "user"
            }
        }
    
    async def initialize(self):
        """Initialize language models if needed"""
        pass
    
    async def process(
        self,
        text: str,
        target_language: str = "en"
    ) -> Tuple[str, str]:
        """
        Process multilingual text
        
        Args:
            text: Input text in any language
            target_language: Target language for translation
            
        Returns:
            Tuple of (detected_language, translated_text)
        """
        
        # Detect language
        detected_lang = self._detect_language(text)
        
        # Translate if needed
        if detected_lang != target_language and detected_lang != "en":
            translated = self._basic_translate(text, detected_lang, target_language)
        else:
            translated = text
        
        return detected_lang, translated
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text"""
        
        text_lower = text.lower()
        scores = {}
        
        for lang, indicators in self.language_indicators.items():
            score = sum(1 for word in indicators if word in text_lower)
            if score > 0:
                scores[lang] = score
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return "en"  # Default to English
    
    def _basic_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Basic translation using dictionary (fallback when no API available)"""
        
        if source_lang not in self.common_translations:
            return text
        
        translated = text
        translations = self.common_translations[source_lang]
        
        for source_word, target_word in translations.items():
            translated = re.sub(
                r'\b' + source_word + r'\b',
                target_word,
                translated,
                flags=re.IGNORECASE
            )
        
        return translated