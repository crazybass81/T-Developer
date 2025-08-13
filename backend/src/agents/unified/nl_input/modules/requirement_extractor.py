"""
Requirement Extractor Module
Extracts functional, non-functional, and technical requirements
"""

from typing import List, Tuple, Dict, Any
import re


class RequirementExtractor:
    """Extracts different types of requirements from text"""

    def __init__(self):
        self.functional_patterns = [
            r"user[s]? (?:should be able to|can|must) (\w+.*?)(?:\.|,|$)",
            r"(?:feature|functionality)[:]\s*([^.]+)",
            r"(?:need|want|require)[s]?\s+(?:to\s+)?(\w+.*?)(?:\.|,|$)",
            r"(?:implement|create|build|add)\s+(\w+.*?)(?:\.|,|$)",
        ]

        self.non_functional_keywords = {
            "performance": ["fast", "quick", "speed", "performance", "optimize"],
            "security": ["secure", "safe", "encrypt", "auth", "protect"],
            "usability": ["easy", "simple", "intuitive", "user-friendly"],
            "reliability": ["reliable", "stable", "robust", "fault-tolerant"],
            "scalability": ["scale", "grow", "expand", "handle load"],
            "compatibility": ["compatible", "work with", "support", "cross-platform"],
            "accessibility": ["accessible", "a11y", "wcag", "screen reader"],
        }

        self.technical_keywords = {
            "api": ["api", "rest", "graphql", "endpoint", "service"],
            "database": ["database", "storage", "persist", "query", "schema"],
            "frontend": ["ui", "interface", "design", "layout", "component"],
            "backend": ["server", "backend", "processing", "logic", "business"],
            "integration": ["integrate", "connect", "third-party", "external"],
            "deployment": ["deploy", "host", "cloud", "server", "production"],
        }

    async def extract(
        self, text: str, project_type: str, entities: Dict[str, Any]
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Extract requirements from text

        Args:
            text: Project description
            project_type: Type of project
            entities: Extracted entities

        Returns:
            Tuple of (functional, non_functional, technical) requirements
        """
        functional = self._extract_functional(text, project_type)
        non_functional = self._extract_non_functional(text)
        technical = self._extract_technical(text, entities)

        # Add project-specific requirements
        functional.extend(self._get_default_functional(project_type))
        non_functional.extend(self._get_default_non_functional(project_type))

        # Remove duplicates while preserving order
        functional = list(dict.fromkeys(functional))
        non_functional = list(dict.fromkeys(non_functional))
        technical = list(dict.fromkeys(technical))

        return functional, non_functional, technical

    def _extract_functional(self, text: str, project_type: str) -> List[str]:
        """Extract functional requirements"""
        requirements = []

        # Use regex patterns
        for pattern in self.functional_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                requirement = match.strip()
                if len(requirement) > 5:  # Filter out very short matches
                    requirements.append(requirement)

        # Extract from bullet points or numbered lists
        list_pattern = r"[-*•]\s+(.+?)(?:\n|$)"
        list_matches = re.findall(list_pattern, text)
        requirements.extend(list_matches)

        # Extract from "must have" or "should have" statements
        must_have_pattern = r"(?:must|should)\s+have\s+(.+?)(?:\.|,|$)"
        must_matches = re.findall(must_have_pattern, text, re.IGNORECASE)
        requirements.extend(must_matches)

        return requirements

    def _extract_non_functional(self, text: str) -> List[str]:
        """Extract non-functional requirements"""
        requirements = []
        text_lower = text.lower()

        for category, keywords in self.non_functional_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Extract context around keyword
                    pattern = rf"([^.]*{keyword}[^.]*)"
                    matches = re.findall(pattern, text_lower)
                    for match in matches:
                        requirement = f"{category.capitalize()}: {match.strip()}"
                        requirements.append(requirement)
                    break  # Only add once per category

        # Extract specific metrics if mentioned
        metric_patterns = [
            (r"(\d+)\s*(?:ms|milliseconds?)", "Response time: {} ms"),
            (r"(\d+)\s*(?:users?|concurrent)", "Support {} concurrent users"),
            (r"(\d+)\s*(?:%|percent)\s*uptime", "{}% uptime requirement"),
            (
                r"load\s+(?:time|speed)[^.]*(\d+)\s*seconds?",
                "Page load time: {} seconds",
            ),
        ]

        for pattern, template in metric_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                requirements.append(template.format(match))

        return requirements

    def _extract_technical(self, text: str, entities: Dict[str, Any]) -> List[str]:
        """Extract technical requirements"""
        requirements = []
        text_lower = text.lower()

        for category, keywords in self.technical_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    requirement = f"{category.capitalize()} implementation required"
                    if requirement not in requirements:
                        requirements.append(requirement)
                    break

        # Extract specific technical mentions
        tech_patterns = [
            (r"using\s+(\w+(?:\s+\w+)?)", "Use {} technology"),
            (r"built\s+with\s+(\w+(?:\s+\w+)?)", "Built with {}"),
            (r"deploy(?:ed)?\s+(?:to|on)\s+(\w+)", "Deploy to {}"),
            (r"integrate\s+with\s+(\w+(?:\s+\w+)?)", "Integration with {}"),
        ]

        for pattern, template in tech_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                requirements.append(template.format(match))

        # Add entity-based requirements
        if entities and "technologies" in entities:
            for tech in entities["technologies"]:
                requirements.append(f"Implement {tech}")

        return requirements

    def _get_default_functional(self, project_type: str) -> List[str]:
        """Get default functional requirements for project type"""
        defaults = {
            "todo": [
                "Create new tasks",
                "Mark tasks as complete",
                "Delete tasks",
                "Edit task details",
            ],
            "blog": [
                "Create and publish posts",
                "Edit existing posts",
                "Add comments to posts",
                "Categorize content",
            ],
            "ecommerce": [
                "Browse products",
                "Add items to cart",
                "Process checkout",
                "Manage orders",
            ],
            "dashboard": [
                "Display key metrics",
                "Generate reports",
                "Visualize data",
                "Export data",
            ],
            "chat": [
                "Send and receive messages",
                "Create chat rooms",
                "Show user presence",
                "Send notifications",
            ],
        }

        return defaults.get(project_type, [])

    def _get_default_non_functional(self, project_type: str) -> List[str]:
        """Get default non-functional requirements for project type"""
        defaults = {
            "ecommerce": [
                "PCI compliance for payment processing",
                "High availability during peak shopping",
                "Fast product search response",
            ],
            "chat": [
                "Real-time message delivery",
                "End-to-end encryption",
                "Message history persistence",
            ],
            "dashboard": [
                "Fast data refresh rates",
                "Support large datasets",
                "Responsive visualizations",
            ],
        }

        base_requirements = [
            "Mobile responsive design",
            "Cross-browser compatibility",
            "Basic accessibility compliance",
        ]

        specific = defaults.get(project_type, [])
        return base_requirements + specific
