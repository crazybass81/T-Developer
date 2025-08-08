"""
Requirement Extractor Module
Extracts functional, non-functional, and technical requirements
"""

from typing import List, Tuple, Dict, Any
import re

class RequirementExtractor:
    """Extracts different types of requirements from project description"""
    
    def __init__(self):
        # Functional requirement patterns
        self.functional_patterns = {
            "authentication": [
                r"(user|account)\s*(login|signin|authentication)",
                r"(register|signup|create\s*account)",
                r"(logout|signout)",
                r"password\s*(reset|recovery|forgot)",
                r"(two|2)\s*factor\s*auth",
                r"social\s*(login|auth)",
                r"sso|single\s*sign\s*on"
            ],
            "user_management": [
                r"user\s*(profile|management|roles)",
                r"(admin|role)\s*management",
                r"permissions?\s*system",
                r"user\s*groups?",
                r"access\s*control"
            ],
            "data_operations": [
                r"(create|add|insert)\s*\w+",
                r"(read|view|display|show)\s*\w+",
                r"(update|edit|modify)\s*\w+",
                r"(delete|remove)\s*\w+",
                r"crud\s*operations?",
                r"data\s*management"
            ],
            "search_filter": [
                r"search\s*(functionality|feature|bar)",
                r"filter(ing)?\s*(options|data)",
                r"sort(ing)?\s*(options|data)",
                r"advanced\s*search",
                r"faceted\s*search"
            ],
            "payment": [
                r"payment\s*(processing|gateway|integration)",
                r"(stripe|paypal|square)\s*integration",
                r"subscription\s*billing",
                r"checkout\s*process",
                r"shopping\s*cart",
                r"invoice\s*generation"
            ],
            "communication": [
                r"(email|sms)\s*notifications?",
                r"push\s*notifications?",
                r"in[\s-]?app\s*messaging",
                r"chat\s*(functionality|feature)",
                r"comment(ing)?\s*system",
                r"notification\s*center"
            ],
            "file_handling": [
                r"file\s*(upload|download)",
                r"image\s*(upload|processing|gallery)",
                r"document\s*management",
                r"media\s*library",
                r"(import|export)\s*data",
                r"csv\s*(import|export)"
            ],
            "reporting": [
                r"report(ing)?\s*(system|generation)",
                r"analytics\s*dashboard",
                r"data\s*visualization",
                r"charts?\s*and\s*graphs?",
                r"export\s*to\s*(pdf|excel)",
                r"business\s*intelligence"
            ],
            "integration": [
                r"api\s*integration",
                r"third[\s-]?party\s*integration",
                r"webhook\s*support",
                r"rest(ful)?\s*api",
                r"graphql\s*api",
                r"external\s*service"
            ],
            "workflow": [
                r"workflow\s*management",
                r"approval\s*process",
                r"task\s*automation",
                r"business\s*process",
                r"state\s*machine",
                r"pipeline\s*management"
            ]
        }
        
        # Non-functional requirement patterns
        self.non_functional_patterns = {
            "performance": [
                r"(fast|quick|rapid)\s*(loading|response|performance)",
                r"page\s*load\s*time",
                r"response\s*time",
                r"high\s*performance",
                r"optimization",
                r"caching\s*strategy",
                r"lazy\s*loading"
            ],
            "scalability": [
                r"scalab(le|ility)",
                r"(handle|support)\s*\d+\s*users?",
                r"concurrent\s*users?",
                r"auto[\s-]?scaling",
                r"load\s*balancing",
                r"horizontal\s*scaling"
            ],
            "security": [
                r"secure?\s*(data|communication|storage)",
                r"encrypt(ion|ed)",
                r"ssl\s*certificate",
                r"data\s*protection",
                r"gdpr\s*complian(t|ce)",
                r"hipaa\s*complian(t|ce)",
                r"penetration\s*testing"
            ],
            "usability": [
                r"user[\s-]?friendly",
                r"intuitive\s*interface",
                r"easy\s*to\s*use",
                r"ux\s*design",
                r"responsive\s*design",
                r"mobile[\s-]?friendly",
                r"accessibility",
                r"wcag\s*complian(t|ce)"
            ],
            "reliability": [
                r"99\.?\d+%\s*uptime",
                r"high\s*availability",
                r"fault\s*toleran(t|ce)",
                r"disaster\s*recovery",
                r"backup\s*strategy",
                r"redundancy",
                r"failover"
            ],
            "compatibility": [
                r"cross[\s-]?browser",
                r"browser\s*compatibility",
                r"mobile\s*compatibility",
                r"backward\s*compatible",
                r"(ios|android)\s*support",
                r"progressive\s*web\s*app"
            ]
        }
        
        # Technical requirement patterns
        self.technical_patterns = {
            "frontend": [
                r"react(\s*js)?",
                r"vue(\s*js)?",
                r"angular",
                r"next\s*js",
                r"nuxt",
                r"svelte",
                r"typescript",
                r"javascript"
            ],
            "backend": [
                r"node(\s*js)?",
                r"python",
                r"django",
                r"flask",
                r"fastapi",
                r"express(\s*js)?",
                r"nest\s*js",
                r"spring\s*boot",
                r"\.net\s*core",
                r"ruby\s*on\s*rails"
            ],
            "database": [
                r"postgres(ql)?",
                r"mysql",
                r"mongodb",
                r"redis",
                r"elasticsearch",
                r"dynamodb",
                r"firebase",
                r"sqlite"
            ],
            "cloud": [
                r"aws",
                r"amazon\s*web\s*services",
                r"google\s*cloud",
                r"gcp",
                r"azure",
                r"heroku",
                r"vercel",
                r"netlify",
                r"digital\s*ocean"
            ],
            "devops": [
                r"docker",
                r"kubernetes",
                r"k8s",
                r"ci[\s/]cd",
                r"jenkins",
                r"github\s*actions",
                r"terraform",
                r"ansible"
            ]
        }
    
    async def extract(
        self,
        description: str,
        project_type: str,
        entities: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Extract requirements from description
        
        Args:
            description: Project description
            project_type: Type of project
            entities: Extracted entities
            
        Returns:
            Tuple of (functional, non_functional, technical) requirements
        """
        
        functional = await self._extract_functional(description, project_type, entities)
        non_functional = await self._extract_non_functional(description)
        technical = await self._extract_technical(description)
        
        # Add project-type specific requirements
        functional.extend(self._get_default_requirements(project_type))
        
        # Remove duplicates while preserving order
        functional = list(dict.fromkeys(functional))
        non_functional = list(dict.fromkeys(non_functional))
        technical = list(dict.fromkeys(technical))
        
        return functional, non_functional, technical
    
    async def _extract_functional(
        self,
        description: str,
        project_type: str,
        entities: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Extract functional requirements"""
        
        requirements = []
        description_lower = description.lower()
        
        for category, patterns in self.functional_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    requirement = self._format_functional_requirement(category, pattern, description_lower)
                    if requirement:
                        requirements.append(requirement)
                    break  # Only add one requirement per category
        
        # Add entity-based requirements
        if entities:
            requirements.extend(self._extract_from_entities(entities))
        
        return requirements
    
    async def _extract_non_functional(self, description: str) -> List[str]:
        """Extract non-functional requirements"""
        
        requirements = []
        description_lower = description.lower()
        
        for category, patterns in self.non_functional_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, description_lower, re.IGNORECASE)
                if match:
                    requirement = self._format_non_functional_requirement(category, match.group())
                    if requirement:
                        requirements.append(requirement)
                    break
        
        # Add default non-functional requirements
        if not any("performance" in req.lower() for req in requirements):
            requirements.append("Page load time < 3 seconds")
        
        if not any("security" in req.lower() for req in requirements):
            requirements.append("Secure data transmission with HTTPS")
        
        return requirements
    
    async def _extract_technical(self, description: str) -> List[str]:
        """Extract technical requirements"""
        
        requirements = []
        description_lower = description.lower()
        
        for category, patterns in self.technical_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, description_lower, re.IGNORECASE)
                if match:
                    tech = match.group().title()
                    requirements.append(f"{category.title()}: {tech}")
        
        return requirements
    
    def _format_functional_requirement(self, category: str, pattern: str, text: str) -> str:
        """Format functional requirement based on category and match"""
        
        formats = {
            "authentication": "User authentication and authorization system",
            "user_management": "User management and role-based access control",
            "data_operations": "CRUD operations for data management",
            "search_filter": "Search and filter functionality",
            "payment": "Payment processing and billing system",
            "communication": "Communication and notification system",
            "file_handling": "File upload and management system",
            "reporting": "Reporting and analytics dashboard",
            "integration": "Third-party API integrations",
            "workflow": "Workflow and process automation"
        }
        
        return formats.get(category, f"{category.replace('_', ' ').title()} functionality")
    
    def _format_non_functional_requirement(self, category: str, matched_text: str) -> str:
        """Format non-functional requirement"""
        
        formats = {
            "performance": f"High performance with {matched_text}",
            "scalability": f"Scalable architecture to {matched_text}",
            "security": f"Security requirement: {matched_text}",
            "usability": f"Usability: {matched_text}",
            "reliability": f"Reliability: {matched_text}",
            "compatibility": f"Compatibility: {matched_text}"
        }
        
        return formats.get(category, matched_text)
    
    def _extract_from_entities(self, entities: Dict[str, Any]) -> List[str]:
        """Extract requirements from entities"""
        
        requirements = []
        
        if entities.get("pages"):
            requirements.append(f"Implementation of {len(entities['pages'])} pages/screens")
        
        if entities.get("components"):
            requirements.append(f"Development of {len(entities['components'])} UI components")
        
        if entities.get("actions"):
            requirements.append(f"Support for {len(entities['actions'])} user actions")
        
        if entities.get("data_models"):
            requirements.append(f"Data models for {', '.join(entities['data_models'])}")
        
        return requirements
    
    def _get_default_requirements(self, project_type: str) -> List[str]:
        """Get default requirements for project type"""
        
        defaults = {
            "web_app": [
                "Responsive design for all screen sizes",
                "Cross-browser compatibility",
                "SEO optimization"
            ],
            "mobile_app": [
                "Native mobile experience",
                "Offline capability",
                "Push notifications"
            ],
            "e_commerce": [
                "Product catalog management",
                "Shopping cart functionality",
                "Order management system",
                "Inventory tracking"
            ],
            "saas": [
                "Multi-tenant architecture",
                "Subscription management",
                "Usage analytics",
                "API access for integrations"
            ],
            "api": [
                "RESTful API design",
                "API documentation",
                "Rate limiting",
                "API versioning"
            ]
        }
        
        return defaults.get(project_type, [])