"""
Ambiguity Resolver Module
Detects and resolves ambiguous requirements in project descriptions
"""

from typing import Dict, List, Tuple, Optional
import re

class AmbiguityResolver:
    """Resolves ambiguities in project requirements"""
    
    def __init__(self):
        self.ambiguous_terms = {
            "size": {
                "small": ["small", "tiny", "minimal", "simple"],
                "medium": ["moderate", "average", "normal", "standard"],
                "large": ["big", "huge", "massive", "enterprise"],
                "clarification": "What scale of application are you building?"
            },
            "performance": {
                "fast": ["fast", "quick", "rapid", "speedy"],
                "efficient": ["efficient", "optimized", "performant"],
                "clarification": "What are your specific performance requirements?"
            },
            "users": {
                "few": ["few", "some", "several"],
                "many": ["many", "lots", "numerous"],
                "clarification": "How many concurrent users do you expect?"
            },
            "timeline": {
                "soon": ["soon", "quickly", "asap"],
                "later": ["later", "eventually", "future"],
                "clarification": "What is your target completion date?"
            },
            "features": {
                "basic": ["basic", "simple", "essential"],
                "advanced": ["advanced", "complex", "sophisticated"],
                "clarification": "Which specific features are must-haves vs nice-to-haves?"
            }
        }
        
        self.vague_phrases = [
            "user friendly",
            "easy to use",
            "modern design",
            "good performance",
            "secure",
            "scalable",
            "reliable",
            "flexible",
            "robust",
            "intuitive"
        ]
        
        self.clarification_templates = {
            "functionality": "Could you specify what '{term}' means in terms of specific features?",
            "performance": "What specific metrics define '{term}' for your use case?",
            "scale": "Can you provide numbers for '{term}'? (e.g., users, requests/second)",
            "timeline": "What is the specific timeframe for '{term}'?",
            "integration": "Which specific systems need to integrate with '{term}'?",
            "data": "What type and volume of data for '{term}'?",
            "security": "What security standards or compliance requirements for '{term}'?"
        }
        
        self.resolution_strategies = {
            "assumption": "Making educated assumption based on context",
            "default": "Using industry standard defaults",
            "clarification": "Requires user clarification",
            "inference": "Inferring from related requirements"
        }
    
    async def resolve(
        self,
        text: str,
        requirements: Dict[str, any],
        context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Detect and resolve ambiguities in requirements
        
        Args:
            text: Original project description
            requirements: Extracted requirements
            context: Additional context
            
        Returns:
            Resolution results with clarifications needed
        """
        
        # Detect ambiguities
        ambiguities = await self._detect_ambiguities(text, requirements)
        
        # Attempt automatic resolution
        resolutions = await self._attempt_resolutions(ambiguities, context)
        
        # Generate clarification questions
        clarifications = self._generate_clarifications(ambiguities, resolutions)
        
        # Apply resolutions to requirements
        resolved_requirements = self._apply_resolutions(requirements, resolutions)
        
        # Calculate clarity score
        clarity_score = self._calculate_clarity_score(ambiguities, resolutions)
        
        return {
            "ambiguities_detected": ambiguities,
            "resolutions": resolutions,
            "clarifications_needed": clarifications,
            "resolved_requirements": resolved_requirements,
            "clarity_score": clarity_score,
            "confidence_level": self._determine_confidence(clarity_score),
            "recommendations": self._generate_recommendations(ambiguities)
        }
    
    async def _detect_ambiguities(
        self,
        text: str,
        requirements: Dict[str, any]
    ) -> List[Dict]:
        """Detect ambiguous terms and phrases"""
        
        ambiguities = []
        text_lower = text.lower()
        
        # Check for ambiguous size/scale terms
        for category, terms_config in self.ambiguous_terms.items():
            for level, terms in terms_config.items():
                if level == "clarification":
                    continue
                    
                for term in terms:
                    if term in text_lower:
                        ambiguities.append({
                            "type": "ambiguous_term",
                            "category": category,
                            "term": term,
                            "severity": "medium",
                            "location": text_lower.index(term)
                        })
        
        # Check for vague phrases
        for phrase in self.vague_phrases:
            if phrase in text_lower:
                ambiguities.append({
                    "type": "vague_phrase",
                    "phrase": phrase,
                    "severity": "low",
                    "location": text_lower.index(phrase)
                })
        
        # Check for missing specifications
        missing = self._check_missing_specs(requirements)
        ambiguities.extend(missing)
        
        # Check for conflicting requirements
        conflicts = self._check_conflicts(requirements)
        ambiguities.extend(conflicts)
        
        # Check for unclear references
        unclear = self._check_unclear_references(text)
        ambiguities.extend(unclear)
        
        return ambiguities
    
    async def _attempt_resolutions(
        self,
        ambiguities: List[Dict],
        context: Optional[Dict]
    ) -> List[Dict]:
        """Attempt to automatically resolve ambiguities"""
        
        resolutions = []
        
        for ambiguity in ambiguities:
            resolution = None
            
            if ambiguity["type"] == "ambiguous_term":
                resolution = self._resolve_ambiguous_term(ambiguity, context)
            elif ambiguity["type"] == "vague_phrase":
                resolution = self._resolve_vague_phrase(ambiguity, context)
            elif ambiguity["type"] == "missing_spec":
                resolution = self._resolve_missing_spec(ambiguity, context)
            elif ambiguity["type"] == "conflict":
                resolution = self._resolve_conflict(ambiguity, context)
            elif ambiguity["type"] == "unclear_reference":
                resolution = self._resolve_unclear_reference(ambiguity, context)
            
            if resolution:
                resolutions.append(resolution)
        
        return resolutions
    
    def _resolve_ambiguous_term(self, ambiguity: Dict, context: Optional[Dict]) -> Dict:
        """Resolve ambiguous term based on context"""
        
        term = ambiguity["term"]
        category = ambiguity["category"]
        
        # Try to infer from context
        if context:
            if category == "size" and context.get("project_type"):
                project_type = context["project_type"]
                if project_type in ["enterprise", "saas"]:
                    resolved_value = "large"
                elif project_type in ["mvp", "prototype"]:
                    resolved_value = "small"
                else:
                    resolved_value = "medium"
                    
                return {
                    "ambiguity": ambiguity,
                    "strategy": "inference",
                    "resolved_value": resolved_value,
                    "confidence": 0.7
                }
        
        # Use defaults
        defaults = {
            "size": "medium",
            "performance": "standard",
            "users": "100-1000",
            "timeline": "3-6 months",
            "features": "core"
        }
        
        return {
            "ambiguity": ambiguity,
            "strategy": "default",
            "resolved_value": defaults.get(category, "standard"),
            "confidence": 0.5
        }
    
    def _resolve_vague_phrase(self, ambiguity: Dict, context: Optional[Dict]) -> Dict:
        """Resolve vague phrase with specific requirements"""
        
        phrase = ambiguity["phrase"]
        
        specific_requirements = {
            "user friendly": [
                "Intuitive navigation with < 3 clicks to any feature",
                "Clear visual hierarchy and consistent design",
                "Accessibility compliance (WCAG 2.1 AA)"
            ],
            "easy to use": [
                "Minimal learning curve for new users",
                "Context-sensitive help and tooltips",
                "Simplified workflows for common tasks"
            ],
            "modern design": [
                "Responsive design for all devices",
                "Contemporary UI patterns and components",
                "Clean, minimalist aesthetic"
            ],
            "good performance": [
                "Page load time < 3 seconds",
                "API response time < 500ms",
                "Support for 100+ concurrent users"
            ],
            "secure": [
                "HTTPS encryption for all communications",
                "Input validation and sanitization",
                "Role-based access control (RBAC)"
            ],
            "scalable": [
                "Horizontal scaling capability",
                "Microservices architecture where appropriate",
                "Database optimization and caching"
            ]
        }
        
        return {
            "ambiguity": ambiguity,
            "strategy": "assumption",
            "resolved_value": specific_requirements.get(phrase, ["Industry standard implementation"]),
            "confidence": 0.6
        }
    
    def _resolve_missing_spec(self, ambiguity: Dict, context: Optional[Dict]) -> Dict:
        """Resolve missing specification"""
        
        spec_type = ambiguity["spec_type"]
        
        defaults = {
            "database": "PostgreSQL for relational data",
            "authentication": "JWT-based authentication",
            "deployment": "Cloud deployment (AWS/GCP/Azure)",
            "testing": "Unit and integration testing",
            "monitoring": "Basic logging and error tracking"
        }
        
        return {
            "ambiguity": ambiguity,
            "strategy": "default",
            "resolved_value": defaults.get(spec_type, "Standard implementation"),
            "confidence": 0.5
        }
    
    def _resolve_conflict(self, ambiguity: Dict, context: Optional[Dict]) -> Dict:
        """Resolve conflicting requirements"""
        
        conflict = ambiguity["conflict"]
        
        # Prioritize based on common patterns
        priority_rules = {
            ("serverless", "stateful"): "Use managed state services (e.g., DynamoDB)",
            ("real-time", "batch"): "Implement both with different processing paths",
            ("simple", "advanced"): "Start simple with extensible architecture"
        }
        
        key = tuple(sorted(conflict))
        resolution = priority_rules.get(key, "Requires architectural decision")
        
        return {
            "ambiguity": ambiguity,
            "strategy": "clarification",
            "resolved_value": resolution,
            "confidence": 0.4
        }
    
    def _resolve_unclear_reference(self, ambiguity: Dict, context: Optional[Dict]) -> Dict:
        """Resolve unclear reference"""
        
        return {
            "ambiguity": ambiguity,
            "strategy": "clarification",
            "resolved_value": "Requires clarification",
            "confidence": 0.3
        }
    
    def _check_missing_specs(self, requirements: Dict) -> List[Dict]:
        """Check for missing specifications"""
        
        missing = []
        
        essential_specs = [
            "database",
            "authentication",
            "deployment",
            "testing",
            "monitoring"
        ]
        
        for spec in essential_specs:
            if not any(spec in str(req).lower() for req in requirements.values()):
                missing.append({
                    "type": "missing_spec",
                    "spec_type": spec,
                    "severity": "medium"
                })
        
        return missing
    
    def _check_conflicts(self, requirements: Dict) -> List[Dict]:
        """Check for conflicting requirements"""
        
        conflicts = []
        
        conflict_pairs = [
            ("serverless", "stateful"),
            ("real-time", "batch"),
            ("simple", "advanced"),
            ("monolithic", "microservices")
        ]
        
        req_text = str(requirements).lower()
        
        for pair in conflict_pairs:
            if all(term in req_text for term in pair):
                conflicts.append({
                    "type": "conflict",
                    "conflict": pair,
                    "severity": "high"
                })
        
        return conflicts
    
    def _check_unclear_references(self, text: str) -> List[Dict]:
        """Check for unclear references like 'it', 'this', 'that'"""
        
        unclear = []
        
        # Pattern for unclear references at sentence start
        pattern = r"(?:^|\. )(It|This|That|These|Those)\s+(?:should|must|will|can)"
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            unclear.append({
                "type": "unclear_reference",
                "reference": match.group(1),
                "context": match.group(0),
                "severity": "low",
                "location": match.start()
            })
        
        return unclear
    
    def _generate_clarifications(
        self,
        ambiguities: List[Dict],
        resolutions: List[Dict]
    ) -> List[Dict]:
        """Generate clarification questions for unresolved ambiguities"""
        
        clarifications = []
        resolved_ambiguities = {r["ambiguity"]["type"] + str(r["ambiguity"].get("term", ""))
                               for r in resolutions if r["confidence"] > 0.6}
        
        for ambiguity in ambiguities:
            ambig_key = ambiguity["type"] + str(ambiguity.get("term", ""))
            
            if ambig_key not in resolved_ambiguities:
                if ambiguity["type"] == "ambiguous_term":
                    question = self.ambiguous_terms[ambiguity["category"]]["clarification"]
                elif ambiguity["type"] == "vague_phrase":
                    question = f"Can you be more specific about what '{ambiguity['phrase']}' means for your project?"
                elif ambiguity["type"] == "missing_spec":
                    question = f"What are your requirements for {ambiguity['spec_type']}?"
                elif ambiguity["type"] == "conflict":
                    question = f"You mentioned both {ambiguity['conflict'][0]} and {ambiguity['conflict'][1]}. Which is the priority?"
                else:
                    question = "Could you provide more details about this requirement?"
                
                clarifications.append({
                    "question": question,
                    "context": ambiguity,
                    "priority": ambiguity.get("severity", "medium")
                })
        
        return clarifications
    
    def _apply_resolutions(
        self,
        requirements: Dict,
        resolutions: List[Dict]
    ) -> Dict:
        """Apply resolutions to requirements"""
        
        resolved = requirements.copy()
        
        for resolution in resolutions:
            if resolution["confidence"] > 0.5:
                # Add resolved values as additional requirements
                if "resolved_requirements" not in resolved:
                    resolved["resolved_requirements"] = []
                    
                resolved["resolved_requirements"].append({
                    "original": resolution["ambiguity"],
                    "resolved": resolution["resolved_value"],
                    "strategy": resolution["strategy"],
                    "confidence": resolution["confidence"]
                })
        
        return resolved
    
    def _calculate_clarity_score(
        self,
        ambiguities: List[Dict],
        resolutions: List[Dict]
    ) -> float:
        """Calculate overall clarity score"""
        
        if not ambiguities:
            return 1.0
        
        # Weight by severity
        severity_weights = {"high": 3, "medium": 2, "low": 1}
        total_weight = sum(severity_weights.get(a.get("severity", "medium"), 2) 
                          for a in ambiguities)
        
        # Calculate resolved weight
        resolved_weight = sum(severity_weights.get(r["ambiguity"].get("severity", "medium"), 2) * r["confidence"]
                            for r in resolutions)
        
        clarity = 1.0 - ((total_weight - resolved_weight) / (total_weight or 1))
        return max(0.0, min(1.0, clarity))
    
    def _determine_confidence(self, clarity_score: float) -> str:
        """Determine confidence level based on clarity score"""
        
        if clarity_score >= 0.8:
            return "high"
        elif clarity_score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, ambiguities: List[Dict]) -> List[str]:
        """Generate recommendations based on ambiguities"""
        
        recommendations = []
        
        if any(a["type"] == "ambiguous_term" for a in ambiguities):
            recommendations.append("Provide specific numbers and metrics where possible")
        
        if any(a["type"] == "vague_phrase" for a in ambiguities):
            recommendations.append("Define concrete acceptance criteria for qualitative requirements")
        
        if any(a["type"] == "missing_spec" for a in ambiguities):
            recommendations.append("Include technical specifications for all major components")
        
        if any(a["type"] == "conflict" for a in ambiguities):
            recommendations.append("Prioritize conflicting requirements or find architectural compromises")
        
        if len(ambiguities) > 5:
            recommendations.insert(0, "Consider creating a detailed requirements document")
        
        return recommendations