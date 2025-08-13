"""
🧬 T-Developer AI Capability Extractor
Optimized for <6.5KB constraint
"""
import ast
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set


@dataclass
class Capability:
    """Agent capability definition"""

    name: str
    confidence: float
    category: str


@dataclass
class CapabilityProfile:
    """Complete capability profile"""

    capabilities: List[Capability]
    primary_functions: List[str]
    tech_stack: List[str]
    complexity_level: str
    specialization_score: float


class CapabilityExtractor:
    """Extract agent capabilities from code analysis"""

    def __init__(self):
        # Core patterns (reduced for size)
        self.patterns = {
            "data_processing": {"keywords": ["pandas", "numpy", "csv", "json"], "category": "data"},
            "web_api": {"keywords": ["fastapi", "requests", "http", "api"], "category": "web"},
            "database": {"keywords": ["sqlalchemy", "pymongo", "query"], "category": "persistence"},
            "ml_ai": {"keywords": ["sklearn", "model", "predict"], "category": "ai"},
            "file_system": {"keywords": ["pathlib", "open", "read", "write"], "category": "system"},
            "async_processing": {
                "keywords": ["asyncio", "async def", "await"],
                "category": "concurrency",
            },
        }

        self.complexity_indicators = {
            "simple": ["print", "return", "if"],
            "moderate": ["class", "try", "with"],
            "complex": ["decorator", "async"],
            "advanced": ["typing", "protocol"],
        }

    def extract_capabilities(self, code: str, imports: List[str] = None) -> CapabilityProfile:
        """Extract comprehensive capability profile"""
        try:
            tree = ast.parse(code)
            capabilities = self._detect_capabilities(code, imports or [])
            primary_functions = self._extract_primary_functions(tree)
            tech_stack = self._identify_tech_stack(code, imports or [])
            complexity_level = self._assess_complexity(code)
            specialization_score = self._calculate_specialization(capabilities)

            return CapabilityProfile(
                capabilities=capabilities,
                primary_functions=primary_functions,
                tech_stack=tech_stack,
                complexity_level=complexity_level,
                specialization_score=specialization_score,
            )
        except Exception:
            return CapabilityProfile([], [], [], "unknown", 0.0)

    def _detect_capabilities(self, code: str, imports: List[str]) -> List[Capability]:
        """Detect capabilities from code patterns"""
        capabilities = []
        all_text = (code + " ".join(imports)).lower()

        for cap_name, config in self.patterns.items():
            confidence = 0.0

            # Check keywords
            matches = sum(1 for kw in config["keywords"] if kw in all_text)
            confidence = matches * 0.3

            if confidence > 0.5:
                capabilities.append(
                    Capability(
                        name=cap_name, confidence=min(1.0, confidence), category=config["category"]
                    )
                )

        return sorted(capabilities, key=lambda x: x.confidence, reverse=True)

    def _extract_primary_functions(self, tree: ast.AST) -> List[str]:
        """Extract primary function names"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                functions.append(node.name)
        return functions[:3]  # Top 3 functions

    def _identify_tech_stack(self, code: str, imports: List[str]) -> List[str]:
        """Identify technology stack"""
        tech_stack = set()
        all_imports = " ".join(imports) + code

        patterns = {
            "FastAPI": "fastapi",
            "SQLAlchemy": "sqlalchemy",
            "Pandas": "pandas",
            "Requests": "requests",
            "AsyncIO": "asyncio",
        }

        for tech, pattern in patterns.items():
            if pattern in all_imports.lower():
                tech_stack.add(tech)

        return list(tech_stack)

    def _assess_complexity(self, code: str) -> str:
        """Assess code complexity level"""
        complexity_scores = defaultdict(int)
        code_lower = code.lower()

        for level, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                if indicator in code_lower:
                    complexity_scores[level] += 1

        if complexity_scores["advanced"] > 0:
            return "advanced"
        elif complexity_scores["complex"] > 1:
            return "complex"
        elif complexity_scores["moderate"] > 1:
            return "moderate"
        else:
            return "simple"

    def _calculate_specialization(self, capabilities: List[Capability]) -> float:
        """Calculate specialization score (0-1)"""
        if not capabilities:
            return 0.0

        # Group by category
        categories = defaultdict(list)
        for cap in capabilities:
            categories[cap.category].append(cap.confidence)

        # Simple concentration measure
        if len(categories) == 1:
            return 0.9  # Highly specialized
        elif len(categories) <= 2:
            return 0.6  # Moderately specialized
        else:
            return 0.3  # General purpose


# Factory and convenience functions
def create_extractor() -> CapabilityExtractor:
    """Create capability extractor instance"""
    return CapabilityExtractor()


def extract_quick(code: str) -> Dict[str, Any]:
    """Quick capability extraction"""
    extractor = CapabilityExtractor()
    profile = extractor.extract_capabilities(code)
    return {
        "top_capabilities": [cap.name for cap in profile.capabilities[:2]],
        "complexity": profile.complexity_level,
        "specialization": profile.specialization_score,
    }
