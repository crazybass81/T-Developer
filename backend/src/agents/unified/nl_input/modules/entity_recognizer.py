"""
Entity Recognizer Module
Extracts named entities and key concepts
"""

from typing import Dict, Any, List
import re


class EntityRecognizer:
    """Recognizes and extracts entities from text"""

    def __init__(self):
        self.entity_patterns = {
            "technologies": [
                r"\b(React|Vue|Angular|Svelte|Next\.?js|Nuxt)\b",
                r"\b(Node\.?js|Express|FastAPI|Django|Rails|Spring)\b",
                r"\b(PostgreSQL|MySQL|MongoDB|Redis|SQLite)\b",
                r"\b(Docker|Kubernetes|AWS|Azure|GCP)\b",
                r"\b(TypeScript|JavaScript|Python|Java|Ruby|Go)\b",
            ],
            "services": [
                r"\b(Stripe|PayPal|Square)\b",
                r"\b(Auth0|Firebase|Okta)\b",
                r"\b(SendGrid|Mailgun|Twilio)\b",
                r"\b(Cloudinary|S3|Imgur)\b",
            ],
            "concepts": [
                r"\b(API|REST|GraphQL|WebSocket)\b",
                r"\b(OAuth|JWT|SSO|2FA)\b",
                r"\b(CI/CD|DevOps|Agile|Scrum)\b",
                r"\b(SEO|PWA|SPA|SSR|SSG)\b",
            ],
            "users": [
                r"\b(admin|administrator|manager)\b",
                r"\b(user|customer|client|visitor)\b",
                r"\b(developer|programmer|engineer)\b",
                r"\b(student|teacher|instructor)\b",
            ],
        }

    async def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text

        Args:
            text: Input text

        Returns:
            Dictionary of extracted entities
        """
        entities = {}

        for entity_type, patterns in self.entity_patterns.items():
            extracted = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                extracted.extend(matches)

            # Remove duplicates while preserving order
            entities[entity_type] = list(dict.fromkeys(extracted))

        # Extract custom entities
        entities["numbers"] = self._extract_numbers(text)
        entities["urls"] = self._extract_urls(text)
        entities["emails"] = self._extract_emails(text)
        entities["dates"] = self._extract_dates(text)

        return entities

    def _extract_numbers(self, text: str) -> List[Dict[str, Any]]:
        """Extract numbers with context"""
        numbers = []

        # Extract numbers with units
        patterns = [
            (r"(\d+)\s*(users?|customers?)", "user_count"),
            (r"(\d+)\s*(GB|MB|KB)", "storage"),
            (r"(\d+)\s*(ms|seconds?|minutes?|hours?)", "time"),
            (r"\$(\d+(?:,\d+)?(?:\.\d+)?)", "price"),
            (r"(\d+)\s*(%|percent)", "percentage"),
        ]

        for pattern, context in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match[0] if isinstance(match, tuple) else match
                numbers.append({"value": value, "context": context})

        return numbers

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r"https?://[^\s]+"
        return re.findall(url_pattern, text)

    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses"""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.findall(email_pattern, text)

    def _extract_dates(self, text: str) -> List[str]:
        """Extract date references"""
        dates = []

        # Common date patterns
        patterns = [
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
            r"\b(today|tomorrow|yesterday|next week|next month)\b",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)

        return dates
