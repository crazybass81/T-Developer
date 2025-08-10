"""
Constraint Analyzer Module
Analyzes and extracts constraints from requirements
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from enum import Enum
from collections import defaultdict


class ConstraintType(Enum):
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    TECHNICAL = "technical"
    REGULATORY = "regulatory"
    DATA = "data"
    UI = "ui"
    INTEGRATION = "integration"
    OPERATIONAL = "operational"


class ConstraintSeverity(Enum):
    MANDATORY = "mandatory"
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class ConstraintAnalyzer:
    """Analyzes constraints from requirements"""
    
    def __init__(self):
        # Constraint patterns
        self.constraint_patterns = {
            'numeric': {
                'patterns': [
                    r'(?:maximum|max|up to)\s+(\d+(?:\.\d+)?)\s*(\w+)',
                    r'(?:minimum|min|at least)\s+(\d+(?:\.\d+)?)\s*(\w+)',
                    r'(?:exactly|precisely)\s+(\d+(?:\.\d+)?)\s*(\w+)',
                    r'(\d+(?:\.\d+)?)\s*(\w+)\s+(?:limit|maximum|minimum)',
                    r'(?:less than|<)\s*(\d+(?:\.\d+)?)\s*(\w+)',
                    r'(?:greater than|>)\s*(\d+(?:\.\d+)?)\s*(\w+)',
                    r'(?:between)\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)\s*(\w+)'
                ],
                'type': 'numeric'
            },
            'temporal': {
                'patterns': [
                    r'(?:within|in)\s+(\d+)\s+(seconds?|minutes?|hours?|days?|weeks?|months?)',
                    r'(?:before|by)\s+([0-9]{1,2}:[0-9]{2}(?:\s*[AP]M)?)',
                    r'(?:after)\s+([0-9]{1,2}:[0-9]{2}(?:\s*[AP]M)?)',
                    r'(?:during)\s+(?:business hours|office hours|working hours)',
                    r'(?:response time|latency|timeout)\s*(?:of|:)?\s*(\d+)\s*(ms|milliseconds?|seconds?)',
                    r'(?:available|uptime)\s+(\d+(?:\.\d+)?)\s*%',
                    r'(?:deadline|due date|completion)\s+(?:is|by)\s+(.+)'
                ],
                'type': 'temporal'
            },
            'capacity': {
                'patterns': [
                    r'(?:support|handle)\s+(\d+)\s+(?:concurrent|simultaneous)\s+(\w+)',
                    r'(?:store|hold)\s+(?:up to)?\s*(\d+)\s+(\w+)',
                    r'(\d+)\s+(?:users?|connections?|requests?)\s+(?:per|/)\s+(\w+)',
                    r'(?:throughput|bandwidth)\s+(?:of)?\s*(\d+)\s*([KMGT]B/s)',
                    r'(?:capacity|size)\s+(?:of)?\s*(\d+)\s*([KMGT]B)',
                    r'(?:scale to|handle)\s+(\d+[KMB]?)\s+(\w+)'
                ],
                'type': 'capacity'
            },
            'quality': {
                'patterns': [
                    r'(?:accuracy|precision)\s+(?:of)?\s*(\d+(?:\.\d+)?)\s*%',
                    r'(?:error rate)\s+(?:less than|<)\s*(\d+(?:\.\d+)?)\s*%',
                    r'(?:availability|uptime)\s+(?:of)?\s*(\d+(?:\.\d+)?)\s*%',
                    r'(?:reliability)\s+(?:of)?\s*(\d+(?:\.\d+)?)\s*%',
                    r'(?:performance|quality)\s+(?:level|grade)\s+(\w+)'
                ],
                'type': 'quality'
            },
            'security': {
                'patterns': [
                    r'(?:encrypt|encryption)\s+(?:using|with)\s+(\w+)',
                    r'(?:authenticate|authentication)\s+(?:using|with|via)\s+(\w+)',
                    r'(?:comply with|compliant with|follow)\s+(\w+(?:\s+\w+)*)\s+(?:standard|regulation)',
                    r'(?:password)\s+(?:must be|minimum)\s+(\d+)\s+characters',
                    r'(?:session)\s+(?:timeout|expires?)\s+(?:after)?\s*(\d+)\s+(\w+)',
                    r'(?:audit|log)\s+(?:all)?\s*(\w+)\s+(?:actions|events|activities)'
                ],
                'type': 'security'
            },
            'compatibility': {
                'patterns': [
                    r'(?:compatible with|support)\s+(\w+(?:\s+\w+)*)',
                    r'(?:works? with|integrates? with)\s+(\w+(?:\s+\w+)*)',
                    r'(?:browser support|supports?)\s+(\w+(?:\s+\w+)*)',
                    r'(?:platform|OS)\s+(?:support|compatibility)\s+(?:for)?\s*(\w+(?:\s+\w+)*)',
                    r'(?:version|versions?)\s+(\d+(?:\.\d+)*)\s+(?:or higher|and above)'
                ],
                'type': 'compatibility'
            }
        }
        
        # Performance metrics
        self.performance_metrics = {
            'response_time': {'unit': 'ms', 'threshold': 1000},
            'throughput': {'unit': 'rps', 'threshold': 1000},
            'cpu_usage': {'unit': '%', 'threshold': 80},
            'memory_usage': {'unit': 'MB', 'threshold': 1024},
            'network_latency': {'unit': 'ms', 'threshold': 100},
            'database_queries': {'unit': 'queries/s', 'threshold': 100}
        }
        
        # Compliance standards
        self.compliance_standards = {
            'GDPR': 'General Data Protection Regulation',
            'HIPAA': 'Health Insurance Portability and Accountability Act',
            'PCI DSS': 'Payment Card Industry Data Security Standard',
            'SOC 2': 'Service Organization Control 2',
            'ISO 27001': 'Information Security Management',
            'WCAG': 'Web Content Accessibility Guidelines',
            'CCPA': 'California Consumer Privacy Act'
        }
    
    async def analyze(self, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze constraints from NLP processed text
        
        Args:
            nlp_result: NLP processing results
            
        Returns:
            Analyzed constraints
        """
        text = nlp_result.get('original', '')
        sentences = nlp_result.get('sentences', [])
        
        # Extract constraints by pattern
        pattern_constraints = self._extract_pattern_constraints(text)
        
        # Extract constraints from sentences
        sentence_constraints = self._extract_sentence_constraints(sentences)
        
        # Merge constraints
        all_constraints = self._merge_constraints(pattern_constraints, sentence_constraints)
        
        # Classify constraints
        classified = self._classify_constraints(all_constraints)
        
        # Analyze performance constraints
        performance = self._analyze_performance_constraints(classified)
        
        # Analyze security constraints
        security = self._analyze_security_constraints(classified)
        
        # Analyze business constraints
        business = self._analyze_business_constraints(classified)
        
        # Analyze compliance requirements
        compliance = self._analyze_compliance(text)
        
        # Generate validation rules
        validation_rules = self._generate_validation_rules(classified)
        
        # Identify conflicts
        conflicts = self._identify_conflicts(classified)
        
        # Calculate impact
        impact = self._calculate_impact(classified)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(classified)
        
        return {
            'constraints': classified,
            'performance': performance,
            'security': security,
            'business': business,
            'compliance': compliance,
            'validation_rules': validation_rules,
            'conflicts': conflicts,
            'impact': impact,
            'recommendations': recommendations,
            'statistics': self._calculate_statistics(classified)
        }
    
    def _extract_pattern_constraints(self, text: str) -> List[Dict]:
        """Extract constraints using patterns"""
        constraints = []
        
        for category, config in self.constraint_patterns.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    constraint = self._parse_constraint_match(match, config['type'])
                    if constraint:
                        constraints.append(constraint)
        
        return constraints
    
    def _parse_constraint_match(self, match: re.Match, constraint_type: str) -> Optional[Dict]:
        """Parse constraint from regex match"""
        groups = match.groups()
        
        if constraint_type == 'numeric':
            if len(groups) >= 2:
                return {
                    'type': constraint_type,
                    'value': float(groups[0]) if '.' in groups[0] else int(groups[0]),
                    'unit': groups[1] if len(groups) > 1 else None,
                    'operator': self._extract_operator(match.group(0)),
                    'text': match.group(0),
                    'position': match.span()
                }
        elif constraint_type == 'temporal':
            if groups:
                return {
                    'type': constraint_type,
                    'value': groups[0],
                    'unit': groups[1] if len(groups) > 1 else None,
                    'text': match.group(0),
                    'position': match.span()
                }
        elif constraint_type == 'capacity':
            if len(groups) >= 2:
                return {
                    'type': constraint_type,
                    'value': self._parse_capacity_value(groups[0]),
                    'resource': groups[1],
                    'text': match.group(0),
                    'position': match.span()
                }
        elif constraint_type == 'quality':
            if groups:
                return {
                    'type': constraint_type,
                    'metric': self._extract_metric_name(match.group(0)),
                    'value': groups[0],
                    'text': match.group(0),
                    'position': match.span()
                }
        elif constraint_type == 'security':
            if groups:
                return {
                    'type': constraint_type,
                    'requirement': groups[0],
                    'text': match.group(0),
                    'position': match.span()
                }
        elif constraint_type == 'compatibility':
            if groups:
                return {
                    'type': constraint_type,
                    'target': groups[0],
                    'text': match.group(0),
                    'position': match.span()
                }
        
        return None
    
    def _extract_operator(self, text: str) -> str:
        """Extract comparison operator from text"""
        text_lower = text.lower()
        
        if 'maximum' in text_lower or 'max' in text_lower or 'up to' in text_lower:
            return '<='
        elif 'minimum' in text_lower or 'min' in text_lower or 'at least' in text_lower:
            return '>='
        elif 'exactly' in text_lower or 'precisely' in text_lower:
            return '=='
        elif 'less than' in text_lower or '<' in text:
            return '<'
        elif 'greater than' in text_lower or '>' in text:
            return '>'
        elif 'between' in text_lower:
            return 'between'
        
        return '=='
    
    def _parse_capacity_value(self, value_str: str) -> int:
        """Parse capacity value with K/M/B suffixes"""
        value_str = value_str.upper()
        
        if value_str.endswith('K'):
            return int(float(value_str[:-1]) * 1000)
        elif value_str.endswith('M'):
            return int(float(value_str[:-1]) * 1000000)
        elif value_str.endswith('B'):
            return int(float(value_str[:-1]) * 1000000000)
        else:
            return int(float(value_str))
    
    def _extract_metric_name(self, text: str) -> str:
        """Extract metric name from text"""
        text_lower = text.lower()
        
        if 'accuracy' in text_lower or 'precision' in text_lower:
            return 'accuracy'
        elif 'error' in text_lower:
            return 'error_rate'
        elif 'availability' in text_lower or 'uptime' in text_lower:
            return 'availability'
        elif 'reliability' in text_lower:
            return 'reliability'
        elif 'performance' in text_lower:
            return 'performance'
        
        return 'quality'
    
    def _extract_sentence_constraints(self, sentences: List[str]) -> List[Dict]:
        """Extract constraints from individual sentences"""
        constraints = []
        
        for sentence in sentences:
            # Check for constraint keywords
            if self._is_constraint_sentence(sentence):
                constraint = self._parse_constraint_sentence(sentence)
                if constraint:
                    constraints.append(constraint)
        
        return constraints
    
    def _is_constraint_sentence(self, sentence: str) -> bool:
        """Check if sentence contains a constraint"""
        constraint_keywords = [
            'must', 'shall', 'should', 'require', 'limit', 'maximum', 'minimum',
            'within', 'before', 'after', 'less than', 'greater than', 'between',
            'constraint', 'restriction', 'boundary', 'threshold'
        ]
        
        sentence_lower = sentence.lower()
        return any(keyword in sentence_lower for keyword in constraint_keywords)
    
    def _parse_constraint_sentence(self, sentence: str) -> Optional[Dict]:
        """Parse constraint from sentence"""
        return {
            'type': 'general',
            'text': sentence,
            'severity': self._determine_severity(sentence),
            'category': self._determine_category(sentence)
        }
    
    def _determine_severity(self, text: str) -> str:
        """Determine constraint severity"""
        text_lower = text.lower()
        
        if 'must' in text_lower or 'shall' in text_lower or 'required' in text_lower:
            return ConstraintSeverity.MANDATORY.value
        elif 'should' in text_lower:
            return ConstraintSeverity.REQUIRED.value
        elif 'recommended' in text_lower:
            return ConstraintSeverity.RECOMMENDED.value
        elif 'may' in text_lower or 'optional' in text_lower:
            return ConstraintSeverity.OPTIONAL.value
        
        return ConstraintSeverity.REQUIRED.value
    
    def _determine_category(self, text: str) -> str:
        """Determine constraint category"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['performance', 'speed', 'latency', 'response']):
            return ConstraintType.PERFORMANCE.value
        elif any(word in text_lower for word in ['security', 'authentication', 'encryption', 'privacy']):
            return ConstraintType.SECURITY.value
        elif any(word in text_lower for word in ['business', 'rule', 'policy', 'process']):
            return ConstraintType.BUSINESS.value
        elif any(word in text_lower for word in ['technical', 'system', 'architecture', 'implementation']):
            return ConstraintType.TECHNICAL.value
        elif any(word in text_lower for word in ['compliance', 'regulation', 'standard', 'audit']):
            return ConstraintType.REGULATORY.value
        elif any(word in text_lower for word in ['data', 'database', 'storage', 'format']):
            return ConstraintType.DATA.value
        elif any(word in text_lower for word in ['ui', 'interface', 'display', 'layout']):
            return ConstraintType.UI.value
        elif any(word in text_lower for word in ['integration', 'api', 'interface', 'connect']):
            return ConstraintType.INTEGRATION.value
        
        return ConstraintType.OPERATIONAL.value
    
    def _merge_constraints(self, *constraint_lists) -> List[Dict]:
        """Merge and deduplicate constraints"""
        merged = []
        seen_texts = set()
        
        for constraint_list in constraint_lists:
            for constraint in constraint_list:
                text = constraint.get('text', '')
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    merged.append(constraint)
        
        return merged
    
    def _classify_constraints(self, constraints: List[Dict]) -> Dict[str, List[Dict]]:
        """Classify constraints by type"""
        classified = defaultdict(list)
        
        for constraint in constraints:
            # Enhance classification
            constraint['severity'] = constraint.get('severity', self._determine_severity(constraint.get('text', '')))
            constraint['category'] = constraint.get('category', self._determine_category(constraint.get('text', '')))
            
            # Group by category
            classified[constraint['category']].append(constraint)
        
        return dict(classified)
    
    def _analyze_performance_constraints(self, classified: Dict) -> Dict[str, Any]:
        """Analyze performance-specific constraints"""
        performance = {
            'response_time': [],
            'throughput': [],
            'capacity': [],
            'availability': [],
            'scalability': []
        }
        
        perf_constraints = classified.get(ConstraintType.PERFORMANCE.value, [])
        
        for constraint in perf_constraints:
            if 'response' in constraint.get('text', '').lower():
                performance['response_time'].append({
                    'value': constraint.get('value'),
                    'unit': constraint.get('unit', 'ms'),
                    'requirement': constraint.get('text')
                })
            elif 'throughput' in constraint.get('text', '').lower():
                performance['throughput'].append({
                    'value': constraint.get('value'),
                    'unit': constraint.get('unit', 'rps'),
                    'requirement': constraint.get('text')
                })
            elif 'capacity' in constraint.get('text', '').lower() or 'concurrent' in constraint.get('text', '').lower():
                performance['capacity'].append({
                    'value': constraint.get('value'),
                    'resource': constraint.get('resource', 'users'),
                    'requirement': constraint.get('text')
                })
            elif 'availability' in constraint.get('text', '').lower() or 'uptime' in constraint.get('text', '').lower():
                performance['availability'].append({
                    'value': constraint.get('value'),
                    'unit': '%',
                    'requirement': constraint.get('text')
                })
        
        # Add capacity constraints
        capacity_constraints = classified.get('capacity', [])
        for constraint in capacity_constraints:
            performance['scalability'].append({
                'value': constraint.get('value'),
                'resource': constraint.get('resource'),
                'requirement': constraint.get('text')
            })
        
        return performance
    
    def _analyze_security_constraints(self, classified: Dict) -> Dict[str, Any]:
        """Analyze security-specific constraints"""
        security = {
            'authentication': [],
            'authorization': [],
            'encryption': [],
            'audit': [],
            'compliance': []
        }
        
        sec_constraints = classified.get(ConstraintType.SECURITY.value, [])
        
        for constraint in sec_constraints:
            text_lower = constraint.get('text', '').lower()
            
            if 'authenticat' in text_lower:
                security['authentication'].append({
                    'method': constraint.get('requirement'),
                    'requirement': constraint.get('text')
                })
            elif 'authoriz' in text_lower or 'permission' in text_lower:
                security['authorization'].append({
                    'requirement': constraint.get('text')
                })
            elif 'encrypt' in text_lower:
                security['encryption'].append({
                    'algorithm': constraint.get('requirement'),
                    'requirement': constraint.get('text')
                })
            elif 'audit' in text_lower or 'log' in text_lower:
                security['audit'].append({
                    'requirement': constraint.get('text')
                })
            elif 'complian' in text_lower or 'standard' in text_lower:
                security['compliance'].append({
                    'standard': constraint.get('requirement'),
                    'requirement': constraint.get('text')
                })
        
        return security
    
    def _analyze_business_constraints(self, classified: Dict) -> Dict[str, Any]:
        """Analyze business-specific constraints"""
        business = {
            'rules': [],
            'policies': [],
            'processes': [],
            'sla': []
        }
        
        biz_constraints = classified.get(ConstraintType.BUSINESS.value, [])
        
        for constraint in biz_constraints:
            text_lower = constraint.get('text', '').lower()
            
            if 'rule' in text_lower:
                business['rules'].append({
                    'rule': constraint.get('text'),
                    'severity': constraint.get('severity')
                })
            elif 'policy' in text_lower:
                business['policies'].append({
                    'policy': constraint.get('text'),
                    'severity': constraint.get('severity')
                })
            elif 'process' in text_lower or 'workflow' in text_lower:
                business['processes'].append({
                    'process': constraint.get('text'),
                    'severity': constraint.get('severity')
                })
            elif 'sla' in text_lower or 'service level' in text_lower:
                business['sla'].append({
                    'requirement': constraint.get('text'),
                    'severity': constraint.get('severity')
                })
        
        return business
    
    def _analyze_compliance(self, text: str) -> Dict[str, Any]:
        """Analyze compliance requirements"""
        compliance = {
            'standards': [],
            'regulations': [],
            'certifications': []
        }
        
        text_upper = text.upper()
        
        # Check for known standards
        for standard, description in self.compliance_standards.items():
            if standard in text_upper:
                compliance['standards'].append({
                    'name': standard,
                    'description': description,
                    'mentioned': True
                })
        
        # Check for regulation keywords
        if any(word in text.lower() for word in ['regulation', 'regulatory', 'compliance']):
            compliance['regulations'].append({
                'type': 'general',
                'requirement': 'Regulatory compliance required'
            })
        
        # Check for certification requirements
        if any(word in text.lower() for word in ['certified', 'certification', 'accredited']):
            compliance['certifications'].append({
                'type': 'general',
                'requirement': 'Certification required'
            })
        
        return compliance
    
    def _generate_validation_rules(self, classified: Dict) -> List[Dict]:
        """Generate validation rules from constraints"""
        rules = []
        
        for category, constraints in classified.items():
            for constraint in constraints:
                rule = {
                    'category': category,
                    'type': constraint.get('type'),
                    'severity': constraint.get('severity'),
                    'rule': self._create_validation_rule(constraint)
                }
                
                if rule['rule']:
                    rules.append(rule)
        
        return rules
    
    def _create_validation_rule(self, constraint: Dict) -> Optional[Dict]:
        """Create validation rule from constraint"""
        if constraint.get('type') == 'numeric':
            return {
                'field': constraint.get('field', 'value'),
                'operator': constraint.get('operator', '<='),
                'value': constraint.get('value'),
                'unit': constraint.get('unit'),
                'message': f"Value must be {constraint.get('operator', '<=')} {constraint.get('value')} {constraint.get('unit', '')}"
            }
        elif constraint.get('type') == 'temporal':
            return {
                'field': 'time',
                'condition': 'within',
                'value': constraint.get('value'),
                'unit': constraint.get('unit'),
                'message': f"Must complete within {constraint.get('value')} {constraint.get('unit', '')}"
            }
        elif constraint.get('type') == 'capacity':
            return {
                'field': constraint.get('resource', 'resource'),
                'max': constraint.get('value'),
                'message': f"Maximum {constraint.get('value')} {constraint.get('resource', 'items')}"
            }
        
        return None
    
    def _identify_conflicts(self, classified: Dict) -> List[Dict]:
        """Identify conflicting constraints"""
        conflicts = []
        
        # Check for numeric conflicts
        for category, constraints in classified.items():
            numeric_constraints = [c for c in constraints if c.get('type') == 'numeric']
            
            for i, c1 in enumerate(numeric_constraints):
                for c2 in numeric_constraints[i+1:]:
                    if self._are_conflicting(c1, c2):
                        conflicts.append({
                            'constraint1': c1.get('text'),
                            'constraint2': c2.get('text'),
                            'type': 'numeric_conflict',
                            'resolution': 'Review and clarify requirements'
                        })
        
        return conflicts
    
    def _are_conflicting(self, c1: Dict, c2: Dict) -> bool:
        """Check if two constraints are conflicting"""
        # Simple check for numeric conflicts
        if c1.get('unit') == c2.get('unit'):
            op1 = c1.get('operator', '==')
            op2 = c2.get('operator', '==')
            val1 = c1.get('value', 0)
            val2 = c2.get('value', 0)
            
            # Check for impossible conditions
            if op1 == '<' and op2 == '>' and val1 <= val2:
                return True
            if op1 == '<=' and op2 == '>=' and val1 < val2:
                return True
        
        return False
    
    def _calculate_impact(self, classified: Dict) -> Dict[str, Any]:
        """Calculate impact of constraints"""
        impact = {
            'complexity': 'low',
            'cost': 'low',
            'time': 'low',
            'risk': 'low'
        }
        
        total_constraints = sum(len(constraints) for constraints in classified.values())
        
        # Calculate complexity
        if total_constraints > 20:
            impact['complexity'] = 'high'
        elif total_constraints > 10:
            impact['complexity'] = 'medium'
        
        # Check for high-impact categories
        if ConstraintType.SECURITY.value in classified:
            impact['risk'] = 'high'
            impact['cost'] = 'medium'
        
        if ConstraintType.REGULATORY.value in classified:
            impact['risk'] = 'high'
            impact['complexity'] = 'high'
        
        if ConstraintType.PERFORMANCE.value in classified:
            perf_constraints = classified[ConstraintType.PERFORMANCE.value]
            if any('real-time' in c.get('text', '').lower() for c in perf_constraints):
                impact['complexity'] = 'high'
                impact['cost'] = 'high'
        
        return impact
    
    def _generate_recommendations(self, classified: Dict) -> List[str]:
        """Generate recommendations based on constraints"""
        recommendations = []
        
        # Performance recommendations
        if ConstraintType.PERFORMANCE.value in classified:
            recommendations.append("Implement performance monitoring and profiling")
            recommendations.append("Consider caching strategies for improved response times")
            recommendations.append("Plan for load testing and performance optimization")
        
        # Security recommendations
        if ConstraintType.SECURITY.value in classified:
            recommendations.append("Conduct security assessment and threat modeling")
            recommendations.append("Implement comprehensive logging and audit trails")
            recommendations.append("Plan for security testing and vulnerability assessments")
        
        # Compliance recommendations
        if ConstraintType.REGULATORY.value in classified:
            recommendations.append("Engage compliance experts early in the project")
            recommendations.append("Document all compliance-related decisions")
            recommendations.append("Plan for regular compliance audits")
        
        # Scalability recommendations
        if any('scalab' in c.get('text', '').lower() for constraints in classified.values() for c in constraints):
            recommendations.append("Design for horizontal scalability from the start")
            recommendations.append("Implement proper load balancing and distribution")
            recommendations.append("Consider microservices architecture for better scalability")
        
        return recommendations
    
    def _calculate_statistics(self, classified: Dict) -> Dict[str, Any]:
        """Calculate constraint statistics"""
        total = sum(len(constraints) for constraints in classified.values())
        
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        
        for category, constraints in classified.items():
            type_counts[category] = len(constraints)
            
            for constraint in constraints:
                severity = constraint.get('severity', 'unknown')
                severity_counts[severity] += 1
        
        return {
            'total_constraints': total,
            'by_category': dict(type_counts),
            'by_severity': dict(severity_counts),
            'categories': list(classified.keys()),
            'high_priority': severity_counts.get(ConstraintSeverity.MANDATORY.value, 0)
        }