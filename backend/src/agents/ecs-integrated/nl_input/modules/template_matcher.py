"""
Template Matcher Module  
Matches project descriptions against predefined project templates
"""

from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass

@dataclass
class ProjectTemplate:
    """Project template definition"""
    id: str
    name: str
    category: str
    description: str
    keywords: List[str]
    required_features: List[str]
    optional_features: List[str]
    tech_stack: Dict[str, List[str]]
    estimated_effort: str
    complexity: str

class TemplateMatcher:
    """Matches projects against predefined templates"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.feature_weights = {
            "required": 1.0,
            "optional": 0.5,
            "keyword": 0.3,
            "tech_stack": 0.4
        }
    
    def _initialize_templates(self) -> List[ProjectTemplate]:
        """Initialize project templates"""
        
        return [
            ProjectTemplate(
                id="ecommerce_standard",
                name="Standard E-commerce Platform",
                category="e_commerce",
                description="Full-featured online store with cart, checkout, and payment",
                keywords=["shop", "store", "product", "cart", "checkout", "payment", "order"],
                required_features=[
                    "Product catalog",
                    "Shopping cart",
                    "User authentication",
                    "Payment processing",
                    "Order management"
                ],
                optional_features=[
                    "Inventory tracking",
                    "Reviews and ratings",
                    "Wishlist",
                    "Discount codes",
                    "Email notifications"
                ],
                tech_stack={
                    "frontend": ["React", "Next.js"],
                    "backend": ["Node.js", "Express"],
                    "database": ["PostgreSQL"],
                    "payment": ["Stripe"]
                },
                estimated_effort="3-4 months",
                complexity="medium-high"
            ),
            ProjectTemplate(
                id="saas_b2b",
                name="B2B SaaS Platform",
                category="saas",
                description="Multi-tenant SaaS with subscription billing",
                keywords=["saas", "subscription", "tenant", "billing", "dashboard", "analytics"],
                required_features=[
                    "Multi-tenancy",
                    "User authentication",
                    "Subscription management",
                    "Admin dashboard",
                    "API access"
                ],
                optional_features=[
                    "Usage analytics",
                    "Team collaboration",
                    "Webhooks",
                    "White-labeling",
                    "SSO integration"
                ],
                tech_stack={
                    "frontend": ["React", "TypeScript"],
                    "backend": ["Node.js", "Express"],
                    "database": ["PostgreSQL", "Redis"],
                    "auth": ["Auth0"]
                },
                estimated_effort="4-6 months",
                complexity="high"
            ),
            ProjectTemplate(
                id="social_platform",
                name="Social Media Platform",
                category="social",
                description="Social networking with posts, comments, and messaging",
                keywords=["social", "post", "comment", "like", "follow", "message", "feed"],
                required_features=[
                    "User profiles",
                    "Post creation",
                    "Comments and likes",
                    "Follow system",
                    "News feed"
                ],
                optional_features=[
                    "Direct messaging",
                    "Stories",
                    "Groups",
                    "Notifications",
                    "Search"
                ],
                tech_stack={
                    "frontend": ["React", "TypeScript"],
                    "backend": ["Node.js", "GraphQL"],
                    "database": ["PostgreSQL", "Redis"],
                    "realtime": ["WebSocket"]
                },
                estimated_effort="4-5 months",
                complexity="high"
            ),
            ProjectTemplate(
                id="blog_cms",
                name="Blog/CMS Platform",
                category="content",
                description="Content management system with blog functionality",
                keywords=["blog", "article", "post", "content", "cms", "publish", "editor"],
                required_features=[
                    "Content editor",
                    "Post management",
                    "Categories and tags",
                    "User authentication",
                    "Comments"
                ],
                optional_features=[
                    "SEO optimization",
                    "Media library",
                    "Draft/publish workflow",
                    "Multi-author support",
                    "RSS feed"
                ],
                tech_stack={
                    "frontend": ["Next.js", "React"],
                    "backend": ["Node.js", "Express"],
                    "database": ["PostgreSQL"],
                    "cms": ["Markdown", "MDX"]
                },
                estimated_effort="2-3 months",
                complexity="medium"
            ),
            ProjectTemplate(
                id="marketplace",
                name="Two-sided Marketplace",
                category="marketplace",
                description="Platform connecting buyers and sellers",
                keywords=["marketplace", "vendor", "seller", "buyer", "listing", "commission"],
                required_features=[
                    "Vendor registration",
                    "Product listings",
                    "Search and filter",
                    "Payment splitting",
                    "Reviews system"
                ],
                optional_features=[
                    "Vendor dashboard",
                    "Commission management",
                    "Dispute resolution",
                    "Featured listings",
                    "Analytics"
                ],
                tech_stack={
                    "frontend": ["React", "TypeScript"],
                    "backend": ["Node.js", "Express"],
                    "database": ["PostgreSQL"],
                    "payment": ["Stripe Connect"]
                },
                estimated_effort="4-5 months",
                complexity="high"
            ),
            ProjectTemplate(
                id="booking_system",
                name="Booking/Reservation System",
                category="booking",
                description="Appointment or resource booking platform",
                keywords=["booking", "appointment", "reservation", "schedule", "calendar", "availability"],
                required_features=[
                    "Calendar view",
                    "Availability management",
                    "Booking creation",
                    "Email confirmations",
                    "User accounts"
                ],
                optional_features=[
                    "Payment processing",
                    "Recurring bookings",
                    "Waitlist",
                    "SMS reminders",
                    "Google Calendar sync"
                ],
                tech_stack={
                    "frontend": ["React", "TypeScript"],
                    "backend": ["Node.js", "Express"],
                    "database": ["PostgreSQL"],
                    "calendar": ["FullCalendar"]
                },
                estimated_effort="2-3 months",
                complexity="medium"
            ),
            ProjectTemplate(
                id="learning_platform",
                name="E-learning Platform",
                category="education",
                description="Online learning management system",
                keywords=["course", "learning", "education", "student", "teacher", "lesson", "quiz"],
                required_features=[
                    "Course creation",
                    "Video hosting",
                    "Progress tracking",
                    "Quiz system",
                    "Certificates"
                ],
                optional_features=[
                    "Live sessions",
                    "Discussion forums",
                    "Assignments",
                    "Grade book",
                    "Payment integration"
                ],
                tech_stack={
                    "frontend": ["React", "TypeScript"],
                    "backend": ["Node.js", "Express"],
                    "database": ["PostgreSQL"],
                    "video": ["AWS S3", "CloudFront"]
                },
                estimated_effort="4-6 months",
                complexity="high"
            ),
            ProjectTemplate(
                id="dashboard_analytics",
                name="Analytics Dashboard",
                category="analytics",
                description="Data visualization and analytics platform",
                keywords=["dashboard", "analytics", "chart", "graph", "report", "metrics", "kpi"],
                required_features=[
                    "Data visualization",
                    "Custom dashboards",
                    "Report generation",
                    "Data filtering",
                    "Export functionality"
                ],
                optional_features=[
                    "Real-time updates",
                    "Scheduled reports",
                    "Alert system",
                    "API integration",
                    "Custom widgets"
                ],
                tech_stack={
                    "frontend": ["React", "D3.js"],
                    "backend": ["Node.js", "Express"],
                    "database": ["PostgreSQL", "InfluxDB"],
                    "charts": ["Chart.js", "Recharts"]
                },
                estimated_effort="3-4 months",
                complexity="medium-high"
            ),
            ProjectTemplate(
                id="crm_system",
                name="Customer Relationship Management",
                category="business",
                description="CRM system for managing customer relationships",
                keywords=["crm", "customer", "contact", "lead", "deal", "pipeline", "sales"],
                required_features=[
                    "Contact management",
                    "Lead tracking",
                    "Deal pipeline",
                    "Activity logging",
                    "Reports"
                ],
                optional_features=[
                    "Email integration",
                    "Calendar sync",
                    "Task automation",
                    "Custom fields",
                    "API webhooks"
                ],
                tech_stack={
                    "frontend": ["React", "TypeScript"],
                    "backend": ["Node.js", "Express"],
                    "database": ["PostgreSQL"],
                    "email": ["SendGrid"]
                },
                estimated_effort="3-5 months",
                complexity="medium-high"
            ),
            ProjectTemplate(
                id="mobile_app",
                name="Cross-platform Mobile App",
                category="mobile",
                description="Mobile application for iOS and Android",
                keywords=["mobile", "app", "ios", "android", "native", "push", "offline"],
                required_features=[
                    "User authentication",
                    "Push notifications",
                    "Offline support",
                    "API integration",
                    "App store deployment"
                ],
                optional_features=[
                    "In-app purchases",
                    "Social sharing",
                    "Camera integration",
                    "Location services",
                    "Biometric auth"
                ],
                tech_stack={
                    "mobile": ["React Native", "TypeScript"],
                    "backend": ["Node.js", "Express"],
                    "database": ["PostgreSQL"],
                    "push": ["Firebase"]
                },
                estimated_effort="3-4 months",
                complexity="medium-high"
            )
        ]
    
    async def match(
        self,
        description: str,
        project_type: str,
        requirements: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Match description against templates
        
        Args:
            description: Project description
            project_type: Identified project type
            requirements: Extracted requirements
            
        Returns:
            Best matching templates with scores
        """
        
        # Calculate scores for each template
        scores = []
        for template in self.templates:
            score = await self._calculate_match_score(
                template,
                description,
                project_type,
                requirements
            )
            scores.append((template, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1]["total"], reverse=True)
        
        # Get top matches
        top_matches = scores[:3]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(top_matches[0] if top_matches else None)
        
        return {
            "best_match": self._format_match(top_matches[0]) if top_matches else None,
            "alternative_matches": [self._format_match(m) for m in top_matches[1:3]],
            "recommendations": recommendations,
            "customization_needed": self._assess_customization(top_matches[0] if top_matches else None, requirements)
        }
    
    async def _calculate_match_score(
        self,
        template: ProjectTemplate,
        description: str,
        project_type: str,
        requirements: Dict
    ) -> Dict[str, float]:
        """Calculate match score for a template"""
        
        scores = {
            "keyword": 0.0,
            "features": 0.0,
            "tech_stack": 0.0,
            "category": 0.0,
            "total": 0.0
        }
        
        description_lower = description.lower()
        
        # Keyword matching
        keyword_matches = sum(1 for kw in template.keywords if kw in description_lower)
        scores["keyword"] = (keyword_matches / len(template.keywords)) if template.keywords else 0
        
        # Feature matching
        required_matches = 0
        optional_matches = 0
        
        req_text = str(requirements).lower()
        
        for feature in template.required_features:
            if any(word in req_text for word in feature.lower().split()):
                required_matches += 1
        
        for feature in template.optional_features:
            if any(word in req_text for word in feature.lower().split()):
                optional_matches += 1
        
        if template.required_features:
            scores["features"] = (
                (required_matches / len(template.required_features)) * self.feature_weights["required"] +
                (optional_matches / len(template.optional_features)) * self.feature_weights["optional"]
                if template.optional_features else 0
            )
        
        # Tech stack matching
        tech_matches = 0
        tech_total = 0
        
        for category, techs in template.tech_stack.items():
            tech_total += len(techs)
            for tech in techs:
                if tech.lower() in description_lower:
                    tech_matches += 1
        
        scores["tech_stack"] = (tech_matches / tech_total) if tech_total > 0 else 0
        
        # Category matching
        if template.category == project_type:
            scores["category"] = 1.0
        elif self._are_categories_related(template.category, project_type):
            scores["category"] = 0.5
        
        # Calculate total score
        scores["total"] = (
            scores["keyword"] * self.feature_weights["keyword"] +
            scores["features"] * 0.4 +
            scores["tech_stack"] * self.feature_weights["tech_stack"] +
            scores["category"] * 0.3
        )
        
        return scores
    
    def _are_categories_related(self, cat1: str, cat2: str) -> bool:
        """Check if two categories are related"""
        
        related = {
            "e_commerce": ["marketplace", "saas"],
            "marketplace": ["e_commerce"],
            "social": ["content"],
            "content": ["social", "education"],
            "education": ["content"],
            "business": ["saas", "analytics"],
            "analytics": ["business"]
        }
        
        return cat2 in related.get(cat1, [])
    
    def _format_match(self, match: Tuple[ProjectTemplate, Dict]) -> Dict:
        """Format template match for output"""
        
        template, scores = match
        
        return {
            "template_id": template.id,
            "name": template.name,
            "description": template.description,
            "match_score": round(scores["total"], 2),
            "score_breakdown": {
                "keyword_match": round(scores["keyword"], 2),
                "feature_match": round(scores["features"], 2),
                "tech_match": round(scores["tech_stack"], 2),
                "category_match": round(scores["category"], 2)
            },
            "required_features": template.required_features,
            "optional_features": template.optional_features,
            "suggested_tech_stack": template.tech_stack,
            "estimated_effort": template.estimated_effort,
            "complexity": template.complexity
        }
    
    def _generate_recommendations(self, best_match: Optional[Tuple]) -> List[str]:
        """Generate recommendations based on template match"""
        
        if not best_match:
            return [
                "No strong template match found - consider custom implementation",
                "Break down requirements into smaller, more specific features",
                "Consider starting with an MVP approach"
            ]
        
        template, scores = best_match
        recommendations = []
        
        if scores["total"] > 0.8:
            recommendations.append(f"Strong match with {template.name} template - use as foundation")
        elif scores["total"] > 0.6:
            recommendations.append(f"Moderate match with {template.name} - customize as needed")
        else:
            recommendations.append(f"Weak match - consider hybrid approach or custom solution")
        
        if scores["features"] < 0.5:
            recommendations.append("Many custom features needed - plan for extended development")
        
        if scores["tech_stack"] < 0.3:
            recommendations.append("Consider adopting suggested tech stack for better compatibility")
        
        # Add template-specific recommendations
        if template.category == "e_commerce":
            recommendations.append("Implement PCI compliance for payment processing")
        elif template.category == "saas":
            recommendations.append("Design for multi-tenancy from the start")
        elif template.category == "social":
            recommendations.append("Plan for scalability and real-time features")
        
        return recommendations
    
    def _assess_customization(
        self,
        best_match: Optional[Tuple],
        requirements: Dict
    ) -> Dict[str, any]:
        """Assess customization needed beyond template"""
        
        if not best_match:
            return {
                "level": "high",
                "description": "Fully custom implementation required",
                "areas": ["All components"]
            }
        
        template, scores = best_match
        
        # Determine customization level
        if scores["total"] > 0.8:
            level = "low"
            description = "Minor customizations to template"
        elif scores["total"] > 0.6:
            level = "medium"
            description = "Moderate customizations required"
        else:
            level = "high"
            description = "Significant customizations needed"
        
        # Identify customization areas
        areas = []
        
        if scores["features"] < 0.7:
            areas.append("Additional feature development")
        
        if scores["tech_stack"] < 0.5:
            areas.append("Technology stack modifications")
        
        # Check for features not in template
        req_text = str(requirements).lower()
        template_features = " ".join(template.required_features + template.optional_features).lower()
        
        custom_features = []
        common_features = ["api", "dashboard", "reports", "notifications", "search"]
        
        for feature in common_features:
            if feature in req_text and feature not in template_features:
                custom_features.append(feature)
        
        if custom_features:
            areas.append(f"Custom features: {', '.join(custom_features)}")
        
        return {
            "level": level,
            "description": description,
            "areas": areas,
            "estimated_additional_effort": self._estimate_additional_effort(level)
        }
    
    def _estimate_additional_effort(self, level: str) -> str:
        """Estimate additional effort based on customization level"""
        
        efforts = {
            "low": "10-20% additional time",
            "medium": "30-50% additional time",
            "high": "60-100% additional time"
        }
        
        return efforts.get(level, "Variable based on requirements")