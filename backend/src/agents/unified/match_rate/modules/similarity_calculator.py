"""
Similarity Calculator Module
Calculates various similarity metrics between components and requirements
"""

from typing import Dict, List, Any, Optional
import numpy as np
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimilarityCalculator:
    """Calculates similarity using multiple methods"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
    async def calculate(
        self,
        components: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate similarity scores using multiple methods"""
        
        similarities = {}
        
        for component in components:
            component_id = component.get('id', component.get('name'))
            
            similarities[component_id] = {
                'cosine_similarity': self._cosine_similarity(component, requirements),
                'jaccard_similarity': self._jaccard_similarity(component, requirements),
                'euclidean_similarity': self._euclidean_similarity(component, requirements),
                'semantic_similarity': self._semantic_similarity(component, requirements),
                'fuzzy_similarity': self._fuzzy_similarity(component, requirements),
                'weighted_average': 0.0
            }
            
            # Calculate weighted average
            similarities[component_id]['weighted_average'] = self._calculate_weighted_average(
                similarities[component_id]
            )
        
        return similarities
    
    def _cosine_similarity(self, component: Dict, requirements: Dict) -> float:
        """Calculate cosine similarity"""
        
        comp_features = self._extract_features(component)
        req_features = self._extract_features(requirements)
        
        # Convert to vectors
        comp_vector = self._features_to_vector(comp_features)
        req_vector = self._features_to_vector(req_features)
        
        # Calculate cosine similarity
        dot_product = np.dot(comp_vector, req_vector)
        magnitude1 = np.linalg.norm(comp_vector)
        magnitude2 = np.linalg.norm(req_vector)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _jaccard_similarity(self, component: Dict, requirements: Dict) -> float:
        """Calculate Jaccard similarity"""
        
        comp_features = set(self._extract_keywords(component))
        req_features = set(self._extract_keywords(requirements))
        
        intersection = len(comp_features.intersection(req_features))
        union = len(comp_features.union(req_features))
        
        return intersection / union if union > 0 else 0.0
    
    def _euclidean_similarity(self, component: Dict, requirements: Dict) -> float:
        """Calculate Euclidean similarity (converted to similarity from distance)"""
        
        comp_features = self._extract_numeric_features(component)
        req_features = self._extract_numeric_features(requirements)
        
        # Ensure same length
        max_len = max(len(comp_features), len(req_features))
        comp_features.extend([0] * (max_len - len(comp_features)))
        req_features.extend([0] * (max_len - len(req_features)))
        
        # Calculate Euclidean distance
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(comp_features, req_features)))
        
        # Convert to similarity (1 / (1 + distance))
        return 1 / (1 + distance)
    
    def _semantic_similarity(self, component: Dict, requirements: Dict) -> float:
        """Calculate semantic similarity using TF-IDF"""
        
        comp_text = self._extract_text(component)
        req_text = self._extract_text(requirements)
        
        if not comp_text or not req_text:
            return 0.0
        
        # Create TF-IDF vectors
        documents = [comp_text, req_text]
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return similarity_matrix[0][1]
    
    def _fuzzy_similarity(self, component: Dict, requirements: Dict) -> float:
        """Calculate fuzzy string similarity"""
        
        comp_name = str(component.get('name', ''))
        req_keywords = ' '.join(str(v) for v in requirements.values() if isinstance(v, str))
        
        return self._calculate_string_similarity(comp_name, req_keywords)
    
    def _extract_features(self, data: Dict) -> List[str]:
        """Extract features from component or requirements"""
        
        features = []
        
        # Extract text features
        for key, value in data.items():
            if isinstance(value, str):
                features.extend(value.lower().split())
            elif isinstance(value, list):
                features.extend([str(v).lower() for v in value])
        
        return features
    
    def _extract_keywords(self, data: Dict) -> List[str]:
        """Extract keywords from data"""
        
        keywords = []
        
        text_fields = ['name', 'description', 'tags', 'category', 'type']
        
        for field in text_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    keywords.extend(value.lower().split())
                elif isinstance(value, list):
                    keywords.extend([str(v).lower() for v in value])
        
        return list(set(keywords))  # Remove duplicates
    
    def _extract_numeric_features(self, data: Dict) -> List[float]:
        """Extract numeric features"""
        
        features = []
        
        numeric_fields = ['priority', 'complexity', 'performance', 'cost', 'popularity']
        
        for field in numeric_fields:
            if field in data and isinstance(data[field], (int, float)):
                features.append(float(data[field]))
        
        # Add derived features
        features.append(len(str(data.get('description', ''))))  # Description length
        features.append(len(data.get('tags', [])))  # Number of tags
        
        return features
    
    def _extract_text(self, data: Dict) -> str:
        """Extract all text from data"""
        
        text_parts = []
        
        for key, value in data.items():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend([str(v) for v in value if isinstance(v, str)])
            elif isinstance(value, dict):
                text_parts.append(self._extract_text(value))
        
        return ' '.join(text_parts)
    
    def _features_to_vector(self, features: List[str]) -> np.ndarray:
        """Convert features to numerical vector"""
        
        # Simple word count vectorization
        word_counts = {}
        for word in features:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top 100 most common words as dimensions
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:100]
        
        vector = np.zeros(100)
        for i, (word, count) in enumerate(sorted_words):
            vector[i] = count
        
        return vector
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using Levenshtein distance"""
        
        if not str1 or not str2:
            return 0.0
        
        # Levenshtein distance
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        
        distance = dp[m][n]
        max_len = max(m, n)
        
        return 1 - (distance / max_len) if max_len > 0 else 0.0
    
    def _calculate_weighted_average(self, similarities: Dict[str, float]) -> float:
        """Calculate weighted average of all similarity metrics"""
        
        weights = {
            'cosine_similarity': 0.3,
            'jaccard_similarity': 0.2,
            'euclidean_similarity': 0.15,
            'semantic_similarity': 0.25,
            'fuzzy_similarity': 0.1
        }
        
        weighted_sum = sum(
            similarities[metric] * weight
            for metric, weight in weights.items()
            if metric in similarities and isinstance(similarities[metric], (int, float))
        )
        
        return min(1.0, max(0.0, weighted_sum))
