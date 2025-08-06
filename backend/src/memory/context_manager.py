from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import hashlib
import re

@dataclass
class ContextEntry:
    key: str
    value: Any
    timestamp: datetime
    relevance_score: float
    access_count: int
    source: str
    metadata: Dict[str, Any]

class RelevanceCalculator:
    def __init__(self):
        self.keyword_weights = {
            'project': 1.0,
            'requirement': 0.9,
            'component': 0.8,
            'user': 0.7,
            'task': 0.6
        }
    
    async def calculate(self, key: str, value: Any, existing_context: Dict[str, ContextEntry]) -> float:
        """Calculate relevance score for new context entry"""
        base_score = 0.5
        
        # Keyword matching
        text = f"{key} {str(value)}".lower()
        keyword_score = sum(
            weight for keyword, weight in self.keyword_weights.items()
            if keyword in text
        ) / len(self.keyword_weights)
        
        # Recency weight (new items get higher score)
        recency_weight = 1.0
        
        # Context coherence
        coherence_score = 0.5
        if existing_context:
            similar_count = sum(
                1 for entry in existing_context.values()
                if self._calculate_similarity(text, f"{entry.key} {str(entry.value)}".lower()) > 0.3
            )
            coherence_score = min(1.0, similar_count / len(existing_context))
        
        return min(1.0, base_score * 0.3 + keyword_score * 0.3 + recency_weight * 0.2 + coherence_score * 0.2)
    
    async def calculate_query_relevance(self, query: str, entry: ContextEntry) -> float:
        """Calculate relevance of context entry to query"""
        query_lower = query.lower()
        entry_text = f"{entry.key} {str(entry.value)}".lower()
        
        # Text similarity
        similarity = self._calculate_similarity(query_lower, entry_text)
        
        # Access frequency bonus
        access_bonus = min(0.2, entry.access_count * 0.01)
        
        # Recency bonus
        age_hours = (datetime.utcnow() - entry.timestamp).total_seconds() / 3600
        recency_bonus = max(0, 0.1 - age_hours * 0.001)
        
        return min(1.0, similarity + access_bonus + recency_bonus)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity using common words"""
        words1 = set(re.findall(r'\w+', text1))
        words2 = set(re.findall(r'\w+', text2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0

class ContextManager:
    def __init__(self, max_context_size: int = 1000):
        self.context: Dict[str, ContextEntry] = {}
        self.max_context_size = max_context_size
        self.relevance_calculator = RelevanceCalculator()
    
    async def add_context(
        self,
        key: str,
        value: Any,
        source: str = 'user',
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add information to context"""
        
        # Handle duplicate keys
        if key in self.context:
            await self._merge_context(key, value, metadata)
            return
        
        # Manage context size
        if len(self.context) >= self.max_context_size:
            await self._compress_context()
        
        # Calculate relevance score
        relevance_score = await self.relevance_calculator.calculate(
            key, value, self.context
        )
        
        # Create context entry
        entry = ContextEntry(
            key=key,
            value=value,
            timestamp=datetime.utcnow(),
            relevance_score=relevance_score,
            access_count=0,
            source=source,
            metadata=metadata or {}
        )
        
        self.context[key] = entry
    
    async def get_relevant_context(
        self,
        query: str,
        max_items: int = 10
    ) -> List[ContextEntry]:
        """Get context entries relevant to query"""
        
        # Calculate relevance scores for all entries
        scores = []
        for entry in self.context.values():
            score = await self.relevance_calculator.calculate_query_relevance(
                query, entry
            )
            scores.append((score, entry))
        
        # Sort by score
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Return top items
        relevant_entries = [entry for _, entry in scores[:max_items]]
        
        # Update access count
        for entry in relevant_entries:
            entry.access_count += 1
        
        return relevant_entries
    
    async def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context"""
        if not self.context:
            return {"total_entries": 0, "sources": {}, "avg_relevance": 0}
        
        sources = {}
        total_relevance = 0
        
        for entry in self.context.values():
            sources[entry.source] = sources.get(entry.source, 0) + 1
            total_relevance += entry.relevance_score
        
        return {
            "total_entries": len(self.context),
            "sources": sources,
            "avg_relevance": total_relevance / len(self.context),
            "oldest_entry": min(entry.timestamp for entry in self.context.values()),
            "newest_entry": max(entry.timestamp for entry in self.context.values())
        }
    
    async def _merge_context(self, key: str, value: Any, metadata: Optional[Dict[str, Any]]) -> None:
        """Merge new value with existing context entry"""
        existing = self.context[key]
        
        # Update value (combine if both are lists/dicts)
        if isinstance(existing.value, dict) and isinstance(value, dict):
            existing.value.update(value)
        elif isinstance(existing.value, list) and isinstance(value, list):
            existing.value.extend(value)
        else:
            existing.value = value
        
        # Update metadata
        if metadata:
            existing.metadata.update(metadata)
        
        # Update timestamp and relevance
        existing.timestamp = datetime.utcnow()
        existing.relevance_score = await self.relevance_calculator.calculate(
            key, existing.value, self.context
        )
    
    async def _compress_context(self) -> None:
        """Compress context by removing low-relevance entries"""
        if len(self.context) <= self.max_context_size * 0.8:
            return
        
        # Calculate thresholds
        relevance_scores = [entry.relevance_score for entry in self.context.values()]
        relevance_threshold = sorted(relevance_scores)[len(relevance_scores) // 4]  # Bottom 25%
        
        current_time = datetime.utcnow()
        age_threshold = timedelta(hours=24)
        access_threshold = 1
        
        # Find items to remove
        items_to_remove = []
        for key, entry in self.context.items():
            if (entry.relevance_score < relevance_threshold and
                entry.access_count < access_threshold and
                current_time - entry.timestamp > age_threshold):
                items_to_remove.append(key)
        
        # Remove items
        for key in items_to_remove:
            del self.context[key]
        
        # If still too large, remove oldest low-relevance items
        if len(self.context) > self.max_context_size * 0.9:
            sorted_entries = sorted(
                self.context.items(),
                key=lambda x: (x[1].relevance_score, x[1].timestamp)
            )
            
            remove_count = len(self.context) - int(self.max_context_size * 0.8)
            for key, _ in sorted_entries[:remove_count]:
                del self.context[key]
    
    async def clear_context(self, source: Optional[str] = None) -> int:
        """Clear context entries, optionally filtered by source"""
        if source:
            keys_to_remove = [
                key for key, entry in self.context.items()
                if entry.source == source
            ]
            for key in keys_to_remove:
                del self.context[key]
            return len(keys_to_remove)
        else:
            count = len(self.context)
            self.context.clear()
            return count