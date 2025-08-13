"""
Ambiguity Resolver Module
Detects and resolves ambiguities in requirements
"""

from typing import List, Dict, Any
import re


class AmbiguityResolver:
    """Detects and helps resolve ambiguities in project requirements"""

    def __init__(self):
        self.ambiguous_terms = {
            "size": ["small", "medium", "large", "big", "huge"],
            "speed": ["fast", "slow", "quick", "rapid"],
            "quality": ["good", "bad", "better", "best", "worst"],
            "quantity": ["some", "many", "few", "several", "lots"],
            "time": ["soon", "later", "eventually", "quickly"],
            "frequency": ["often", "sometimes", "rarely", "always", "never"],
        }

        self.vague_requirements = [
            "user-friendly",
            "intuitive",
            "modern",
            "professional",
            "easy to use",
            "nice looking",
            "responsive",
            "scalable",
        ]

    async def detect(self, requirements: Any) -> List[Dict[str, Any]]:
        """
        Detect ambiguities in requirements object

        Args:
            requirements: Requirements object

        Returns:
            List of detected ambiguities
        """
        ambiguities = []

        # Check description
        if hasattr(requirements, "description"):
            desc_ambiguities = self._detect_in_text(requirements.description)
            ambiguities.extend(desc_ambiguities)

        # Check features
        if hasattr(requirements, "features"):
            for feature in requirements.features:
                if self._is_vague(feature):
                    ambiguities.append(
                        {
                            "type": "vague_feature",
                            "text": feature,
                            "suggestion": f"Please specify what '{feature}' means in concrete terms",
                        }
                    )

        # Check requirements lists
        for req_type in ["functional_requirements", "non_functional_requirements"]:
            if hasattr(requirements, req_type):
                req_list = getattr(requirements, req_type)
                for req in req_list:
                    if self._contains_ambiguous_terms(req):
                        ambiguities.append(
                            {
                                "type": "ambiguous_requirement",
                                "text": req,
                                "category": req_type,
                            }
                        )

        return ambiguities

    async def detect_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Detect ambiguities directly from text"""
        return self._detect_in_text(text)

    def _detect_in_text(self, text: str) -> List[Dict[str, Any]]:
        """Detect ambiguities in text"""
        ambiguities = []
        text_lower = text.lower()

        # Check for ambiguous terms
        for category, terms in self.ambiguous_terms.items():
            for term in terms:
                if term in text_lower:
                    # Find context around the term
                    pattern = rf"([^.]*\b{term}\b[^.]*)"
                    matches = re.findall(pattern, text_lower)
                    for match in matches:
                        ambiguities.append(
                            {
                                "type": "ambiguous_term",
                                "category": category,
                                "term": term,
                                "context": match.strip(),
                            }
                        )

        # Check for vague requirements
        for vague_term in self.vague_requirements:
            if vague_term in text_lower:
                ambiguities.append(
                    {
                        "type": "vague_requirement",
                        "term": vague_term,
                        "suggestion": self._get_clarification_for_vague_term(
                            vague_term
                        ),
                    }
                )

        # Check for missing specifics
        if "database" in text_lower and not any(
            db in text_lower for db in ["postgres", "mysql", "mongodb", "sqlite"]
        ):
            ambiguities.append(
                {
                    "type": "missing_specific",
                    "category": "database",
                    "suggestion": "Which database system should be used?",
                }
            )

        if "api" in text_lower and not any(
            api in text_lower for api in ["rest", "graphql", "soap"]
        ):
            ambiguities.append(
                {
                    "type": "missing_specific",
                    "category": "api",
                    "suggestion": "What type of API (REST, GraphQL, etc.)?",
                }
            )

        return ambiguities

    async def generate_questions(self, ambiguities: List[Dict[str, Any]]) -> List[str]:
        """
        Generate clarification questions for ambiguities

        Args:
            ambiguities: List of detected ambiguities

        Returns:
            List of clarification questions
        """
        questions = []
        seen_categories = set()

        for ambiguity in ambiguities:
            amb_type = ambiguity.get("type")
            category = ambiguity.get("category", "")

            # Avoid duplicate questions for same category
            if category in seen_categories:
                continue

            if amb_type == "ambiguous_term":
                term = ambiguity.get("term")
                if category == "size":
                    questions.append(
                        f"When you say '{term}', approximately how many items/users are we talking about?"
                    )
                elif category == "speed":
                    questions.append(
                        f"What specific performance metrics are you targeting (e.g., response time in ms)?"
                    )
                elif category == "time":
                    questions.append(
                        f"What is your target timeline or deadline for this project?"
                    )
                seen_categories.add(category)

            elif amb_type == "vague_requirement":
                term = ambiguity.get("term")
                suggestion = ambiguity.get("suggestion")
                if suggestion:
                    questions.append(suggestion)

            elif amb_type == "missing_specific":
                suggestion = ambiguity.get("suggestion")
                if suggestion:
                    questions.append(suggestion)

        # Add general clarification questions if needed
        if len(questions) < 3:
            general_questions = [
                "Who is the primary target audience for this application?",
                "What is the expected number of concurrent users?",
                "Are there any specific design preferences or brand guidelines?",
                "What is the primary goal or success metric for this project?",
                "Are there any existing systems this needs to integrate with?",
            ]

            for q in general_questions:
                if len(questions) >= 5:
                    break
                if q not in questions:
                    questions.append(q)

        return questions[:5]  # Limit to 5 questions

    def _is_vague(self, text: str) -> bool:
        """Check if text contains vague terms"""
        text_lower = text.lower()
        return any(vague in text_lower for vague in self.vague_requirements)

    def _contains_ambiguous_terms(self, text: str) -> bool:
        """Check if text contains ambiguous terms"""
        text_lower = text.lower()
        for terms in self.ambiguous_terms.values():
            if any(term in text_lower for term in terms):
                return True
        return False

    def _get_clarification_for_vague_term(self, term: str) -> str:
        """Get clarification question for vague term"""
        clarifications = {
            "user-friendly": "What specific user experience features are most important (e.g., onboarding, help system, shortcuts)?",
            "intuitive": "What navigation patterns or UI conventions should we follow?",
            "modern": "What design style do you prefer (minimalist, material, glassmorphism)?",
            "professional": "What industry or business context should the design reflect?",
            "easy to use": "What is the technical skill level of your target users?",
            "nice looking": "Do you have any design references or color preferences?",
            "responsive": "Which devices and screen sizes must be supported?",
            "scalable": "What are your expected growth metrics (users, data, traffic)?",
        }

        return clarifications.get(
            term, f"Can you provide more specific details about '{term}'?"
        )
