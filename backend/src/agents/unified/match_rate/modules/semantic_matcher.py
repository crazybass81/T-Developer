"""
Semantic Matcher Module
Performs semantic matching using NLP techniques
"""

from typing import Dict, List, Any, Optional
import re
from collections import Counter


class SemanticMatcher:
    """Performs semantic matching analysis"""
    
    def __init__(self):
        self.domain_keywords = self._build_domain_keywords()
        self.semantic_patterns = self._build_semantic_patterns()
        
    async def match(
        self,
        components: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Perform semantic matching analysis"""
        
        semantic_results = {}
        
        # Extract semantic features from requirements
        req_semantics = self._extract_semantic_features(requirements)
        
        for component in components:
            component_id = component.get('id', component.get('name'))
            
            # Extract semantic features from component
            comp_semantics = self._extract_semantic_features(component)
            
            # Calculate semantic similarity
            semantic_score = self._calculate_semantic_similarity(comp_semantics, req_semantics)
            
            # Analyze intent matching
            intent_match = self._analyze_intent_matching(comp_semantics, req_semantics)
            
            # Analyze domain relevance
            domain_relevance = self._analyze_domain_relevance(comp_semantics, req_semantics)
            
            # Extract key concepts
            key_concepts = self._extract_key_concepts(comp_semantics, req_semantics)
            
            semantic_results[component_id] = {
                'semantic_score': semantic_score,
                'intent_match': intent_match,
                'domain_relevance': domain_relevance,
                'key_concepts': key_concepts,
                'concept_overlap': self._calculate_concept_overlap(comp_semantics, req_semantics),
                'context_alignment': self._analyze_context_alignment(comp_semantics, req_semantics)
            }
        
        return semantic_results
    
    def _extract_semantic_features(self, data: Dict) -> Dict[str, Any]:
        """Extract semantic features from data"""
        
        text = self._extract_all_text(data)
        
        return {
            'keywords': self._extract_keywords(text),
            'entities': self._extract_entities(text),
            'concepts': self._extract_concepts(text),
            'intent': self._extract_intent(text),
            'domain': self._identify_domain(text),
            'sentiment': self._analyze_sentiment(text),
            'complexity': self._analyze_complexity(text)
        }
    
    def _extract_all_text(self, data: Dict) -> str:
        """Extract all text content"""
        
        text_parts = []
        
        for key, value in data.items():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend([str(v) for v in value if isinstance(v, str)])
            elif isinstance(value, dict):
                text_parts.append(self._extract_all_text(value))
        
        return ' '.join(text_parts).lower()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        
        # Remove stop words and extract meaningful keywords
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'to', 'for', 'of', 'with', 'in'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Get most frequent keywords
        word_freq = Counter(keywords)
        return [word for word, freq in word_freq.most_common(20)]
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities (simplified)"""
        
        entities = []
        
        # Technology entities
        tech_patterns = [
            r'\b(react|vue|angular|django|flask|spring|node\.?js)\b',
            r'\b(postgresql|mysql|mongodb|redis|elasticsearch)\b',
            r'\b(aws|azure|gcp|docker|kubernetes)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract conceptual terms"""
        
        concepts = []
        
        # Domain-specific concept patterns
        concept_patterns = {
            'architecture': ['microservice', 'monolithic', 'serverless', 'distributed'],
            'data': ['database', 'storage', 'cache', 'backup', 'migration'],
            'security': ['authentication', 'authorization', 'encryption', 'ssl', 'firewall'],
            'performance': ['optimization', 'scaling', 'load', 'latency', 'throughput'],
            'ui': ['interface', 'component', 'responsive', 'mobile', 'design']
        }
        
        for category, terms in concept_patterns.items():
            for term in terms:
                if term in text:
                    concepts.append(f"{category}:{term}")
        
        return concepts
    
    def _extract_intent(self, text: str) -> str:
        """Extract user intent"""
        
        intent_patterns = {
            'create': ['create', 'build', 'develop', 'make', 'generate'],
            'update': ['update', 'modify', 'change', 'edit', 'improve'],
            'analyze': ['analyze', 'evaluate', 'assess', 'review', 'examine'],
            'optimize': ['optimize', 'enhance', 'improve', 'speed up', 'efficient'],
            'integrate': ['integrate', 'connect', 'combine', 'merge', 'link']
        }
        
        for intent, keywords in intent_patterns.items():
            if any(keyword in text for keyword in keywords):
                return intent
        
        return 'general'
    
    def _identify_domain(self, text: str) -> str:
        """Identify application domain"""
        
        domain_indicators = {
            'ecommerce': ['shop', 'cart', 'payment', 'product', 'order', 'checkout'],
            'social': ['social', 'user', 'profile', 'friend', 'message', 'post'],
            'finance': ['finance', 'bank', 'transaction', 'money', 'account', 'investment'],
            'healthcare': ['health', 'patient', 'medical', 'doctor', 'hospital', 'treatment'],
            'education': ['education', 'student', 'course', 'learning', 'school', 'university'],
            'enterprise': ['enterprise', 'business', 'corporate', 'workflow', 'process']
        }
        
        domain_scores = {}
        for domain, indicators in domain_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            domain_scores[domain] = score
        
        return max(domain_scores, key=domain_scores.get) if domain_scores else 'general'
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment (simplified)"""
        
        positive_words = ['good', 'great', 'excellent', 'fast', 'efficient', 'reliable', 'secure']
        negative_words = ['bad', 'slow', 'complex', 'difficult', 'expensive', 'unreliable']
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        total = pos_count + neg_count
        return (pos_count - neg_count) / total if total > 0 else 0.0
    
    def _analyze_complexity(self, text: str) -> float:
        """Analyze text complexity"""
        
        words = len(text.split())
        sentences = len(re.split(r'[.\!?]+', text))
        
        if sentences == 0:
            return 0.0
        
        avg_words_per_sentence = words / sentences
        
        # Normalize complexity (0-1 scale)
        return min(1.0, avg_words_per_sentence / 20.0)
    
    def _calculate_semantic_similarity(self, comp_semantics: Dict, req_semantics: Dict) -> float:
        """Calculate overall semantic similarity"""
        
        similarities = []
        
        # Keyword overlap
        comp_keywords = set(comp_semantics.get('keywords', []))
        req_keywords = set(req_semantics.get('keywords', []))
        keyword_similarity = len(comp_keywords.intersection(req_keywords)) / len(comp_keywords.union(req_keywords)) if comp_keywords.union(req_keywords) else 0
        similarities.append(keyword_similarity)
        
        # Entity overlap
        comp_entities = set(comp_semantics.get('entities', []))
        req_entities = set(req_semantics.get('entities', []))
        entity_similarity = len(comp_entities.intersection(req_entities)) / len(comp_entities.union(req_entities)) if comp_entities.union(req_entities) else 0
        similarities.append(entity_similarity)
        
        # Concept overlap
        comp_concepts = set(comp_semantics.get('concepts', []))
        req_concepts = set(req_semantics.get('concepts', []))
        concept_similarity = len(comp_concepts.intersection(req_concepts)) / len(comp_concepts.union(req_concepts)) if comp_concepts.union(req_concepts) else 0
        similarities.append(concept_similarity)
        
        # Intent matching
        intent_match = 1.0 if comp_semantics.get('intent') == req_semantics.get('intent') else 0.5
        similarities.append(intent_match)
        
        # Domain matching
        domain_match = 1.0 if comp_semantics.get('domain') == req_semantics.get('domain') else 0.3
        similarities.append(domain_match)
        
        return sum(similarities) / len(similarities)
    
    def _analyze_intent_matching(self, comp_semantics: Dict, req_semantics: Dict) -> Dict[str, Any]:
        """Analyze intent matching"""
        
        comp_intent = comp_semantics.get('intent', 'general')
        req_intent = req_semantics.get('intent', 'general')
        
        return {
            'component_intent': comp_intent,
            'requirement_intent': req_intent,
            'exact_match': comp_intent == req_intent,
            'compatibility_score': self._calculate_intent_compatibility(comp_intent, req_intent)
        }
    
    def _calculate_intent_compatibility(self, intent1: str, intent2: str) -> float:
        """Calculate compatibility between intents"""
        
        compatibility_matrix = {
            'create': {'create': 1.0, 'build': 0.9, 'develop': 0.8, 'update': 0.6},
            'update': {'update': 1.0, 'modify': 0.9, 'improve': 0.8, 'create': 0.6},
            'analyze': {'analyze': 1.0, 'evaluate': 0.9, 'assess': 0.8, 'optimize': 0.7},
            'optimize': {'optimize': 1.0, 'improve': 0.9, 'enhance': 0.8, 'analyze': 0.7},
            'integrate': {'integrate': 1.0, 'connect': 0.9, 'combine': 0.8, 'create': 0.6}
        }
        
        if intent1 in compatibility_matrix and intent2 in compatibility_matrix[intent1]:
            return compatibility_matrix[intent1][intent2]
        
        return 0.5 if intent1 == intent2 else 0.3
    
    def _analyze_domain_relevance(self, comp_semantics: Dict, req_semantics: Dict) -> Dict[str, Any]:
        """Analyze domain relevance"""
        
        comp_domain = comp_semantics.get('domain', 'general')
        req_domain = req_semantics.get('domain', 'general')
        
        return {
            'component_domain': comp_domain,
            'requirement_domain': req_domain,
            'domain_match': comp_domain == req_domain,
            'relevance_score': self._calculate_domain_relevance(comp_domain, req_domain)
        }
    
    def _calculate_domain_relevance(self, domain1: str, domain2: str) -> float:
        """Calculate relevance between domains"""
        
        if domain1 == domain2:
            return 1.0
        
        # Domain similarity matrix
        related_domains = {
            'ecommerce': ['finance', 'enterprise'],
            'social': ['enterprise', 'education'],
            'finance': ['ecommerce', 'enterprise'],
            'healthcare': ['enterprise'],
            'education': ['enterprise', 'social'],
            'enterprise': ['finance', 'education', 'healthcare']
        }
        
        if domain1 in related_domains and domain2 in related_domains[domain1]:
            return 0.7
        
        return 0.3  # General compatibility
    
    def _extract_key_concepts(self, comp_semantics: Dict, req_semantics: Dict) -> List[str]:
        """Extract key concepts from both sources"""
        
        comp_concepts = set(comp_semantics.get('concepts', []))
        req_concepts = set(req_semantics.get('concepts', []))
        
        # Get intersection (common concepts) and high-priority concepts
        common_concepts = comp_concepts.intersection(req_concepts)
        
        return list(common_concepts)[:10]  # Top 10 key concepts
    
    def _calculate_concept_overlap(self, comp_semantics: Dict, req_semantics: Dict) -> float:
        """Calculate concept overlap percentage"""
        
        comp_concepts = set(comp_semantics.get('concepts', []))
        req_concepts = set(req_semantics.get('concepts', []))
        
        if not comp_concepts and not req_concepts:
            return 1.0
        
        intersection = len(comp_concepts.intersection(req_concepts))
        union = len(comp_concepts.union(req_concepts))
        
        return intersection / union if union > 0 else 0.0
    
    def _analyze_context_alignment(self, comp_semantics: Dict, req_semantics: Dict) -> Dict[str, float]:
        """Analyze context alignment"""
        
        return {
            'sentiment_alignment': self._calculate_sentiment_alignment(
                comp_semantics.get('sentiment', 0),
                req_semantics.get('sentiment', 0)
            ),
            'complexity_match': self._calculate_complexity_match(
                comp_semantics.get('complexity', 0),
                req_semantics.get('complexity', 0)
            ),
            'overall_context_score': 0.0  # Will be calculated
        }
    
    def _calculate_sentiment_alignment(self, comp_sentiment: float, req_sentiment: float) -> float:
        """Calculate sentiment alignment"""
        
        # If both are neutral (close to 0), consider it a good match
        if abs(comp_sentiment) < 0.1 and abs(req_sentiment) < 0.1:
            return 1.0
        
        # Calculate similarity (1 - normalized difference)
        max_diff = 2.0  # Maximum possible difference (-1 to +1)
        actual_diff = abs(comp_sentiment - req_sentiment)
        
        return 1.0 - (actual_diff / max_diff)
    
    def _calculate_complexity_match(self, comp_complexity: float, req_complexity: float) -> float:
        """Calculate complexity match"""
        
        # Prefer component complexity to be slightly higher than requirement complexity
        if comp_complexity >= req_complexity:
            return 1.0 - abs(comp_complexity - req_complexity)
        else:
            # Penalize if component is much simpler than required
            return max(0.0, 0.7 - (req_complexity - comp_complexity))
    
    def _build_domain_keywords(self) -> Dict[str, List[str]]:
        """Build domain-specific keyword mappings"""
        
        return {
            'web_development': ['html', 'css', 'javascript', 'react', 'vue', 'angular'],
            'backend': ['api', 'server', 'database', 'microservice', 'rest', 'graphql'],
            'mobile': ['ios', 'android', 'react-native', 'flutter', 'mobile', 'app'],
            'data': ['analytics', 'ml', 'ai', 'data', 'pipeline', 'etl'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'aws', 'azure', 'deployment']
        }
    
    def _build_semantic_patterns(self) -> Dict[str, str]:
        """Build semantic pattern mappings"""
        
        return {
            'action_patterns': r'\b(create|build|develop|implement|design|make)\b',
            'object_patterns': r'\b(app|application|system|platform|service|tool)\b',
            'tech_patterns': r'\b(using|with|based on|powered by)\s+(\w+)\b',
            'requirement_patterns': r'\b(need|require|want|should|must)\b'
        }
