"""
Tech Stack Analyzer Module
Analyzes and recommends technology stack
"""

from typing import Dict, Any, List, Optional
import re

class TechStackAnalyzer:
    """Analyzes technology preferences and recommends appropriate stack"""
    
    def __init__(self):
        self.tech_stacks = {
            "modern_web": {
                "frontend": ["React", "TypeScript", "Tailwind CSS"],
                "backend": ["Node.js", "Express", "TypeScript"],
                "database": ["PostgreSQL", "Redis"],
                "tools": ["Docker", "GitHub Actions"]
            },
            "enterprise_java": {
                "frontend": ["React", "TypeScript"],
                "backend": ["Spring Boot", "Java"],
                "database": ["PostgreSQL", "Redis"],
                "tools": ["Docker", "Jenkins", "Kubernetes"]
            },
            "python_ml": {
                "frontend": ["React", "TypeScript"],
                "backend": ["FastAPI", "Python"],
                "database": ["PostgreSQL", "MongoDB"],
                "ml": ["TensorFlow", "PyTorch", "Scikit-learn"],
                "tools": ["Docker", "MLflow"]
            },
            "serverless": {
                "frontend": ["Next.js", "TypeScript"],
                "backend": ["AWS Lambda", "API Gateway"],
                "database": ["DynamoDB", "Aurora Serverless"],
                "tools": ["Serverless Framework", "AWS CDK"]
            },
            "mobile_cross_platform": {
                "mobile": ["React Native", "TypeScript"],
                "backend": ["Node.js", "GraphQL"],
                "database": ["PostgreSQL", "Firebase"],
                "tools": ["Expo", "Fastlane"]
            },
            "startup_mvp": {
                "frontend": ["Next.js", "TypeScript"],
                "backend": ["Node.js", "Prisma"],
                "database": ["PostgreSQL"],
                "deployment": ["Vercel", "Railway"],
                "tools": ["GitHub Actions"]
            }
        }
        
        self.tech_compatibility = {
            "React": ["Node.js", "Python", "Java", ".NET"],
            "Vue": ["Node.js", "Python", "PHP", "Java"],
            "Angular": ["Node.js", "Java", ".NET"],
            "PostgreSQL": ["Node.js", "Python", "Java", "PHP", ".NET"],
            "MongoDB": ["Node.js", "Python", "Java"],
            "Redis": ["Node.js", "Python", "Java", "PHP"]
        }
    
    async def analyze(
        self,
        description: str,
        project_type: str,
        preferred_stack: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze and recommend technology stack
        
        Args:
            description: Project description
            project_type: Type of project
            preferred_stack: User's preferred technologies
            
        Returns:
            Recommended technology stack
        """
        
        # Extract mentioned technologies
        mentioned_tech = self._extract_technologies(description)
        
        # Get base stack for project type
        base_stack = self._get_base_stack(project_type)
        
        # Merge with preferences
        if preferred_stack:
            base_stack = self._merge_preferences(base_stack, preferred_stack)
        
        # Merge with mentioned technologies
        if mentioned_tech:
            base_stack = self._merge_mentioned(base_stack, mentioned_tech)
        
        # Validate compatibility
        base_stack = self._ensure_compatibility(base_stack)
        
        # Add recommendations
        base_stack["recommendations"] = self._get_recommendations(project_type, base_stack)
        
        return base_stack
    
    def _extract_technologies(self, description: str) -> Dict[str, List[str]]:
        """Extract mentioned technologies from description"""
        
        mentioned = {
            "frontend": [],
            "backend": [],
            "database": [],
            "cloud": [],
            "tools": []
        }
        
        description_lower = description.lower()
        
        # Frontend technologies
        frontend_techs = ["react", "vue", "angular", "svelte", "next.js", "nuxt", "gatsby"]
        for tech in frontend_techs:
            if tech in description_lower:
                mentioned["frontend"].append(tech.title())
        
        # Backend technologies
        backend_techs = ["node", "python", "java", "php", "ruby", "go", "rust", ".net", "django", "flask", "fastapi", "express", "spring"]
        for tech in backend_techs:
            if tech in description_lower:
                mentioned["backend"].append(tech.title())
        
        # Database technologies
        db_techs = ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb", "firebase", "sqlite"]
        for tech in db_techs:
            if tech in description_lower:
                mentioned["database"].append(tech.title())
        
        # Cloud providers
        cloud_techs = ["aws", "google cloud", "gcp", "azure", "heroku", "vercel", "netlify", "digital ocean"]
        for tech in cloud_techs:
            if tech in description_lower:
                mentioned["cloud"].append(tech.title())
        
        return mentioned
    
    def _get_base_stack(self, project_type: str) -> Dict[str, Any]:
        """Get base technology stack for project type"""
        
        base_stacks = {
            "web_app": self.tech_stacks["modern_web"],
            "mobile_app": self.tech_stacks["mobile_cross_platform"],
            "e_commerce": {
                "frontend": ["Next.js", "TypeScript", "Tailwind CSS"],
                "backend": ["Node.js", "Express", "TypeScript"],
                "database": ["PostgreSQL", "Redis"],
                "payment": ["Stripe"],
                "tools": ["Docker", "GitHub Actions"]
            },
            "saas": {
                "frontend": ["React", "TypeScript", "Tailwind CSS"],
                "backend": ["Node.js", "Express", "TypeScript"],
                "database": ["PostgreSQL", "Redis"],
                "auth": ["Auth0", "Clerk"],
                "tools": ["Docker", "Kubernetes", "GitHub Actions"]
            },
            "api": {
                "backend": ["Node.js", "Express", "TypeScript"],
                "database": ["PostgreSQL", "Redis"],
                "docs": ["Swagger", "Postman"],
                "tools": ["Docker", "GitHub Actions"]
            },
            "ai_ml": self.tech_stacks["python_ml"],
            "serverless": self.tech_stacks["serverless"]
        }
        
        return base_stacks.get(project_type, self.tech_stacks["modern_web"]).copy()
    
    def _merge_preferences(
        self,
        base_stack: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge user preferences with base stack"""
        
        for category, techs in preferences.items():
            if category in base_stack:
                if isinstance(techs, list):
                    base_stack[category] = techs
                elif isinstance(techs, str):
                    base_stack[category] = [techs]
        
        return base_stack
    
    def _merge_mentioned(
        self,
        base_stack: Dict[str, Any],
        mentioned: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Merge mentioned technologies with base stack"""
        
        for category, techs in mentioned.items():
            if techs and category in base_stack:
                # Replace with mentioned technologies if explicitly stated
                base_stack[category] = techs
        
        return base_stack
    
    def _ensure_compatibility(self, stack: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure technologies in stack are compatible"""
        
        # Check frontend-backend compatibility
        if "frontend" in stack and "backend" in stack:
            frontend = stack["frontend"][0] if stack["frontend"] else None
            backend = stack["backend"][0] if stack["backend"] else None
            
            # Adjust if incompatible
            if frontend == "Angular" and backend == "PHP":
                stack["backend"] = ["Node.js", "Express"]
        
        return stack
    
    def _get_recommendations(
        self,
        project_type: str,
        stack: Dict[str, Any]
    ) -> List[str]:
        """Get technology recommendations"""
        
        recommendations = []
        
        # General recommendations
        if "TypeScript" not in str(stack):
            recommendations.append("Consider using TypeScript for better type safety")
        
        if "Docker" not in str(stack):
            recommendations.append("Use Docker for consistent development environments")
        
        # Project-specific recommendations
        if project_type == "e_commerce" and "Stripe" not in str(stack):
            recommendations.append("Integrate Stripe for payment processing")
        
        if project_type == "saas" and "auth" not in stack:
            recommendations.append("Implement authentication with Auth0 or Clerk")
        
        if project_type == "mobile_app" and "push" not in stack:
            recommendations.append("Add push notification service (Firebase, OneSignal)")
        
        return recommendations