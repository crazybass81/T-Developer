"""
Requirement Analyzer Module
Analyzes and structures requirements from natural language
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from enum import Enum
from collections import defaultdict


class RequirementType(Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    BUSINESS = "business"
    TECHNICAL = "technical"
    USER = "user"
    SYSTEM = "system"
    INTERFACE = "interface"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    RELIABILITY = "reliability"
    COMPLIANCE = "compliance"


class RequirementPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NICE_TO_HAVE = "nice_to_have"


class RequirementAnalyzer:
    """Analyzes and structures requirements from text"""
    
    def __init__(self):
        # Requirement indicators
        self.requirement_keywords = {
            'mandatory': ['must', 'shall', 'required', 'mandatory', 'essential', 'critical'],
            'desired': ['should', 'ought', 'recommended', 'preferred', 'desired'],
            'optional': ['may', 'might', 'could', 'optional', 'nice to have'],
            'prohibited': ['must not', 'shall not', 'cannot', 'forbidden', 'prohibited']
        }
        
        # Requirement patterns
        self.requirement_patterns = {
            'user_story': r'as a\s+(.+?),?\s+i\s+(?:want|need)\s+(.+?)\s+so\s+that\s+(.+)',
            'given_when_then': r'given\s+(.+?)\s+when\s+(.+?)\s+then\s+(.+)',
            'feature': r'(?:feature|capability):\s*(.+)',
            'constraint': r'(?:constraint|limitation):\s*(.+)',
            'assumption': r'(?:assume|assuming|assumption):\s*(.+)',
            'dependency': r'(?:depends on|dependent on|requires):\s*(.+)'
        }
        
        # Functional requirement indicators
        self.functional_indicators = [
            'create', 'read', 'update', 'delete', 'search', 'filter', 'sort',
            'display', 'show', 'hide', 'enable', 'disable', 'calculate', 'process',
            'validate', 'submit', 'save', 'load', 'export', 'import', 'generate',
            'send', 'receive', 'notify', 'alert', 'authenticate', 'authorize'
        ]
        
        # Non-functional categories
        self.nfr_categories = {
            'performance': ['fast', 'quick', 'speed', 'response time', 'latency', 'throughput'],
            'security': ['secure', 'encrypt', 'authentication', 'authorization', 'access control'],
            'usability': ['easy', 'intuitive', 'user-friendly', 'accessible', 'simple'],
            'reliability': ['reliable', 'available', 'uptime', 'fault-tolerant', 'backup'],
            'scalability': ['scalable', 'scale', 'concurrent users', 'load', 'growth'],
            'compatibility': ['compatible', 'support', 'cross-platform', 'browser', 'device'],
            'maintainability': ['maintainable', 'modular', 'documented', 'testable']
        }
        
        # Acceptance criteria patterns
        self.acceptance_patterns = {
            'verification': r'verify\s+that\s+(.+)',
            'validation': r'validate\s+that\s+(.+)',
            'confirmation': r'confirm\s+that\s+(.+)',
            'checking': r'check\s+that\s+(.+)',
            'ensuring': r'ensure\s+that\s+(.+)'
        }
    
    async def analyze(
        self,
        nlp_result: Dict[str, Any],
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze requirements from NLP processed text
        
        Args:
            nlp_result: NLP processing results
            entities: Extracted entities
            
        Returns:
            Analyzed requirements
        """
        text = nlp_result.get('original', '')
        sentences = nlp_result.get('sentences', [])
        
        # Extract requirements from sentences
        requirements = []
        
        for sentence in sentences:
            # Check if sentence contains requirement
            if self._is_requirement(sentence):
                req = await self._analyze_requirement(sentence, entities)
                if req:
                    requirements.append(req)
        
        # Extract user stories
        user_stories = self._extract_user_stories(text)
        requirements.extend(user_stories)
        
        # Extract acceptance criteria
        acceptance_criteria = self._extract_acceptance_criteria(text)
        
        # Group requirements
        grouped = self._group_requirements(requirements)
        
        # Prioritize requirements
        prioritized = self._prioritize_requirements(requirements)
        
        # Identify dependencies
        dependencies = self._identify_dependencies(requirements)
        
        # Validate requirements
        validation = self._validate_requirements(requirements)
        
        # Generate requirement specifications
        specifications = self._generate_specifications(requirements)
        
        # Create traceability matrix
        traceability = self._create_traceability_matrix(requirements, entities)
        
        return {
            'requirements': prioritized,
            'user_stories': user_stories,
            'acceptance_criteria': acceptance_criteria,
            'grouped': grouped,
            'dependencies': dependencies,
            'validation': validation,
            'specifications': specifications,
            'traceability': traceability,
            'statistics': self._calculate_statistics(requirements)
        }
    
    def _is_requirement(self, sentence: str) -> bool:
        """Check if sentence contains a requirement"""
        sentence_lower = sentence.lower()
        
        # Check for requirement keywords
        for keywords in self.requirement_keywords.values():
            if any(keyword in sentence_lower for keyword in keywords):
                return True
        
        # Check for functional indicators
        if any(indicator in sentence_lower for indicator in self.functional_indicators):
            return True
        
        return False
    
    async def _analyze_requirement(
        self,
        sentence: str,
        entities: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze a single requirement"""
        requirement = {
            'text': sentence,
            'type': self._classify_requirement_type(sentence),
            'priority': self._determine_priority(sentence),
            'category': self._categorize_requirement(sentence),
            'entities': self._extract_requirement_entities(sentence, entities),
            'attributes': {},
            'metadata': {}
        }
        
        # Extract modal verb
        requirement['modal'] = self._extract_modal(sentence)
        
        # Extract action
        requirement['action'] = self._extract_action(sentence)
        
        # Extract subject and object
        requirement['subject'] = self._extract_subject(sentence)
        requirement['object'] = self._extract_object(sentence)
        
        # Extract conditions
        requirement['conditions'] = self._extract_conditions(sentence)
        
        # Extract constraints
        requirement['constraints'] = self._extract_constraints(sentence)
        
        # Generate ID
        requirement['id'] = self._generate_requirement_id(requirement)
        
        # Analyze complexity
        requirement['complexity'] = self._analyze_complexity(sentence)
        
        # Extract metrics
        requirement['metrics'] = self._extract_metrics(sentence)
        
        return requirement
    
    def _classify_requirement_type(self, text: str) -> str:
        """Classify the type of requirement"""
        text_lower = text.lower()
        
        # Check for non-functional indicators
        for category, indicators in self.nfr_categories.items():
            if any(indicator in text_lower for indicator in indicators):
                return RequirementType.NON_FUNCTIONAL.value
        
        # Check for functional indicators
        if any(indicator in text_lower for indicator in self.functional_indicators):
            return RequirementType.FUNCTIONAL.value
        
        # Check for business rules
        if any(word in text_lower for word in ['business', 'rule', 'policy']):
            return RequirementType.BUSINESS.value
        
        # Check for technical requirements
        if any(word in text_lower for word in ['technical', 'implementation', 'architecture']):
            return RequirementType.TECHNICAL.value
        
        # Check for interface requirements
        if any(word in text_lower for word in ['interface', 'api', 'integration']):
            return RequirementType.INTERFACE.value
        
        return RequirementType.FUNCTIONAL.value
    
    def _determine_priority(self, text: str) -> str:
        """Determine requirement priority"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'essential', 'vital']):
            return RequirementPriority.CRITICAL.value
        elif any(word in text_lower for word in ['must', 'shall', 'required']):
            return RequirementPriority.HIGH.value
        elif any(word in text_lower for word in ['should', 'recommended']):
            return RequirementPriority.MEDIUM.value
        elif any(word in text_lower for word in ['could', 'may', 'might']):
            return RequirementPriority.LOW.value
        elif any(word in text_lower for word in ['nice to have', 'optional']):
            return RequirementPriority.NICE_TO_HAVE.value
        
        return RequirementPriority.MEDIUM.value
    
    def _categorize_requirement(self, text: str) -> str:
        """Categorize requirement into functional area"""
        text_lower = text.lower()
        
        categories = {
            'authentication': ['login', 'logout', 'authenticate', 'password'],
            'authorization': ['permission', 'role', 'access', 'authorize'],
            'data_management': ['create', 'read', 'update', 'delete', 'crud'],
            'reporting': ['report', 'export', 'dashboard', 'analytics'],
            'notification': ['notify', 'alert', 'email', 'message'],
            'search': ['search', 'find', 'filter', 'query'],
            'integration': ['integrate', 'api', 'sync', 'connect'],
            'ui': ['display', 'show', 'interface', 'screen', 'page'],
            'workflow': ['process', 'workflow', 'approve', 'reject'],
            'validation': ['validate', 'verify', 'check', 'ensure']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _extract_requirement_entities(
        self,
        text: str,
        entities: Dict[str, Any]
    ) -> List[str]:
        """Extract entities mentioned in requirement"""
        mentioned_entities = []
        text_lower = text.lower()
        
        # Check all entity categories
        for category, entity_list in entities.get('entities', {}).items():
            for entity in entity_list:
                if entity['text'].lower() in text_lower:
                    mentioned_entities.append(entity['text'])
        
        return mentioned_entities
    
    def _extract_modal(self, text: str) -> Optional[str]:
        """Extract modal verb from requirement"""
        modals = ['must', 'shall', 'should', 'could', 'would', 'may', 'might', 'will', 'can']
        text_lower = text.lower()
        
        for modal in modals:
            if modal in text_lower:
                return modal
        
        return None
    
    def _extract_action(self, text: str) -> Optional[str]:
        """Extract main action from requirement"""
        # Simple extraction of verb
        for indicator in self.functional_indicators:
            if indicator in text.lower():
                return indicator
        
        return None
    
    def _extract_subject(self, text: str) -> Optional[str]:
        """Extract subject of requirement"""
        # Pattern: [Subject] must/should [action]
        pattern = r'^(\w+(?:\s+\w+)*?)\s+(?:must|shall|should|can|may)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        return None
    
    def _extract_object(self, text: str) -> Optional[str]:
        """Extract object of requirement"""
        # Pattern: [action] [object]
        for action in self.functional_indicators:
            pattern = f'{action}\\s+([a-zA-Z]+(?:\\s+[a-zA-Z]+)*)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_conditions(self, text: str) -> List[str]:
        """Extract conditions from requirement"""
        conditions = []
        
        # Conditional patterns
        patterns = [
            r'if\s+(.+?)(?:then|,)',
            r'when\s+(.+?)(?:then|,)',
            r'where\s+(.+?)(?:then|,)',
            r'provided\s+that\s+(.+)',
            r'given\s+that\s+(.+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                conditions.append(match.group(1).strip())
        
        return conditions
    
    def _extract_constraints(self, text: str) -> List[Dict[str, Any]]:
        """Extract constraints from requirement"""
        constraints = []
        
        # Numeric constraints
        numeric_pattern = r'(\d+)\s*(?:seconds?|minutes?|hours?|days?|users?|items?|characters?|bytes?|MB|GB)'
        matches = re.finditer(numeric_pattern, text, re.IGNORECASE)
        for match in matches:
            constraints.append({
                'type': 'numeric',
                'value': match.group(1),
                'unit': match.group(0).replace(match.group(1), '').strip()
            })
        
        # Range constraints
        range_pattern = r'between\s+(\d+)\s+and\s+(\d+)'
        matches = re.finditer(range_pattern, text, re.IGNORECASE)
        for match in matches:
            constraints.append({
                'type': 'range',
                'min': match.group(1),
                'max': match.group(2)
            })
        
        return constraints
    
    def _generate_requirement_id(self, requirement: Dict) -> str:
        """Generate unique ID for requirement"""
        import hashlib
        
        # Create ID based on content
        content = f"{requirement['type']}_{requirement['text']}"
        hash_obj = hashlib.md5(content.encode())
        short_hash = hash_obj.hexdigest()[:8]
        
        # Format: REQ-[TYPE]-[HASH]
        type_abbr = {
            'functional': 'FR',
            'non_functional': 'NFR',
            'business': 'BR',
            'technical': 'TR',
            'user': 'UR',
            'system': 'SR'
        }
        
        prefix = type_abbr.get(requirement['type'], 'REQ')
        return f"{prefix}-{short_hash.upper()}"
    
    def _analyze_complexity(self, text: str) -> str:
        """Analyze requirement complexity"""
        # Simple heuristic based on length and conditions
        word_count = len(text.split())
        condition_count = len(self._extract_conditions(text))
        
        if word_count > 50 or condition_count > 2:
            return 'high'
        elif word_count > 25 or condition_count > 0:
            return 'medium'
        else:
            return 'low'
    
    def _extract_metrics(self, text: str) -> List[Dict[str, Any]]:
        """Extract measurable metrics from requirement"""
        metrics = []
        
        # Performance metrics
        perf_pattern = r'(\d+)\s*(ms|milliseconds?|seconds?|minutes?)\s*(?:response time|latency)?'
        matches = re.finditer(perf_pattern, text, re.IGNORECASE)
        for match in matches:
            metrics.append({
                'type': 'performance',
                'value': match.group(1),
                'unit': match.group(2),
                'metric': 'response_time'
            })
        
        # Availability metrics
        avail_pattern = r'(\d+(?:\.\d+)?)\s*%\s*(?:availability|uptime)'
        matches = re.finditer(avail_pattern, text, re.IGNORECASE)
        for match in matches:
            metrics.append({
                'type': 'availability',
                'value': match.group(1),
                'unit': '%',
                'metric': 'uptime'
            })
        
        return metrics
    
    def _extract_user_stories(self, text: str) -> List[Dict[str, Any]]:
        """Extract user stories from text"""
        stories = []
        
        pattern = self.requirement_patterns['user_story']
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            story = {
                'type': 'user_story',
                'actor': match.group(1).strip(),
                'action': match.group(2).strip(),
                'benefit': match.group(3).strip(),
                'text': match.group(0),
                'priority': RequirementPriority.MEDIUM.value
            }
            stories.append(story)
        
        return stories
    
    def _extract_acceptance_criteria(self, text: str) -> List[Dict[str, Any]]:
        """Extract acceptance criteria"""
        criteria = []
        
        for name, pattern in self.acceptance_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                criteria.append({
                    'type': name,
                    'criterion': match.group(1).strip(),
                    'text': match.group(0)
                })
        
        # Extract Given-When-Then scenarios
        gwt_pattern = self.requirement_patterns['given_when_then']
        matches = re.finditer(gwt_pattern, text, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            criteria.append({
                'type': 'scenario',
                'given': match.group(1).strip(),
                'when': match.group(2).strip(),
                'then': match.group(3).strip(),
                'text': match.group(0)
            })
        
        return criteria
    
    def _group_requirements(self, requirements: List[Dict]) -> Dict[str, List[Dict]]:
        """Group requirements by various criteria"""
        grouped = {
            'by_type': defaultdict(list),
            'by_priority': defaultdict(list),
            'by_category': defaultdict(list),
            'by_complexity': defaultdict(list)
        }
        
        for req in requirements:
            grouped['by_type'][req.get('type', 'unknown')].append(req)
            grouped['by_priority'][req.get('priority', 'unknown')].append(req)
            grouped['by_category'][req.get('category', 'unknown')].append(req)
            grouped['by_complexity'][req.get('complexity', 'unknown')].append(req)
        
        return {k: dict(v) for k, v in grouped.items()}
    
    def _prioritize_requirements(self, requirements: List[Dict]) -> List[Dict]:
        """Prioritize requirements"""
        priority_order = {
            RequirementPriority.CRITICAL.value: 0,
            RequirementPriority.HIGH.value: 1,
            RequirementPriority.MEDIUM.value: 2,
            RequirementPriority.LOW.value: 3,
            RequirementPriority.NICE_TO_HAVE.value: 4
        }
        
        return sorted(
            requirements,
            key=lambda x: priority_order.get(x.get('priority', 'medium'), 2)
        )
    
    def _identify_dependencies(self, requirements: List[Dict]) -> List[Dict]:
        """Identify dependencies between requirements"""
        dependencies = []
        
        for i, req1 in enumerate(requirements):
            for j, req2 in enumerate(requirements):
                if i != j:
                    # Check if req2 mentions entities from req1
                    req1_entities = set(req1.get('entities', []))
                    req2_text = req2.get('text', '').lower()
                    
                    for entity in req1_entities:
                        if entity.lower() in req2_text:
                            dependencies.append({
                                'from': req1.get('id', i),
                                'to': req2.get('id', j),
                                'type': 'entity_reference',
                                'strength': 'weak'
                            })
                    
                    # Check for explicit dependencies
                    if 'after' in req2_text or 'before' in req2_text:
                        dependencies.append({
                            'from': req1.get('id', i),
                            'to': req2.get('id', j),
                            'type': 'temporal',
                            'strength': 'strong'
                        })
        
        return dependencies
    
    def _validate_requirements(self, requirements: List[Dict]) -> Dict[str, Any]:
        """Validate requirements for completeness and consistency"""
        validation = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'suggestions': []
        }
        
        for req in requirements:
            # Check completeness
            if not req.get('action'):
                validation['warnings'].append(f"Requirement '{req.get('id')}' lacks clear action")
            
            if not req.get('subject'):
                validation['warnings'].append(f"Requirement '{req.get('id')}' lacks clear subject")
            
            # Check for ambiguity
            ambiguous_terms = ['appropriate', 'adequate', 'as needed', 'etc', 'various']
            req_text = req.get('text', '').lower()
            for term in ambiguous_terms:
                if term in req_text:
                    validation['warnings'].append(
                        f"Requirement '{req.get('id')}' contains ambiguous term: {term}"
                    )
            
            # Check for testability
            if req.get('type') == 'non_functional' and not req.get('metrics'):
                validation['suggestions'].append(
                    f"Non-functional requirement '{req.get('id')}' should have measurable metrics"
                )
        
        validation['valid'] = len(validation['issues']) == 0
        
        return validation
    
    def _generate_specifications(self, requirements: List[Dict]) -> Dict[str, Any]:
        """Generate requirement specifications"""
        specs = {
            'functional_specs': [],
            'technical_specs': [],
            'test_cases': []
        }
        
        for req in requirements:
            if req.get('type') == 'functional':
                specs['functional_specs'].append({
                    'id': req.get('id'),
                    'description': req.get('text'),
                    'inputs': self._identify_inputs(req),
                    'outputs': self._identify_outputs(req),
                    'processing': req.get('action'),
                    'validation': req.get('constraints', [])
                })
            
            # Generate test cases
            specs['test_cases'].append({
                'requirement_id': req.get('id'),
                'test_description': f"Verify {req.get('action', 'requirement')}",
                'preconditions': req.get('conditions', []),
                'steps': [],
                'expected_result': 'Requirement satisfied'
            })
        
        return specs
    
    def _identify_inputs(self, requirement: Dict) -> List[str]:
        """Identify inputs for a requirement"""
        inputs = []
        text = requirement.get('text', '').lower()
        
        input_keywords = ['input', 'enter', 'provide', 'submit', 'upload', 'select']
        for keyword in input_keywords:
            if keyword in text:
                # Extract what follows the keyword
                pattern = f'{keyword}\\s+([a-zA-Z]+(?:\\s+[a-zA-Z]+)*)'
                match = re.search(pattern, text)
                if match:
                    inputs.append(match.group(1))
        
        return inputs
    
    def _identify_outputs(self, requirement: Dict) -> List[str]:
        """Identify outputs for a requirement"""
        outputs = []
        text = requirement.get('text', '').lower()
        
        output_keywords = ['display', 'show', 'return', 'generate', 'produce', 'output']
        for keyword in output_keywords:
            if keyword in text:
                # Extract what follows the keyword
                pattern = f'{keyword}\\s+([a-zA-Z]+(?:\\s+[a-zA-Z]+)*)'
                match = re.search(pattern, text)
                if match:
                    outputs.append(match.group(1))
        
        return outputs
    
    def _create_traceability_matrix(
        self,
        requirements: List[Dict],
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create requirement traceability matrix"""
        matrix = {
            'requirements_to_entities': defaultdict(list),
            'entities_to_requirements': defaultdict(list),
            'requirements_to_components': defaultdict(list)
        }
        
        for req in requirements:
            req_id = req.get('id')
            
            # Map to entities
            for entity in req.get('entities', []):
                matrix['requirements_to_entities'][req_id].append(entity)
                matrix['entities_to_requirements'][entity].append(req_id)
            
            # Map to components (based on category)
            category = req.get('category')
            if category:
                matrix['requirements_to_components'][req_id].append(category)
        
        return dict(matrix)
    
    def _calculate_statistics(self, requirements: List[Dict]) -> Dict[str, Any]:
        """Calculate requirement statistics"""
        if not requirements:
            return {
                'total': 0,
                'by_type': {},
                'by_priority': {},
                'complexity_distribution': {}
            }
        
        stats = {
            'total': len(requirements),
            'by_type': defaultdict(int),
            'by_priority': defaultdict(int),
            'by_category': defaultdict(int),
            'complexity_distribution': defaultdict(int),
            'average_complexity': 0
        }
        
        complexity_scores = {'low': 1, 'medium': 2, 'high': 3}
        total_complexity = 0
        
        for req in requirements:
            stats['by_type'][req.get('type', 'unknown')] += 1
            stats['by_priority'][req.get('priority', 'unknown')] += 1
            stats['by_category'][req.get('category', 'unknown')] += 1
            
            complexity = req.get('complexity', 'medium')
            stats['complexity_distribution'][complexity] += 1
            total_complexity += complexity_scores.get(complexity, 2)
        
        stats['average_complexity'] = total_complexity / len(requirements)
        
        return dict(stats)