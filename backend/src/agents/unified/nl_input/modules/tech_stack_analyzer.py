"""
Tech Stack Analyzer Module
Analyzes and recommends technology stacks
"""

from typing import Dict, Any, List, Optional


class TechStackAnalyzer:
    """Analyzes and recommends technology stacks"""

    def __init__(self):
        self.tech_stacks = {
            "modern_web": {
                "frontend": ["react", "typescript", "tailwind"],
                "backend": ["nodejs", "express", "prisma"],
                "database": ["postgresql"],
                "tools": ["vite", "eslint", "prettier"],
            },
            "full_stack_next": {
                "frontend": ["nextjs", "typescript", "tailwind"],
                "backend": ["nextjs_api"],
                "database": ["postgresql", "prisma"],
                "tools": ["turbo", "eslint"],
            },
            "enterprise": {
                "frontend": ["angular", "typescript", "material"],
                "backend": ["java", "spring"],
                "database": ["oracle", "postgresql"],
                "tools": ["jenkins", "sonar"],
            },
            "startup": {
                "frontend": ["react", "typescript"],
                "backend": ["nodejs", "fastify"],
                "database": ["mongodb"],
                "tools": ["docker", "github_actions"],
            },
            "python_stack": {
                "frontend": ["react", "typescript"],
                "backend": ["python", "fastapi"],
                "database": ["postgresql", "sqlalchemy"],
                "tools": ["poetry", "black", "pytest"],
            },
        }

    async def analyze(
        self, text: str, project_type: str, preferred_stack: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze and recommend technology stack

        Args:
            text: Project description
            project_type: Type of project
            preferred_stack: User's preferred stack

        Returns:
            Recommended technology stack
        """
        text_lower = text.lower()

        # Start with preferred stack or default
        if preferred_stack and preferred_stack in self.tech_stacks:
            base_stack = self.tech_stacks[preferred_stack].copy()
        else:
            base_stack = self._get_default_stack(project_type)

        # Adjust based on mentions in text
        stack = self._adjust_stack_from_text(base_stack, text_lower)

        # Add project-specific recommendations
        stack = self._add_project_specific_tech(stack, project_type)

        # Add performance and scaling considerations
        if any(
            word in text_lower for word in ["scale", "performance", "fast", "million"]
        ):
            stack = self._add_performance_tech(stack)

        # Add security considerations
        if any(word in text_lower for word in ["secure", "security", "encryption"]):
            stack = self._add_security_tech(stack)

        return stack

    def _get_default_stack(self, project_type: str) -> Dict[str, List[str]]:
        """Get default stack for project type"""
        defaults = {
            "todo": self.tech_stacks["modern_web"],
            "blog": self.tech_stacks["full_stack_next"],
            "ecommerce": self.tech_stacks["full_stack_next"],
            "dashboard": self.tech_stacks["modern_web"],
            "chat": self.tech_stacks["modern_web"],
            "saas": self.tech_stacks["startup"],
            "enterprise": self.tech_stacks["enterprise"],
        }

        return defaults.get(project_type, self.tech_stacks["modern_web"]).copy()

    def _adjust_stack_from_text(self, stack: Dict, text: str) -> Dict[str, List[str]]:
        """Adjust stack based on text mentions"""
        adjusted = stack.copy()

        # Framework detection
        if "vue" in text:
            adjusted["frontend"] = ["vue", "typescript", "tailwind"]
        elif "angular" in text:
            adjusted["frontend"] = ["angular", "typescript", "material"]
        elif "svelte" in text:
            adjusted["frontend"] = ["svelte", "typescript", "tailwind"]

        # Backend detection
        if "python" in text or "fastapi" in text:
            adjusted["backend"] = ["python", "fastapi"]
        elif "django" in text:
            adjusted["backend"] = ["python", "django"]
        elif "spring" in text or "java" in text:
            adjusted["backend"] = ["java", "spring"]

        # Database detection
        if "mongo" in text:
            adjusted["database"] = ["mongodb"]
        elif "mysql" in text:
            adjusted["database"] = ["mysql"]
        elif "redis" in text:
            if "database" not in adjusted:
                adjusted["database"] = []
            adjusted["database"].append("redis")

        return adjusted

    def _add_project_specific_tech(
        self, stack: Dict, project_type: str
    ) -> Dict[str, List[str]]:
        """Add project-specific technologies"""
        enhanced = stack.copy()

        specific_tech = {
            "ecommerce": {
                "payment": ["stripe", "paypal"],
                "services": ["sendgrid", "twilio"],
            },
            "chat": {
                "realtime": ["socket.io", "websockets"],
                "services": ["pusher", "firebase"],
            },
            "dashboard": {
                "visualization": ["d3", "chartjs", "recharts"],
                "services": ["elasticsearch", "grafana"],
            },
            "blog": {
                "cms": ["strapi", "contentful"],
                "services": ["algolia", "disqus"],
            },
        }

        if project_type in specific_tech:
            for category, techs in specific_tech[project_type].items():
                if category not in enhanced:
                    enhanced[category] = []
                enhanced[category].extend(techs)

        return enhanced

    def _add_performance_tech(self, stack: Dict) -> Dict[str, List[str]]:
        """Add performance-related technologies"""
        enhanced = stack.copy()

        if "caching" not in enhanced:
            enhanced["caching"] = []
        enhanced["caching"].extend(["redis", "memcached"])

        if "cdn" not in enhanced:
            enhanced["cdn"] = []
        enhanced["cdn"].extend(["cloudflare", "fastly"])

        if "monitoring" not in enhanced:
            enhanced["monitoring"] = []
        enhanced["monitoring"].extend(["newrelic", "datadog"])

        return enhanced

    def _add_security_tech(self, stack: Dict) -> Dict[str, List[str]]:
        """Add security-related technologies"""
        enhanced = stack.copy()

        if "security" not in enhanced:
            enhanced["security"] = []
        enhanced["security"].extend(["jwt", "bcrypt", "helmet"])

        if "auth" not in enhanced:
            enhanced["auth"] = []
        enhanced["auth"].extend(["auth0", "firebase-auth"])

        return enhanced
