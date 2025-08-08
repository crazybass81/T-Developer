"""
Intent Analyzer Module
Analyzes user intent from natural language description
"""

from typing import Dict, List, Optional
import re

class IntentAnalyzer:
    """Analyzes and classifies user intent from project descriptions"""
    
    def __init__(self):
        self.intent_patterns = {
            "create_new": {
                "patterns": [
                    r"create\s+(?:a\s+)?new",
                    r"build\s+(?:a\s+)?new",
                    r"develop\s+(?:a\s+)?new",
                    r"start\s+(?:a\s+)?new",
                    r"from\s+scratch",
                    r"greenfield"
                ],
                "confidence": 0.9
            },
            "migrate_existing": {
                "patterns": [
                    r"migrate\s+(?:from|to)",
                    r"convert\s+(?:from|to)",
                    r"port\s+(?:from|to)",
                    r"modernize",
                    r"upgrade\s+(?:from|to)",
                    r"legacy\s+migration"
                ],
                "confidence": 0.85
            },
            "enhance_existing": {
                "patterns": [
                    r"add\s+(?:feature|functionality)",
                    r"enhance",
                    r"improve",
                    r"extend",
                    r"augment",
                    r"optimize"
                ],
                "confidence": 0.8
            },
            "replace_system": {
                "patterns": [
                    r"replace\s+(?:existing|current|old)",
                    r"redesign",
                    r"rebuild",
                    r"rewrite",
                    r"overhaul"
                ],
                "confidence": 0.85
            },
            "integrate_systems": {
                "patterns": [
                    r"integrate\s+with",
                    r"connect\s+to",
                    r"sync\s+with",
                    r"interface\s+with",
                    r"bridge\s+between"
                ],
                "confidence": 0.8
            },
            "automate_process": {
                "patterns": [
                    r"automate",
                    r"streamline",
                    r"workflow\s+automation",
                    r"process\s+automation",
                    r"reduce\s+manual"
                ],
                "confidence": 0.85
            },
            "prototype_mvp": {
                "patterns": [
                    r"prototype",
                    r"mvp",
                    r"proof\s+of\s+concept",
                    r"poc",
                    r"demo",
                    r"pilot"
                ],
                "confidence": 0.9
            }
        }
        
        self.action_verbs = {
            "creation": ["create", "build", "develop", "make", "construct", "design", "implement"],
            "modification": ["modify", "update", "change", "alter", "revise", "edit", "adjust"],
            "analysis": ["analyze", "examine", "evaluate", "assess", "review", "investigate"],
            "optimization": ["optimize", "improve", "enhance", "boost", "accelerate", "streamline"],
            "integration": ["integrate", "connect", "link", "combine", "merge", "unify"],
            "automation": ["automate", "orchestrate", "schedule", "trigger", "execute"]
        }
        
        self.urgency_indicators = {
            "high": ["asap", "urgent", "immediately", "critical", "priority", "rush"],
            "medium": ["soon", "quickly", "timely", "prompt"],
            "low": ["eventually", "when possible", "future", "planned"]
        }
    
    async def analyze(self, text: str) -> Dict[str, any]:
        """
        Analyze user intent from text
        
        Args:
            text: Natural language description
            
        Returns:
            Dictionary containing intent analysis
        """
        
        text_lower = text.lower()
        
        # Identify primary intent
        primary_intent = self._identify_primary_intent(text_lower)
        
        # Extract action verbs
        actions = self._extract_actions(text_lower)
        
        # Determine urgency
        urgency = self._determine_urgency(text_lower)
        
        # Identify goals
        goals = self._extract_goals(text_lower)
        
        # Calculate confidence
        confidence = self._calculate_confidence(primary_intent, actions, goals)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(primary_intent, urgency)
        
        return {
            "primary_intent": primary_intent,
            "secondary_intents": self._identify_secondary_intents(text_lower, primary_intent),
            "actions": actions,
            "urgency": urgency,
            "goals": goals,
            "confidence": confidence,
            "recommendations": recommendations,
            "context_hints": self._extract_context_hints(text_lower)
        }
    
    def _identify_primary_intent(self, text: str) -> Dict[str, any]:
        """Identify the primary intent from text"""
        
        scores = {}
        
        for intent_type, config in self.intent_patterns.items():
            score = 0
            matched_patterns = []
            
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    score += config["confidence"]
                    matched_patterns.append(pattern)
            
            if score > 0:
                scores[intent_type] = {
                    "score": score,
                    "matched_patterns": matched_patterns,
                    "confidence": min(score, 1.0)
                }
        
        if not scores:
            return {
                "type": "create_new",
                "confidence": 0.5,
                "reason": "No specific intent pattern found, defaulting to new creation"
            }
        
        # Get the highest scoring intent
        best_intent = max(scores.items(), key=lambda x: x[1]["score"])
        
        return {
            "type": best_intent[0],
            "confidence": best_intent[1]["confidence"],
            "matched_patterns": best_intent[1]["matched_patterns"]
        }
    
    def _identify_secondary_intents(self, text: str, primary: Dict) -> List[Dict]:
        """Identify secondary intents"""
        
        secondary = []
        primary_type = primary.get("type")
        
        for intent_type, config in self.intent_patterns.items():
            if intent_type == primary_type:
                continue
                
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    secondary.append({
                        "type": intent_type,
                        "confidence": config["confidence"] * 0.7
                    })
                    break
        
        return secondary[:3]  # Return top 3 secondary intents
    
    def _extract_actions(self, text: str) -> List[str]:
        """Extract action verbs from text"""
        
        actions = []
        
        for category, verbs in self.action_verbs.items():
            for verb in verbs:
                if verb in text:
                    actions.append({
                        "verb": verb,
                        "category": category
                    })
        
        return actions
    
    def _determine_urgency(self, text: str) -> Dict[str, any]:
        """Determine urgency level from text"""
        
        for level, indicators in self.urgency_indicators.items():
            for indicator in indicators:
                if indicator in text:
                    return {
                        "level": level,
                        "indicator": indicator,
                        "priority_score": {"high": 3, "medium": 2, "low": 1}[level]
                    }
        
        return {
            "level": "medium",
            "indicator": None,
            "priority_score": 2
        }
    
    def _extract_goals(self, text: str) -> List[str]:
        """Extract project goals from text"""
        
        goals = []
        
        # Common goal patterns
        goal_patterns = [
            r"(?:to|for)\s+(\w+ing\s+\w+)",
            r"(?:goal|objective|aim)(?:\s+is)?\s+to\s+(.+?)(?:\.|,|;|$)",
            r"(?:want|need|require)\s+to\s+(.+?)(?:\.|,|;|$)",
            r"(?:should|must|will)\s+(.+?)(?:\.|,|;|$)"
        ]
        
        for pattern in goal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                goal = match.strip()
                if len(goal) > 10 and len(goal) < 100:
                    goals.append(goal)
        
        return goals[:5]  # Return top 5 goals
    
    def _calculate_confidence(self, primary_intent: Dict, actions: List, goals: List) -> float:
        """Calculate overall confidence score"""
        
        confidence = primary_intent.get("confidence", 0.5)
        
        # Boost confidence based on clarity indicators
        if actions:
            confidence += 0.1
        if goals:
            confidence += 0.1
        if len(actions) > 3:
            confidence += 0.05
        if len(goals) > 2:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _generate_recommendations(self, primary_intent: Dict, urgency: Dict) -> List[str]:
        """Generate recommendations based on intent"""
        
        recommendations = []
        intent_type = primary_intent.get("type")
        
        if intent_type == "create_new":
            recommendations.extend([
                "Start with core features and MVP approach",
                "Define clear project scope and requirements",
                "Consider scalability from the beginning"
            ])
        elif intent_type == "migrate_existing":
            recommendations.extend([
                "Create detailed migration plan with rollback strategy",
                "Ensure data integrity during migration",
                "Plan for parallel running during transition"
            ])
        elif intent_type == "enhance_existing":
            recommendations.extend([
                "Analyze current system limitations first",
                "Ensure backward compatibility",
                "Create comprehensive test suite"
            ])
        elif intent_type == "integrate_systems":
            recommendations.extend([
                "Define clear API contracts",
                "Implement proper error handling and retry logic",
                "Consider using message queues for reliability"
            ])
        elif intent_type == "automate_process":
            recommendations.extend([
                "Map current manual process thoroughly",
                "Identify automation boundaries and exceptions",
                "Plan for monitoring and alerting"
            ])
        
        # Add urgency-based recommendations
        if urgency["level"] == "high":
            recommendations.insert(0, "Focus on critical path items first")
        elif urgency["level"] == "low":
            recommendations.append("Consider phased implementation approach")
        
        return recommendations
    
    def _extract_context_hints(self, text: str) -> Dict[str, any]:
        """Extract context hints from text"""
        
        hints = {
            "industry": None,
            "scale": None,
            "users": None,
            "timeline": None
        }
        
        # Industry patterns
        industries = {
            "healthcare": ["health", "medical", "patient", "clinic", "hospital"],
            "finance": ["bank", "payment", "transaction", "finance", "trading"],
            "ecommerce": ["shop", "store", "product", "cart", "checkout"],
            "education": ["student", "course", "learning", "school", "education"],
            "social": ["social", "community", "network", "chat", "messaging"]
        }
        
        for industry, keywords in industries.items():
            if any(keyword in text for keyword in keywords):
                hints["industry"] = industry
                break
        
        # Scale patterns
        if re.search(r"\b(?:small|simple|basic|minimal)\b", text, re.IGNORECASE):
            hints["scale"] = "small"
        elif re.search(r"\b(?:large|enterprise|complex|comprehensive)\b", text, re.IGNORECASE):
            hints["scale"] = "large"
        else:
            hints["scale"] = "medium"
        
        # User count patterns
        user_match = re.search(r"(\d+)[+\s]*(?:users?|customers?|clients?)", text, re.IGNORECASE)
        if user_match:
            hints["users"] = int(user_match.group(1))
        
        # Timeline patterns
        timeline_match = re.search(r"(\d+)\s*(?:days?|weeks?|months?)", text, re.IGNORECASE)
        if timeline_match:
            hints["timeline"] = timeline_match.group(0)
        
        return hints