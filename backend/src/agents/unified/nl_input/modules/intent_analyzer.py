"""
Intent Analyzer Module
Analyzes user intent and purpose
"""

from typing import Dict, Any
import re


class IntentAnalyzer:
    """Analyzes the intent behind user requests"""
    
    def __init__(self):
        self.intent_patterns = {
            'create_new': ['create', 'build', 'make', 'develop', 'construct'],
            'improve_existing': ['improve', 'enhance', 'upgrade', 'optimize', 'refactor'],
            'fix_issue': ['fix', 'repair', 'debug', 'solve', 'resolve'],
            'add_feature': ['add', 'implement', 'include', 'integrate'],
            'learn': ['learn', 'understand', 'study', 'practice'],
            'prototype': ['prototype', 'poc', 'proof of concept', 'demo'],
            'production': ['production', 'deploy', 'launch', 'release'],
            'migrate': ['migrate', 'port', 'convert', 'transfer']
        }
        
        self.urgency_indicators = {
            'high': ['urgent', 'asap', 'immediately', 'critical', 'emergency'],
            'medium': ['soon', 'quickly', 'fast', 'rapid'],
            'low': ['eventually', 'when possible', 'no rush', 'future']
        }
        
        self.purpose_keywords = {
            'business': ['business', 'company', 'enterprise', 'commercial'],
            'personal': ['personal', 'hobby', 'fun', 'learning'],
            'education': ['school', 'university', 'course', 'assignment'],
            'nonprofit': ['nonprofit', 'charity', 'volunteer', 'community']
        }
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze the intent of the user request
        
        Args:
            text: User input text
            
        Returns:
            Dictionary containing intent analysis
        """
        text_lower = text.lower()
        
        intent = {
            'primary_intent': self._detect_primary_intent(text_lower),
            'urgency': self._detect_urgency(text_lower),
            'purpose': self._detect_purpose(text_lower),
            'is_question': self._is_question(text),
            'sentiment': self._analyze_sentiment(text_lower),
            'action_verbs': self._extract_action_verbs(text_lower),
            'goals': self._extract_goals(text_lower)
        }
        
        return intent
    
    def _detect_primary_intent(self, text: str) -> str:
        """Detect the primary intent"""
        intent_scores = {}
        
        for intent_type, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                intent_scores[intent_type] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return 'create_new'  # Default intent
    
    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level"""
        for level, indicators in self.urgency_indicators.items():
            if any(indicator in text for indicator in indicators):
                return level
        
        return 'medium'  # Default urgency
    
    def _detect_purpose(self, text: str) -> str:
        """Detect the purpose of the project"""
        for purpose, keywords in self.purpose_keywords.items():
            if any(keyword in text for keyword in keywords):
                return purpose
        
        return 'general'  # Default purpose
    
    def _is_question(self, text: str) -> bool:
        """Check if the input is a question"""
        question_patterns = [
            r'^(what|how|why|when|where|who|which)',
            r'\?$',
            r'(can|could|would|should)\s+(you|i|we)',
            r'(is it|are there|do you)'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze the sentiment of the text"""
        positive_words = ['good', 'great', 'excellent', 'love', 'awesome', 'amazing']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'worst']
        uncertain_words = ['maybe', 'perhaps', 'might', 'could', 'possibly']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        uncertain_count = sum(1 for word in uncertain_words if word in text)
        
        if uncertain_count > positive_count + negative_count:
            return 'uncertain'
        elif positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_action_verbs(self, text: str) -> list:
        """Extract action verbs from text"""
        action_verbs = [
            'create', 'build', 'make', 'develop', 'design',
            'implement', 'add', 'remove', 'update', 'modify',
            'integrate', 'connect', 'deploy', 'test', 'optimize'
        ]
        
        found_verbs = [verb for verb in action_verbs if verb in text]
        return found_verbs
    
    def _extract_goals(self, text: str) -> list:
        """Extract project goals"""
        goals = []
        
        # Pattern for goals
        goal_patterns = [
            r'(?:to|want to|need to|should)\s+([^.,]+)',
            r'(?:goal is|objective is|aim is)\s+([^.,]+)',
            r'(?:so that|in order to)\s+([^.,]+)'
        ]
        
        for pattern in goal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            goals.extend([match.strip() for match in matches])
        
        return goals[:5]  # Return top 5 goals