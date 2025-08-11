"""
Semantic Search Module
Advanced semantic search using natural language processing and embeddings
"""

from typing import Dict, List, Any, Optional, Tuple
import re
import math
from collections import defaultdict
import asyncio


class SemanticSearch:
    """Advanced semantic search implementation"""
    
    def __init__(self):
        # Semantic similarity thresholds
        self.similarity_threshold = 0.6
        self.high_similarity_threshold = 0.8
        
        # Word embeddings and semantic relationships
        self.word_relationships = self._build_word_relationships()
        self.concept_mappings = self._build_concept_mappings()
        self.synonym_weights = self._build_synonym_weights()
        
        # Domain-specific knowledge
        self.domain_concepts = self._build_domain_concepts()
        self.technology_relationships = self._build_technology_relationships()
        
        # Semantic scoring weights
        self.semantic_weights = {
            'exact_semantic_match': 2.0,
            'concept_similarity': 1.5,
            'contextual_relevance': 1.2,
            'domain_expertise': 1.0,
            'intent_matching': 1.3,
            'linguistic_similarity': 0.8
        }
        
    async def search(
        self,
        query: Dict[str, Any],
        components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Perform semantic search"""
        
        if not components:
            return []
        
        # Extract semantic features from query
        query_features = await self._extract_query_semantics(query)
        
        # Calculate semantic similarity for each component
        scored_components = []
        
        for component in components:
            # Extract component semantics
            component_features = self._extract_component_semantics(component)
            
            # Calculate semantic similarity
            similarity_score = await self._calculate_semantic_similarity(
                query_features, component_features
            )
            
            if similarity_score >= self.similarity_threshold:
                result = component.copy()
                result['semantic_score'] = similarity_score
                result['semantic_matches'] = self._get_semantic_matches(
                    query_features, component_features
                )
                result['search_type'] = 'semantic'
                
                # Add semantic ranking factors
                result['semantic_ranking'] = self._get_semantic_ranking_factors(
                    query_features, component_features, similarity_score
                )
                
                scored_components.append(result)
        
        # Sort by semantic score
        scored_components.sort(key=lambda x: x['semantic_score'], reverse=True)
        
        return scored_components
    
    async def _extract_query_semantics(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Extract semantic features from query"""
        
        query_text = query.get('original_query', '')
        terms = query.get('expanded_terms', query.get('terms', []))
        requirements = query.get('requirements', {})
        
        # Extract intent
        intent = self._detect_intent(query_text)
        
        # Extract concepts
        concepts = self._extract_concepts(query_text, terms)
        
        # Extract domain context
        domain_context = self._extract_domain_context(query_text, requirements)
        
        # Extract semantic entities
        entities = self._extract_entities(query_text)
        
        # Analyze query complexity and specificity
        query_analysis = self._analyze_query_complexity(query_text, terms)
        
        return {
            'original_text': query_text,
            'terms': terms,
            'intent': intent,
            'concepts': concepts,
            'domain_context': domain_context,
            'entities': entities,
            'analysis': query_analysis,
            'embeddings': self._generate_text_embedding(query_text)
        }
    
    def _extract_component_semantics(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """Extract semantic features from component"""
        
        # Combine all textual content
        combined_text = self._combine_component_text(component)
        
        # Extract component concepts
        concepts = self._extract_concepts(combined_text, component.get('tags', []))
        
        # Extract domain information
        domain_info = self._extract_component_domain_info(component)
        
        # Extract functional capabilities
        capabilities = self._extract_component_capabilities(component)
        
        # Extract technical characteristics
        tech_characteristics = self._extract_tech_characteristics(component)
        
        return {
            'combined_text': combined_text,
            'concepts': concepts,
            'domain_info': domain_info,
            'capabilities': capabilities,
            'tech_characteristics': tech_characteristics,
            'embeddings': self._generate_text_embedding(combined_text)
        }
    
    async def _calculate_semantic_similarity(
        self,
        query_features: Dict[str, Any],
        component_features: Dict[str, Any]
    ) -> float:
        """Calculate comprehensive semantic similarity"""
        
        total_score = 0.0
        
        # 1. Intent matching
        intent_score = self._calculate_intent_similarity(
            query_features['intent'],
            component_features['capabilities']
        )
        total_score += intent_score * self.semantic_weights['intent_matching']
        
        # 2. Concept similarity
        concept_score = self._calculate_concept_similarity(
            query_features['concepts'],
            component_features['concepts']
        )
        total_score += concept_score * self.semantic_weights['concept_similarity']
        
        # 3. Domain expertise matching
        domain_score = self._calculate_domain_similarity(
            query_features['domain_context'],
            component_features['domain_info']
        )
        total_score += domain_score * self.semantic_weights['domain_expertise']
        
        # 4. Contextual relevance
        context_score = self._calculate_contextual_relevance(
            query_features,
            component_features
        )
        total_score += context_score * self.semantic_weights['contextual_relevance']
        
        # 5. Embedding similarity
        embedding_score = self._calculate_embedding_similarity(
            query_features['embeddings'],
            component_features['embeddings']
        )
        total_score += embedding_score * self.semantic_weights['linguistic_similarity']
        
        # 6. Exact semantic matches
        exact_score = self._calculate_exact_semantic_matches(
            query_features,
            component_features
        )
        total_score += exact_score * self.semantic_weights['exact_semantic_match']
        
        # Normalize to 0-1 scale
        max_possible_score = sum(self.semantic_weights.values())
        normalized_score = total_score / max_possible_score
        
        return min(normalized_score, 1.0)
    
    def _detect_intent(self, query_text: str) -> Dict[str, float]:
        """Detect user intent from query"""
        
        query_lower = query_text.lower()
        intents = {}
        
        # Search intent patterns
        search_patterns = {
            'find_component': ['find', 'search', 'looking for', 'need', 'want'],
            'compare_options': ['compare', 'vs', 'versus', 'alternatives', 'options'],
            'build_feature': ['build', 'create', 'develop', 'implement', 'make'],
            'solve_problem': ['solve', 'fix', 'resolve', 'handle', 'deal with'],
            'learn_about': ['learn', 'understand', 'explain', 'what is', 'how to'],
            'recommend': ['recommend', 'suggest', 'best', 'top', 'popular']
        }
        
        for intent_type, patterns in search_patterns.items():
            confidence = 0.0
            for pattern in patterns:
                if pattern in query_lower:
                    confidence += 0.2
            
            if confidence > 0:
                intents[intent_type] = min(confidence, 1.0)
        
        # Default intent if none detected
        if not intents:
            intents['find_component'] = 0.5
        
        return intents
    
    def _extract_concepts(self, text: str, additional_terms: List[str] = None) -> List[str]:
        """Extract semantic concepts from text"""
        
        concepts = set()
        text_lower = text.lower()
        
        # Add additional terms
        if additional_terms:
            concepts.update(term.lower() for term in additional_terms)
        
        # Extract concepts using predefined mappings
        for concept, keywords in self.concept_mappings.items():
            for keyword in keywords:
                if keyword in text_lower:
                    concepts.add(concept)
        
        # Extract domain-specific concepts
        for domain, domain_concepts in self.domain_concepts.items():
            for concept_pattern in domain_concepts:
                if concept_pattern in text_lower:
                    concepts.add(f"{domain}:{concept_pattern}")
        
        # Extract technology relationships
        for tech, related_concepts in self.technology_relationships.items():
            if tech in text_lower:
                concepts.update(related_concepts)
        
        return list(concepts)
    
    def _extract_domain_context(
        self, 
        text: str, 
        requirements: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract domain context and expertise areas"""
        
        domains = {}
        text_lower = text.lower()
        
        # Define domain indicators
        domain_indicators = {
            'frontend': ['ui', 'frontend', 'client-side', 'browser', 'react', 'vue', 'angular'],
            'backend': ['api', 'server', 'backend', 'database', 'microservice'],
            'mobile': ['mobile', 'ios', 'android', 'react-native', 'flutter'],
            'data': ['data', 'analytics', 'ml', 'ai', 'machine learning'],
            'devops': ['deploy', 'ci/cd', 'docker', 'kubernetes', 'infrastructure'],
            'testing': ['test', 'testing', 'qa', 'unit test', 'integration'],
            'security': ['security', 'auth', 'encryption', 'secure', 'ssl']
        }
        
        # Score each domain
        for domain, indicators in domain_indicators.items():
            score = 0.0
            for indicator in indicators:
                if indicator in text_lower:
                    score += 0.2
                    
            # Boost from requirements
            if requirements:
                req_text = str(requirements).lower()
                for indicator in indicators:
                    if indicator in req_text:
                        score += 0.1
            
            if score > 0:
                domains[domain] = min(score, 1.0)
        
        return domains
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities and structured information"""
        
        entities = {
            'technologies': [],
            'frameworks': [],
            'languages': [],
            'platforms': []
        }
        
        text_lower = text.lower()
        
        # Technology entities
        technologies = [
            'react', 'vue', 'angular', 'svelte', 'node', 'express', 'fastapi',
            'django', 'flask', 'spring', 'laravel', 'ruby', 'rails'
        ]
        
        for tech in technologies:
            if tech in text_lower:
                entities['technologies'].append(tech)
        
        # Programming languages
        languages = [
            'javascript', 'typescript', 'python', 'java', 'go', 'rust',
            'c++', 'c#', 'php', 'ruby', 'kotlin', 'swift'
        ]
        
        for lang in languages:
            if lang in text_lower:
                entities['languages'].append(lang)
        
        # Platforms
        platforms = [
            'web', 'mobile', 'desktop', 'cloud', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'serverless'
        ]
        
        for platform in platforms:
            if platform in text_lower:
                entities['platforms'].append(platform)
        
        return entities
    
    def _analyze_query_complexity(
        self, 
        query_text: str, 
        terms: List[str]
    ) -> Dict[str, Any]:
        """Analyze query complexity and specificity"""
        
        return {
            'length': len(query_text),
            'term_count': len(terms),
            'specificity': self._calculate_query_specificity(query_text),
            'technical_level': self._calculate_technical_level(query_text),
            'clarity': self._calculate_query_clarity(query_text)
        }
    
    def _combine_component_text(self, component: Dict[str, Any]) -> str:
        """Combine all component text fields"""
        
        text_parts = []
        
        # Add weighted text fields
        if component.get('name'):
            text_parts.extend([component['name']] * 3)  # Name is most important
        
        if component.get('description'):
            text_parts.extend([component['description']] * 2)
        
        if component.get('tags'):
            text_parts.extend(component['tags'])
        
        if component.get('category'):
            text_parts.append(component['category'])
        
        if component.get('technology'):
            text_parts.append(component['technology'])
        
        if component.get('features'):
            text_parts.extend(component['features'])
        
        if component.get('documentation'):
            # Truncate long documentation
            doc_text = str(component['documentation'])[:500]
            text_parts.append(doc_text)
        
        return ' '.join(text_parts)
    
    def _extract_component_domain_info(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """Extract domain information from component"""
        
        domain_info = {
            'primary_domain': self._determine_primary_domain(component),
            'secondary_domains': self._determine_secondary_domains(component),
            'expertise_areas': self._determine_expertise_areas(component),
            'use_cases': self._determine_use_cases(component)
        }
        
        return domain_info
    
    def _extract_component_capabilities(self, component: Dict[str, Any]) -> List[str]:
        """Extract functional capabilities of component"""
        
        capabilities = []
        
        # From features
        if component.get('features'):
            capabilities.extend(component['features'])
        
        # From description analysis
        description = component.get('description', '').lower()
        
        capability_patterns = {
            'rendering': ['render', 'display', 'show', 'present'],
            'data_handling': ['data', 'process', 'transform', 'parse'],
            'communication': ['api', 'request', 'fetch', 'send', 'receive'],
            'storage': ['store', 'save', 'persist', 'cache'],
            'validation': ['validate', 'verify', 'check', 'ensure'],
            'authentication': ['auth', 'login', 'secure', 'protect'],
            'optimization': ['optimize', 'fast', 'efficient', 'performance'],
            'integration': ['integrate', 'connect', 'plugin', 'extend']
        }
        
        for capability, patterns in capability_patterns.items():
            if any(pattern in description for pattern in patterns):
                capabilities.append(capability)
        
        return capabilities
    
    def _extract_tech_characteristics(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical characteristics"""
        
        characteristics = {
            'complexity': self._assess_complexity(component),
            'maturity': self._assess_maturity(component),
            'performance_class': self._assess_performance_class(component),
            'maintenance_burden': self._assess_maintenance_burden(component),
            'learning_curve': self._assess_learning_curve(component)
        }
        
        return characteristics
    
    def _calculate_intent_similarity(
        self, 
        query_intents: Dict[str, float], 
        component_capabilities: List[str]
    ) -> float:
        """Calculate how well component matches query intent"""
        
        intent_matches = 0.0
        
        # Intent to capability mapping
        intent_capability_map = {
            'find_component': ['general_purpose', 'utility'],
            'build_feature': ['development', 'builder', 'generator'],
            'solve_problem': ['problem_solving', 'debugging', 'optimization'],
            'compare_options': ['analysis', 'comparison'],
            'learn_about': ['documentation', 'educational'],
            'recommend': ['recommendation', 'suggestion']
        }
        
        for intent, confidence in query_intents.items():
            if intent in intent_capability_map:
                required_capabilities = intent_capability_map[intent]
                capability_match = any(
                    cap in component_capabilities 
                    for cap in required_capabilities
                )
                
                if capability_match:
                    intent_matches += confidence
        
        return min(intent_matches, 1.0)
    
    def _calculate_concept_similarity(
        self, 
        query_concepts: List[str], 
        component_concepts: List[str]
    ) -> float:
        """Calculate concept overlap similarity"""
        
        if not query_concepts or not component_concepts:
            return 0.0
        
        # Direct concept matches
        direct_matches = set(query_concepts) & set(component_concepts)
        direct_score = len(direct_matches) / len(query_concepts)
        
        # Semantic concept matches
        semantic_matches = 0
        for q_concept in query_concepts:
            for c_concept in component_concepts:
                if self._are_concepts_related(q_concept, c_concept):
                    semantic_matches += 1
                    break
        
        semantic_score = semantic_matches / len(query_concepts)
        
        # Weighted combination
        return direct_score * 0.7 + semantic_score * 0.3
    
    def _calculate_domain_similarity(
        self, 
        query_domains: Dict[str, float], 
        component_domains: Dict[str, Any]
    ) -> float:
        """Calculate domain expertise similarity"""
        
        if not query_domains:
            return 0.5  # Neutral if no domain specified
        
        primary_domain = component_domains.get('primary_domain')
        secondary_domains = component_domains.get('secondary_domains', [])
        
        max_score = 0.0
        
        for domain, confidence in query_domains.items():
            score = 0.0
            
            if domain == primary_domain:
                score = confidence * 1.0
            elif domain in secondary_domains:
                score = confidence * 0.7
            elif self._are_domains_related(domain, primary_domain):
                score = confidence * 0.5
            
            max_score = max(max_score, score)
        
        return max_score
    
    def _calculate_contextual_relevance(
        self, 
        query_features: Dict[str, Any], 
        component_features: Dict[str, Any]
    ) -> float:
        """Calculate contextual relevance"""
        
        relevance_score = 0.0
        
        # Technical level alignment
        query_tech_level = query_features['analysis'].get('technical_level', 0.5)
        component_complexity = component_features['tech_characteristics'].get('complexity', 0.5)
        
        tech_alignment = 1.0 - abs(query_tech_level - component_complexity)
        relevance_score += tech_alignment * 0.3
        
        # Use case alignment
        query_entities = query_features.get('entities', {})
        component_use_cases = component_features['domain_info'].get('use_cases', [])
        
        use_case_match = 0.0
        for entity_type, entities in query_entities.items():
            for entity in entities:
                if entity in component_use_cases:
                    use_case_match += 0.2
        
        relevance_score += min(use_case_match, 1.0) * 0.4
        
        # Maturity preference
        component_maturity = component_features['tech_characteristics'].get('maturity', 0.5)
        maturity_bonus = component_maturity * 0.3
        relevance_score += maturity_bonus
        
        return min(relevance_score, 1.0)
    
    def _calculate_embedding_similarity(
        self, 
        query_embedding: List[float], 
        component_embedding: List[float]
    ) -> float:
        """Calculate cosine similarity between embeddings"""
        
        if not query_embedding or not component_embedding:
            return 0.0
        
        # Simple cosine similarity (in production, use proper vector operations)
        dot_product = sum(a * b for a, b in zip(query_embedding, component_embedding))
        
        query_magnitude = math.sqrt(sum(x * x for x in query_embedding))
        component_magnitude = math.sqrt(sum(x * x for x in component_embedding))
        
        if query_magnitude == 0 or component_magnitude == 0:
            return 0.0
        
        similarity = dot_product / (query_magnitude * component_magnitude)
        return max(0.0, similarity)  # Ensure non-negative
    
    def _calculate_exact_semantic_matches(
        self, 
        query_features: Dict[str, Any], 
        component_features: Dict[str, Any]
    ) -> float:
        """Calculate exact semantic matches"""
        
        matches = 0.0
        
        # Exact entity matches
        query_entities = query_features.get('entities', {})
        component_text = component_features['combined_text'].lower()
        
        for entity_type, entities in query_entities.items():
            for entity in entities:
                if entity in component_text:
                    matches += 0.3
        
        # Exact concept matches
        query_concepts = query_features.get('concepts', [])
        component_concepts = component_features.get('concepts', [])
        
        exact_concept_matches = set(query_concepts) & set(component_concepts)
        matches += len(exact_concept_matches) * 0.2
        
        return min(matches, 1.0)
    
    def _get_semantic_matches(
        self, 
        query_features: Dict[str, Any], 
        component_features: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get detailed semantic matches"""
        
        matches = []
        
        # Concept matches
        query_concepts = query_features.get('concepts', [])
        component_concepts = component_features.get('concepts', [])
        
        for q_concept in query_concepts:
            for c_concept in component_concepts:
                if q_concept == c_concept:
                    matches.append({
                        'type': 'exact_concept',
                        'query_item': q_concept,
                        'component_item': c_concept,
                        'similarity': 1.0
                    })
                elif self._are_concepts_related(q_concept, c_concept):
                    matches.append({
                        'type': 'related_concept',
                        'query_item': q_concept,
                        'component_item': c_concept,
                        'similarity': 0.7
                    })
        
        # Entity matches
        query_entities = query_features.get('entities', {})
        component_text = component_features['combined_text'].lower()
        
        for entity_type, entities in query_entities.items():
            for entity in entities:
                if entity in component_text:
                    matches.append({
                        'type': 'entity_match',
                        'entity_type': entity_type,
                        'entity': entity,
                        'similarity': 1.0
                    })
        
        return matches
    
    def _get_semantic_ranking_factors(
        self, 
        query_features: Dict[str, Any], 
        component_features: Dict[str, Any],
        similarity_score: float
    ) -> Dict[str, Any]:
        """Get semantic ranking factors for explanation"""
        
        return {
            'overall_semantic_similarity': similarity_score,
            'intent_alignment': self._calculate_intent_similarity(
                query_features['intent'], 
                component_features['capabilities']
            ),
            'concept_overlap': self._calculate_concept_similarity(
                query_features['concepts'], 
                component_features['concepts']
            ),
            'domain_expertise': self._calculate_domain_similarity(
                query_features['domain_context'], 
                component_features['domain_info']
            ),
            'contextual_fit': self._calculate_contextual_relevance(
                query_features, 
                component_features
            )
        }
    
    def _generate_text_embedding(self, text: str) -> List[float]:
        """Generate simple text embedding (in production, use real embeddings)"""
        
        # Simple hash-based embedding for demonstration
        words = text.lower().split()
        embedding_dim = 100
        embedding = [0.0] * embedding_dim
        
        for word in words:
            # Simple hash function
            word_hash = hash(word) % embedding_dim
            embedding[word_hash] += 1.0
        
        # Normalize
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def _build_word_relationships(self) -> Dict[str, List[str]]:
        """Build word relationship mappings"""
        
        return {
            'ui': ['interface', 'frontend', 'view', 'component', 'design'],
            'api': ['service', 'endpoint', 'rest', 'graphql', 'backend'],
            'database': ['storage', 'persistence', 'data', 'db', 'sql'],
            'fast': ['quick', 'rapid', 'speedy', 'efficient', 'optimized'],
            'secure': ['safe', 'protected', 'encrypted', 'auth', 'security'],
            'simple': ['easy', 'basic', 'straightforward', 'minimal', 'clean'],
            'modern': ['latest', 'current', 'new', 'contemporary', 'updated'],
            'responsive': ['mobile', 'adaptive', 'flexible', 'fluid']
        }
    
    def _build_concept_mappings(self) -> Dict[str, List[str]]:
        """Build concept to keyword mappings"""
        
        return {
            'user_interface': ['ui', 'interface', 'frontend', 'gui', 'view'],
            'data_processing': ['data', 'process', 'transform', 'parse', 'analyze'],
            'web_development': ['web', 'html', 'css', 'javascript', 'frontend'],
            'mobile_development': ['mobile', 'ios', 'android', 'app', 'native'],
            'performance': ['fast', 'optimized', 'efficient', 'speed', 'performance'],
            'security': ['secure', 'auth', 'encryption', 'safety', 'protection'],
            'testing': ['test', 'testing', 'qa', 'unit', 'integration'],
            'deployment': ['deploy', 'deployment', 'ci/cd', 'production', 'release']
        }
    
    def _build_synonym_weights(self) -> Dict[str, float]:
        """Build synonym importance weights"""
        
        return {
            'exact_match': 1.0,
            'strong_synonym': 0.9,
            'related_term': 0.7,
            'weak_relation': 0.5,
            'contextual_relation': 0.6
        }
    
    def _build_domain_concepts(self) -> Dict[str, List[str]]:
        """Build domain-specific concept mappings"""
        
        return {
            'frontend': ['component', 'react', 'vue', 'angular', 'css', 'html'],
            'backend': ['api', 'server', 'database', 'microservice', 'rest'],
            'mobile': ['ios', 'android', 'react-native', 'flutter', 'cordova'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'deployment', 'infrastructure'],
            'data': ['analytics', 'ml', 'ai', 'big data', 'visualization'],
            'security': ['authentication', 'authorization', 'encryption', 'ssl', 'oauth']
        }
    
    def _build_technology_relationships(self) -> Dict[str, List[str]]:
        """Build technology relationship mappings"""
        
        return {
            'react': ['jsx', 'components', 'hooks', 'redux', 'material-ui'],
            'vue': ['vuex', 'nuxt', 'composition-api', 'vue-router'],
            'angular': ['typescript', 'rxjs', 'angular-material', 'ngrx'],
            'node': ['express', 'npm', 'v8', 'event-loop'],
            'python': ['django', 'flask', 'fastapi', 'numpy', 'pandas'],
            'docker': ['containers', 'kubernetes', 'devops', 'microservices']
        }
    
    def _are_concepts_related(self, concept1: str, concept2: str) -> bool:
        """Check if two concepts are semantically related"""
        
        # Check direct relationships
        if concept1 in self.word_relationships:
            if concept2 in self.word_relationships[concept1]:
                return True
        
        if concept2 in self.word_relationships:
            if concept1 in self.word_relationships[concept2]:
                return True
        
        # Check concept mappings
        for concept, keywords in self.concept_mappings.items():
            if concept1 in keywords and concept2 in keywords:
                return True
        
        return False
    
    def _are_domains_related(self, domain1: str, domain2: str) -> bool:
        """Check if two domains are related"""
        
        related_domains = {
            'frontend': ['mobile', 'web'],
            'backend': ['api', 'data', 'devops'],
            'mobile': ['frontend', 'app'],
            'devops': ['backend', 'infrastructure'],
            'data': ['backend', 'analytics'],
            'security': ['backend', 'devops']
        }
        
        return domain2 in related_domains.get(domain1, [])
    
    def _calculate_query_specificity(self, query: str) -> float:
        """Calculate how specific the query is"""
        
        specificity_indicators = [
            'version', 'specific', 'exactly', 'must', 'require',
            'framework', 'library', 'tool', 'component'
        ]
        
        query_lower = query.lower()
        specificity_score = sum(
            0.2 for indicator in specificity_indicators
            if indicator in query_lower
        )
        
        # Length factor
        length_factor = min(len(query.split()) / 10, 1.0)
        
        return min(specificity_score + length_factor, 1.0)
    
    def _calculate_technical_level(self, query: str) -> float:
        """Calculate technical complexity level of query"""
        
        technical_terms = [
            'algorithm', 'architecture', 'implementation', 'optimization',
            'performance', 'scalability', 'microservices', 'api',
            'framework', 'library', 'integration', 'deployment'
        ]
        
        query_lower = query.lower()
        tech_score = sum(
            0.15 for term in technical_terms
            if term in query_lower
        )
        
        return min(tech_score, 1.0)
    
    def _calculate_query_clarity(self, query: str) -> float:
        """Calculate how clear and well-formed the query is"""
        
        # Basic clarity indicators
        has_verb = any(verb in query.lower() for verb in ['find', 'search', 'need', 'want', 'build', 'create'])
        has_object = any(obj in query.lower() for obj in ['component', 'library', 'tool', 'framework'])
        
        clarity_score = 0.0
        if has_verb:
            clarity_score += 0.3
        if has_object:
            clarity_score += 0.3
        
        # Length and structure
        word_count = len(query.split())
        if 3 <= word_count <= 15:  # Ideal length range
            clarity_score += 0.4
        
        return clarity_score
    
    def _determine_primary_domain(self, component: Dict[str, Any]) -> str:
        """Determine the primary domain of a component"""
        
        category = component.get('category', '').lower()
        technology = component.get('technology', '').lower()
        tags = [tag.lower() for tag in component.get('tags', [])]
        
        # Domain classification rules
        if 'ui' in category or 'frontend' in category:
            return 'frontend'
        elif 'api' in category or 'backend' in category:
            return 'backend'
        elif technology in ['react', 'vue', 'angular']:
            return 'frontend'
        elif technology in ['node', 'express', 'django', 'flask']:
            return 'backend'
        elif any(tag in ['mobile', 'ios', 'android'] for tag in tags):
            return 'mobile'
        else:
            return 'general'
    
    def _determine_secondary_domains(self, component: Dict[str, Any]) -> List[str]:
        """Determine secondary domains"""
        
        secondary_domains = []
        tags = [tag.lower() for tag in component.get('tags', [])]
        description = component.get('description', '').lower()
        
        domain_indicators = {
            'testing': ['test', 'testing', 'qa'],
            'performance': ['fast', 'optimized', 'performance'],
            'security': ['secure', 'auth', 'encryption'],
            'data': ['data', 'analytics', 'visualization']
        }
        
        for domain, indicators in domain_indicators.items():
            if any(indicator in description or indicator in tags for indicator in indicators):
                secondary_domains.append(domain)
        
        return secondary_domains
    
    def _determine_expertise_areas(self, component: Dict[str, Any]) -> List[str]:
        """Determine areas of expertise"""
        
        features = component.get('features', [])
        return [feature.lower() for feature in features]
    
    def _determine_use_cases(self, component: Dict[str, Any]) -> List[str]:
        """Determine potential use cases"""
        
        use_cases = []
        category = component.get('category', '').lower()
        description = component.get('description', '').lower()
        
        use_case_patterns = {
            'web_development': ['web', 'website', 'webapp'],
            'mobile_development': ['mobile', 'app', 'ios', 'android'],
            'data_visualization': ['chart', 'graph', 'visualization'],
            'form_handling': ['form', 'input', 'validation'],
            'authentication': ['auth', 'login', 'user', 'session'],
            'api_development': ['api', 'rest', 'endpoint', 'service']
        }
        
        for use_case, patterns in use_case_patterns.items():
            if any(pattern in description for pattern in patterns):
                use_cases.append(use_case)
        
        return use_cases
    
    def _assess_complexity(self, component: Dict[str, Any]) -> float:
        """Assess component complexity"""
        
        # Simple heuristics (in production, use more sophisticated metrics)
        features_count = len(component.get('features', []))
        description_length = len(component.get('description', ''))
        
        complexity = (features_count / 10) + (description_length / 1000)
        return min(complexity, 1.0)
    
    def _assess_maturity(self, component: Dict[str, Any]) -> float:
        """Assess component maturity"""
        
        # Use popularity and version as proxies for maturity
        popularity = component.get('popularity', 0) / 10
        
        # Check for version indicators
        version = component.get('version', '0.1.0')
        major_version = float(version.split('.')[0]) if version else 0
        
        version_maturity = min(major_version / 5, 1.0)
        
        return (popularity + version_maturity) / 2
    
    def _assess_performance_class(self, component: Dict[str, Any]) -> str:
        """Assess performance characteristics"""
        
        performance_score = component.get('performance_score', 5)
        
        if performance_score >= 8:
            return 'high_performance'
        elif performance_score >= 6:
            return 'good_performance'
        elif performance_score >= 4:
            return 'average_performance'
        else:
            return 'low_performance'
    
    def _assess_maintenance_burden(self, component: Dict[str, Any]) -> str:
        """Assess maintenance requirements"""
        
        recent_commits = component.get('recent_commits', 0)
        complexity = self._assess_complexity(component)
        
        if recent_commits > 20 or complexity > 0.8:
            return 'high_maintenance'
        elif recent_commits > 10 or complexity > 0.5:
            return 'medium_maintenance'
        else:
            return 'low_maintenance'
    
    def _assess_learning_curve(self, component: Dict[str, Any]) -> str:
        """Assess learning curve difficulty"""
        
        complexity = self._assess_complexity(component)
        documentation_quality = len(component.get('documentation', '')) / 1000
        
        difficulty_score = complexity - (documentation_quality * 0.3)
        
        if difficulty_score > 0.7:
            return 'steep'
        elif difficulty_score > 0.4:
            return 'moderate'
        else:
            return 'gentle'