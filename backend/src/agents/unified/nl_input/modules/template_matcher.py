"""
Template Matcher Module
Matches user input against predefined project templates
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class TemplateMatch:
    """Result of template matching"""

    template_name: str
    project_type: str
    confidence: float
    features: List[str]
    tech_stack: Dict[str, List[str]]
    suggested_name: str
    description: str
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    technical_requirements: Dict[str, Any]
    estimated_hours: int
    target_users: List[str]
    use_scenarios: List[str]


class TemplateMatcher:
    """Matches input against project templates for faster processing"""

    def __init__(self):
        self.templates = {}
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize project templates"""
        self.templates = {
            "simple_todo": {
                "patterns": ["simple todo", "task list", "todo app", "task manager"],
                "project_type": "todo",
                "features": ["auth", "database", "crud", "responsive"],
                "tech_stack": {
                    "frontend": ["react", "typescript", "tailwind"],
                    "backend": ["nodejs", "express"],
                    "database": ["postgresql"],
                },
                "functional_requirements": [
                    "Create, read, update, and delete tasks",
                    "Mark tasks as complete/incomplete",
                    "Filter tasks by status",
                    "Sort tasks by priority or date",
                ],
                "non_functional_requirements": [
                    "Mobile responsive design",
                    "Fast task operations (<100ms)",
                    "Secure user authentication",
                ],
                "estimated_hours": 40,
                "target_users": ["general_users"],
                "use_scenarios": [
                    "Personal task management",
                    "Daily planning",
                    "Project tracking",
                ],
            },
            "blog_platform": {
                "patterns": [
                    "blog",
                    "blogging platform",
                    "content management",
                    "writing platform",
                ],
                "project_type": "blog",
                "features": ["auth", "database", "cms", "seo", "responsive"],
                "tech_stack": {
                    "frontend": ["nextjs", "typescript", "tailwind"],
                    "backend": ["nextjs_api"],
                    "database": ["postgresql", "prisma"],
                },
                "functional_requirements": [
                    "Create and publish blog posts",
                    "Rich text editor for content",
                    "Comment system",
                    "Category and tag management",
                    "Search functionality",
                ],
                "non_functional_requirements": [
                    "SEO optimization",
                    "Fast page loads (<2s)",
                    "Mobile responsive",
                    "RSS feed support",
                ],
                "estimated_hours": 120,
                "target_users": ["content_creators", "readers"],
                "use_scenarios": [
                    "Personal blogging",
                    "Company blog",
                    "News publication",
                ],
            },
            "ecommerce_basic": {
                "patterns": ["online store", "ecommerce", "shop", "marketplace"],
                "project_type": "ecommerce",
                "features": [
                    "auth",
                    "database",
                    "payment",
                    "cart",
                    "search",
                    "responsive",
                ],
                "tech_stack": {
                    "frontend": ["nextjs", "typescript", "tailwind"],
                    "backend": ["nodejs", "express"],
                    "database": ["postgresql"],
                    "payment": ["stripe"],
                },
                "functional_requirements": [
                    "Product catalog with search and filters",
                    "Shopping cart functionality",
                    "Secure checkout process",
                    "Order management",
                    "User accounts and order history",
                ],
                "non_functional_requirements": [
                    "PCI compliance for payments",
                    "High availability (99.9%)",
                    "Fast product search (<500ms)",
                    "Mobile optimized",
                ],
                "estimated_hours": 320,
                "target_users": ["shoppers", "merchants"],
                "use_scenarios": [
                    "Browse and purchase products",
                    "Manage inventory",
                    "Process orders",
                ],
            },
            "admin_dashboard": {
                "patterns": [
                    "admin dashboard",
                    "analytics dashboard",
                    "monitoring dashboard",
                ],
                "project_type": "dashboard",
                "features": ["auth", "database", "charts", "api", "responsive"],
                "tech_stack": {
                    "frontend": ["react", "typescript", "recharts"],
                    "backend": ["nodejs", "express"],
                    "database": ["postgresql"],
                },
                "functional_requirements": [
                    "Real-time data visualization",
                    "Multiple chart types",
                    "Data filtering and date ranges",
                    "Export reports",
                    "User management",
                ],
                "non_functional_requirements": [
                    "Real-time data updates",
                    "Handle large datasets",
                    "Responsive charts",
                    "Role-based access",
                ],
                "estimated_hours": 160,
                "target_users": ["administrators", "analysts"],
                "use_scenarios": [
                    "Monitor business metrics",
                    "Generate reports",
                    "Track KPIs",
                ],
            },
            "chat_app": {
                "patterns": [
                    "chat app",
                    "messaging app",
                    "real-time chat",
                    "messenger",
                ],
                "project_type": "chat",
                "features": [
                    "auth",
                    "database",
                    "realtime",
                    "notification",
                    "responsive",
                ],
                "tech_stack": {
                    "frontend": ["react", "typescript"],
                    "backend": ["nodejs", "socket.io"],
                    "database": ["postgresql", "redis"],
                },
                "functional_requirements": [
                    "Real-time messaging",
                    "Private and group chats",
                    "Message history",
                    "User presence indicators",
                    "File sharing",
                ],
                "non_functional_requirements": [
                    "Message delivery <100ms",
                    "End-to-end encryption",
                    "Handle 10k+ concurrent users",
                    "Message persistence",
                ],
                "estimated_hours": 240,
                "target_users": ["general_users"],
                "use_scenarios": [
                    "Team communication",
                    "Customer support",
                    "Social messaging",
                ],
            },
        }

    async def load_templates(self):
        """Load additional templates (placeholder for future enhancement)"""
        # Could load from database or config file
        pass

    async def match(self, text: str) -> Optional[TemplateMatch]:
        """
        Match input text against templates

        Args:
            text: User input text

        Returns:
            TemplateMatch if found, None otherwise
        """
        text_lower = text.lower()
        best_match = None
        best_confidence = 0.0

        for template_name, template in self.templates.items():
            confidence = self._calculate_match_confidence(text_lower, template)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = (template_name, template)

        if best_confidence > 0.6:  # Threshold for template match
            template_name, template = best_match
            return TemplateMatch(
                template_name=template_name,
                project_type=template["project_type"],
                confidence=best_confidence,
                features=template["features"],
                tech_stack=template["tech_stack"],
                suggested_name=f"my-{template['project_type']}-app",
                description=f"A {template['project_type']} application",
                functional_requirements=template["functional_requirements"],
                non_functional_requirements=template["non_functional_requirements"],
                technical_requirements=template["tech_stack"],
                estimated_hours=template["estimated_hours"],
                target_users=template["target_users"],
                use_scenarios=template["use_scenarios"],
            )

        return None

    def _calculate_match_confidence(self, text: str, template: Dict) -> float:
        """Calculate confidence score for template match"""
        confidence = 0.0

        # Check pattern matches
        for pattern in template["patterns"]:
            if pattern in text:
                confidence += 0.4
                break

        # Check feature mentions
        feature_mentions = 0
        for feature in template["features"]:
            if feature in text:
                feature_mentions += 1

        if feature_mentions > 0:
            confidence += min(0.3, feature_mentions * 0.1)

        # Check tech stack mentions
        tech_mentions = 0
        for tech_list in template["tech_stack"].values():
            for tech in tech_list:
                if tech in text:
                    tech_mentions += 1

        if tech_mentions > 0:
            confidence += min(0.2, tech_mentions * 0.05)

        # Boost confidence for exact matches
        if any(
            f"create {pattern}" in text or f"build {pattern}" in text
            for pattern in template["patterns"]
        ):
            confidence += 0.1

        return min(confidence, 1.0)

    async def customize(self, template_match: TemplateMatch, text: str) -> Dict[str, Any]:
        """
        Customize template based on specific user input

        Args:
            template_match: Matched template
            text: Original user input

        Returns:
            Customizations to apply
        """
        customizations = {"additional_features": [], "modified_tech": {}}

        text_lower = text.lower()

        # Check for additional feature requests
        additional_features = {
            "dark mode": "dark_mode",
            "multi-language": "i18n",
            "notifications": "push_notifications",
            "export": "data_export",
            "import": "data_import",
            "social login": "oauth",
            "two-factor": "2fa",
        }

        for feature_text, feature_code in additional_features.items():
            if feature_text in text_lower and feature_code not in template_match.features:
                customizations["additional_features"].append(feature_code)

        # Check for tech stack modifications
        if "mongodb" in text_lower:
            customizations["modified_tech"]["database"] = ["mongodb"]
        elif "mysql" in text_lower:
            customizations["modified_tech"]["database"] = ["mysql"]

        if "vue" in text_lower:
            customizations["modified_tech"]["frontend"] = ["vue", "typescript"]
        elif "angular" in text_lower:
            customizations["modified_tech"]["frontend"] = ["angular", "typescript"]

        return customizations
