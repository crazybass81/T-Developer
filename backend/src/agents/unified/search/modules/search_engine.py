"""
Search Engine Module
Core search functionality for component retrieval
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import math
from datetime import datetime


class SearchEngine:
    """Core search engine implementation"""
    
    def __init__(self):
        self.search_algorithms = {
            'exact': self._exact_search,
            'fuzzy': self._fuzzy_search,
            'wildcard': self._wildcard_search,
            'phrase': self._phrase_search,
            'boolean': self._boolean_search
        }
        self.scoring_weights = {
            'name_match': 3.0,
            'description_match': 2.0,
            'tag_match': 2.5,
            'category_match': 1.8,
            'technology_match': 1.5,
            'feature_match': 1.2,
            'keyword_match': 1.0
        }
        
    async def search(
        self, 
        query: Dict[str, Any], 
        components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute search query against component library"""
        
        search_type = query.get('query_type', 'standard')
        terms = query.get('expanded_terms', query.get('terms', []))
        
        if not terms:
            return []
        
        results = []
        
        # Apply appropriate search algorithm
        if search_type == 'exact':
            results = await self._exact_search(query, components)
        elif search_type == 'fuzzy':
            results = await self._fuzzy_search(query, components)
        elif search_type == 'boolean':
            results = await self._boolean_search(query, components)
        elif search_type == 'phrase':
            results = await self._phrase_search(query, components)
        elif search_type == 'wildcard':
            results = await self._wildcard_search(query, components)
        else:
            results = await self._hybrid_search(query, components)
        
        # Apply boost factors
        results = self._apply_boost_factors(results, query)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return results
    
    async def _exact_search(
        self, 
        query: Dict[str, Any], 
        components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Exact match search"""
        
        search_term = query.get('original_query', '').lower()
        results = []
        
        for component in components:
            score = 0.0
            matches = []
            
            # Check exact matches in various fields
            fields_to_search = {
                'name': self.scoring_weights['name_match'],
                'description': self.scoring_weights['description_match'],
                'tags': self.scoring_weights['tag_match'],
                'category': self.scoring_weights['category_match'],
                'technology': self.scoring_weights['technology_match']
            }
            
            for field, weight in fields_to_search.items():
                field_value = str(component.get(field, '')).lower()
                
                if field == 'tags' and isinstance(component.get('tags'), list):
                    # Handle tag array
                    for tag in component['tags']:
                        if search_term == tag.lower():
                            score += weight
                            matches.append(f"exact_tag:{tag}")
                else:
                    # Handle string fields
                    if search_term == field_value:
                        score += weight
                        matches.append(f"exact_{field}:{field_value}")
                    elif search_term in field_value:
                        score += weight * 0.8  # Partial match
                        matches.append(f"partial_{field}:{field_value}")
            
            if score > 0:
                result = component.copy()
                result['score'] = score
                result['matches'] = matches
                result['search_type'] = 'exact'
                results.append(result)
        
        return results
    
    async def _fuzzy_search(
        self, 
        query: Dict[str, Any], 
        components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fuzzy matching search"""
        
        terms = query.get('expanded_terms', [])
        fuzzy_threshold = query.get('fuzzy_threshold', 0.7)
        results = []
        
        for component in components:
            total_score = 0.0
            matches = []
            
            for term in terms:
                term_score = 0.0
                
                # Check fuzzy matches in text fields
                text_fields = ['name', 'description', 'documentation']
                for field in text_fields:
                    field_value = str(component.get(field, ''))
                    similarity = self._calculate_string_similarity(term, field_value)
                    
                    if similarity >= fuzzy_threshold:
                        weight = self.scoring_weights.get(f"{field}_match", 1.0)
                        field_score = similarity * weight
                        term_score += field_score
                        matches.append(f"fuzzy_{field}:{term}:{similarity:.2f}")
                
                # Check fuzzy matches in tags
                if 'tags' in component:
                    for tag in component['tags']:
                        similarity = self._calculate_string_similarity(term, tag)
                        if similarity >= fuzzy_threshold:
                            tag_score = similarity * self.scoring_weights['tag_match']
                            term_score += tag_score
                            matches.append(f"fuzzy_tag:{term}:{similarity:.2f}")
                
                total_score += term_score
            
            if total_score > 0:
                result = component.copy()
                result['score'] = total_score / len(terms) if terms else 0
                result['matches'] = matches
                result['search_type'] = 'fuzzy'
                results.append(result)
        
        return results
    
    async def _wildcard_search(
        self, 
        query: Dict[str, Any], 
        components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Wildcard pattern search"""
        
        original_query = query.get('original_query', '')
        results = []
        
        # Convert wildcard patterns to regex
        regex_pattern = self._wildcard_to_regex(original_query)
        
        for component in components:
            score = 0.0
            matches = []
            
            # Search text fields with wildcard pattern
            searchable_fields = ['name', 'description', 'category', 'technology']
            
            for field in searchable_fields:
                field_value = str(component.get(field, ''))
                
                if re.search(regex_pattern, field_value, re.IGNORECASE):
                    weight = self.scoring_weights.get(f"{field}_match", 1.0)
                    score += weight
                    matches.append(f"wildcard_{field}:{field_value}")
            
            # Search in tags
            if 'tags' in component:
                for tag in component['tags']:
                    if re.search(regex_pattern, tag, re.IGNORECASE):
                        score += self.scoring_weights['tag_match']
                        matches.append(f"wildcard_tag:{tag}")
            
            if score > 0:
                result = component.copy()
                result['score'] = score
                result['matches'] = matches
                result['search_type'] = 'wildcard'
                results.append(result)
        
        return results
    
    async def _phrase_search(
        self, 
        query: Dict[str, Any], 
        components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Phrase matching search"""
        
        phrase = query.get('original_query', '').strip('"')
        results = []
        
        for component in components:
            score = 0.0
            matches = []
            
            # Search for exact phrase in text fields
            searchable_fields = ['name', 'description', 'documentation']
            
            for field in searchable_fields:
                field_value = str(component.get(field, '')).lower()
                
                if phrase.lower() in field_value:
                    weight = self.scoring_weights.get(f"{field}_match", 1.0)
                    # Boost score for shorter fields (more precise match)
                    precision_boost = 1.0 + (50 / max(len(field_value), 50))
                    score += weight * precision_boost
                    matches.append(f"phrase_{field}:{phrase}")
            
            if score > 0:
                result = component.copy()
                result['score'] = score
                result['matches'] = matches
                result['search_type'] = 'phrase'
                results.append(result)
        
        return results
    
    async def _boolean_search(
        self, 
        query: Dict[str, Any], 
        components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Boolean query search (AND, OR, NOT)"""
        
        terms = query.get('terms', [])
        operators = query.get('operators', [])
        original_query = query.get('original_query', '')
        
        results = []
        
        for component in components:
            if self._evaluate_boolean_query(original_query, component):
                score = self._calculate_boolean_score(terms, component)
                
                result = component.copy()
                result['score'] = score
                result['search_type'] = 'boolean'
                result['matches'] = [f"boolean_match:{original_query}"]
                results.append(result)
        
        return results
    
    async def _hybrid_search(
        self, 
        query: Dict[str, Any], 
        components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Hybrid search combining multiple algorithms"""
        
        terms = query.get('expanded_terms', query.get('terms', []))
        results = []
        
        for component in components:
            total_score = 0.0
            all_matches = []
            
            # Calculate scores from different search methods
            for term in terms:
                # Exact match score
                exact_score = self._calculate_exact_match_score(term, component)
                
                # Fuzzy match score
                fuzzy_score = self._calculate_fuzzy_match_score(term, component)
                
                # TF-IDF style score
                tfidf_score = self._calculate_tfidf_score(term, component, components)
                
                # Combine scores with weights
                combined_score = (
                    exact_score * 0.5 +
                    fuzzy_score * 0.3 +
                    tfidf_score * 0.2
                )
                
                total_score += combined_score
                
                if combined_score > 0.1:  # Threshold for relevance
                    all_matches.append(f"hybrid:{term}:{combined_score:.2f}")
            
            if total_score > 0:
                result = component.copy()
                result['score'] = total_score / len(terms) if terms else 0
                result['matches'] = all_matches
                result['search_type'] = 'hybrid'
                results.append(result)
        
        return results
    
    def _apply_boost_factors(
        self, 
        results: List[Dict[str, Any]], 
        query: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply boost factors based on query requirements"""
        
        boost_fields = query.get('boost_fields', {})
        
        for result in results:
            original_score = result.get('score', 0)
            boost_multiplier = 1.0
            
            # Apply field-specific boosts
            for field, boost_value in boost_fields.items():
                if field in result and result[field]:
                    boost_multiplier += (boost_value - 1.0) * 0.5
            
            # Apply popularity boost
            popularity = result.get('popularity', 5.0)
            popularity_boost = 1.0 + (popularity / 10.0) * 0.2
            
            # Apply recency boost
            last_updated = result.get('last_updated')
            recency_boost = self._calculate_recency_boost(last_updated)
            
            # Calculate final score
            result['score'] = original_score * boost_multiplier * popularity_boost * recency_boost
            result['boost_applied'] = {
                'field_boost': boost_multiplier,
                'popularity_boost': popularity_boost,
                'recency_boost': recency_boost
            }
        
        return results
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using Levenshtein distance"""
        
        if not str1 or not str2:
            return 0.0
        
        str1, str2 = str1.lower(), str2.lower()
        
        # Quick check for exact match
        if str1 == str2:
            return 1.0
        
        # Check for substring match
        if str1 in str2 or str2 in str1:
            shorter, longer = (str1, str2) if len(str1) < len(str2) else (str2, str1)
            return len(shorter) / len(longer)
        
        # Levenshtein distance calculation
        matrix = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]
        
        for i in range(len(str1) + 1):
            matrix[i][0] = i
        for j in range(len(str2) + 1):
            matrix[0][j] = j
        
        for i in range(1, len(str1) + 1):
            for j in range(1, len(str2) + 1):
                if str1[i-1] == str2[j-1]:
                    matrix[i][j] = matrix[i-1][j-1]
                else:
                    matrix[i][j] = min(
                        matrix[i-1][j] + 1,      # deletion
                        matrix[i][j-1] + 1,      # insertion
                        matrix[i-1][j-1] + 1     # substitution
                    )
        
        distance = matrix[len(str1)][len(str2)]
        max_len = max(len(str1), len(str2))
        
        return 1.0 - (distance / max_len)
    
    def _wildcard_to_regex(self, pattern: str) -> str:
        """Convert wildcard pattern to regex"""
        
        # Escape regex special characters except * and ?
        escaped = re.escape(pattern)
        # Convert wildcards to regex
        regex_pattern = escaped.replace(r'\*', '.*').replace(r'\?', '.')
        
        return regex_pattern
    
    def _evaluate_boolean_query(self, query: str, component: Dict[str, Any]) -> bool:
        """Evaluate boolean query against component"""
        
        # Simplified boolean evaluation - in production would use proper parser
        query_lower = query.lower()
        
        # Extract all searchable text from component
        searchable_text = ' '.join([
            str(component.get('name', '')),
            str(component.get('description', '')),
            str(component.get('category', '')),
            str(component.get('technology', '')),
            ' '.join(component.get('tags', []))
        ]).lower()
        
        # Simple AND/OR/NOT evaluation
        if ' and ' in query_lower:
            terms = [term.strip() for term in query_lower.split(' and ')]
            return all(term in searchable_text for term in terms)
        elif ' or ' in query_lower:
            terms = [term.strip() for term in query_lower.split(' or ')]
            return any(term in searchable_text for term in terms)
        elif ' not ' in query_lower:
            parts = query_lower.split(' not ')
            if len(parts) == 2:
                must_have, must_not_have = parts
                return must_have.strip() in searchable_text and must_not_have.strip() not in searchable_text
        
        # Default: check if query appears in text
        return query_lower in searchable_text
    
    def _calculate_boolean_score(self, terms: List[str], component: Dict[str, Any]) -> float:
        """Calculate score for boolean matches"""
        
        score = 0.0
        searchable_fields = ['name', 'description', 'tags', 'category', 'technology']
        
        for term in terms:
            for field in searchable_fields:
                field_value = str(component.get(field, '')).lower()
                if term.lower() in field_value:
                    weight = self.scoring_weights.get(f"{field}_match", 1.0)
                    score += weight
        
        return score
    
    def _calculate_exact_match_score(self, term: str, component: Dict[str, Any]) -> float:
        """Calculate exact match score for a term"""
        
        score = 0.0
        term_lower = term.lower()
        
        # Check each field for exact matches
        if term_lower == str(component.get('name', '')).lower():
            score += self.scoring_weights['name_match']
        
        if term_lower in str(component.get('description', '')).lower():
            score += self.scoring_weights['description_match'] * 0.8
        
        if 'tags' in component:
            for tag in component['tags']:
                if term_lower == tag.lower():
                    score += self.scoring_weights['tag_match']
        
        return score
    
    def _calculate_fuzzy_match_score(self, term: str, component: Dict[str, Any]) -> float:
        """Calculate fuzzy match score for a term"""
        
        max_score = 0.0
        
        # Check fuzzy matches in various fields
        fields_to_check = ['name', 'description', 'category', 'technology']
        
        for field in fields_to_check:
            field_value = str(component.get(field, ''))
            similarity = self._calculate_string_similarity(term, field_value)
            weight = self.scoring_weights.get(f"{field}_match", 1.0)
            field_score = similarity * weight
            max_score = max(max_score, field_score)
        
        return max_score
    
    def _calculate_tfidf_score(
        self, 
        term: str, 
        component: Dict[str, Any], 
        all_components: List[Dict[str, Any]]
    ) -> float:
        """Calculate TF-IDF style score"""
        
        term_lower = term.lower()
        
        # Term frequency in current component
        tf = 0
        component_text = ' '.join([
            str(component.get('name', '')),
            str(component.get('description', '')),
            ' '.join(component.get('tags', []))
        ]).lower()
        
        tf = component_text.count(term_lower)
        
        if tf == 0:
            return 0.0
        
        # Document frequency across all components
        df = 0
        for comp in all_components:
            comp_text = ' '.join([
                str(comp.get('name', '')),
                str(comp.get('description', '')),
                ' '.join(comp.get('tags', []))
            ]).lower()
            
            if term_lower in comp_text:
                df += 1
        
        if df == 0:
            return 0.0
        
        # TF-IDF calculation
        idf = math.log(len(all_components) / df)
        tfidf = tf * idf
        
        return tfidf
    
    def _calculate_recency_boost(self, last_updated: Optional[str]) -> float:
        """Calculate recency boost based on last update date"""
        
        if not last_updated:
            return 1.0
        
        try:
            update_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            now = datetime.now(update_date.tzinfo)
            days_ago = (now - update_date).days
            
            # Boost recent updates, decay over time
            if days_ago <= 30:
                return 1.2
            elif days_ago <= 90:
                return 1.1
            elif days_ago <= 180:
                return 1.05
            elif days_ago <= 365:
                return 1.0
            else:
                return 0.95
                
        except (ValueError, AttributeError):
            return 1.0