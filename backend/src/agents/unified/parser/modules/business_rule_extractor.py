"""
Business Rule Extractor Module
Extracts business rules and logic from requirements
"""

from typing import Dict, List, Any, Optional
import re
from enum import Enum


class RuleType(Enum):
    VALIDATION = "validation"
    CALCULATION = "calculation"
    WORKFLOW = "workflow"
    AUTHORIZATION = "authorization"
    CONDITIONAL = "conditional"


class BusinessRuleExtractor:
    """Extracts business rules from requirements"""

    def __init__(self):
        self.rule_patterns = {
            "conditional": [
                r"if\s+(.+?)\s+then\s+(.+)",
                r"when\s+(.+?)\s+(?:then|must)\s+(.+)",
                r"(?:only|except)\s+when\s+(.+)",
            ],
            "validation": [
                r"must\s+(?:be|have)\s+(.+)",
                r"should\s+(?:be|have)\s+(.+)",
                r"(?:cannot|must not)\s+(.+)",
            ],
            "calculation": [
                r"(?:calculate|compute)\s+(.+?)\s+(?:as|using|by)\s+(.+)",
                r"(.+?)\s*=\s*(.+)",
                r"(?:sum|total|average)\s+of\s+(.+)",
            ],
        }

    async def extract(self, nlp_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract business rules from text"""

        text = nlp_result.get("original", "")
        sentences = nlp_result.get("sentences", [])

        rules = []

        # Extract rules by pattern
        for rule_type, patterns in self.rule_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    rule = self._create_rule(match, rule_type)
                    if rule:
                        rules.append(rule)

        # Extract rules from sentences
        for sentence in sentences:
            if self._is_rule_sentence(sentence):
                rule = self._extract_rule_from_sentence(sentence)
                if rule:
                    rules.append(rule)

        # Categorize rules
        categorized = self._categorize_rules(rules)

        # Generate rule implementations
        for rule in rules:
            rule["implementation"] = self._generate_implementation(rule)

        return {
            "rules": rules,
            "categorized": categorized,
            "statistics": self._calculate_statistics(rules),
        }

    def _is_rule_sentence(self, sentence: str) -> bool:
        """Check if sentence contains a business rule"""
        rule_keywords = [
            "must",
            "should",
            "cannot",
            "require",
            "if",
            "when",
            "only",
            "except",
        ]
        return any(keyword in sentence.lower() for keyword in rule_keywords)

    def _extract_rule_from_sentence(self, sentence: str) -> Optional[Dict]:
        """Extract rule from sentence"""
        return {
            "text": sentence,
            "type": self._determine_rule_type(sentence),
            "enforceable": True,
            "priority": "medium",
        }

    def _create_rule(self, match: re.Match, rule_type: str) -> Dict:
        """Create rule from regex match"""
        groups = match.groups()

        if rule_type == "conditional":
            return {
                "type": RuleType.CONDITIONAL.value,
                "condition": groups[0] if groups else "",
                "action": groups[1] if len(groups) > 1 else "",
                "text": match.group(0),
                "enforceable": True,
            }
        elif rule_type == "validation":
            return {
                "type": RuleType.VALIDATION.value,
                "requirement": groups[0] if groups else "",
                "text": match.group(0),
                "enforceable": True,
            }
        elif rule_type == "calculation":
            return {
                "type": RuleType.CALCULATION.value,
                "target": groups[0] if groups else "",
                "formula": groups[1] if len(groups) > 1 else "",
                "text": match.group(0),
                "enforceable": True,
            }

        return None

    def _determine_rule_type(self, text: str) -> str:
        """Determine the type of business rule"""
        text_lower = text.lower()

        if "if" in text_lower or "when" in text_lower:
            return RuleType.CONDITIONAL.value
        elif "calculate" in text_lower or "compute" in text_lower:
            return RuleType.CALCULATION.value
        elif "workflow" in text_lower or "process" in text_lower:
            return RuleType.WORKFLOW.value
        elif "permission" in text_lower or "access" in text_lower:
            return RuleType.AUTHORIZATION.value
        else:
            return RuleType.VALIDATION.value

    def _categorize_rules(self, rules: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize rules by type"""
        categorized = {}

        for rule in rules:
            rule_type = rule.get("type", "unknown")
            if rule_type not in categorized:
                categorized[rule_type] = []
            categorized[rule_type].append(rule)

        return categorized

    def _generate_implementation(self, rule: Dict) -> str:
        """Generate pseudo-code implementation for rule"""
        rule_type = rule.get("type")

        if rule_type == RuleType.CONDITIONAL.value:
            return f"""
if ({rule.get('condition', 'condition')}):
    {rule.get('action', 'perform_action()')}
"""
        elif rule_type == RuleType.VALIDATION.value:
            return f"""
def validate():
    return check({rule.get('requirement', 'requirement')})
"""
        elif rule_type == RuleType.CALCULATION.value:
            return f"""
def calculate():
    return {rule.get('formula', 'compute_value()')}
"""

        return "# Rule implementation"

    def _calculate_statistics(self, rules: List[Dict]) -> Dict[str, Any]:
        """Calculate rule statistics"""
        type_counts = {}
        for rule in rules:
            rule_type = rule.get("type", "unknown")
            type_counts[rule_type] = type_counts.get(rule_type, 0) + 1

        return {
            "total_rules": len(rules),
            "by_type": type_counts,
            "enforceable": sum(1 for r in rules if r.get("enforceable")),
        }
