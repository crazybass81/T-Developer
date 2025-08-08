"""
Design Pattern Selector Module
Recommends design patterns based on project requirements
"""

from typing import Dict, Any, List, Optional
from enum import Enum

class ArchitecturePattern(Enum):
    MVC = "Model-View-Controller"
    MVP = "Model-View-Presenter"
    MVVM = "Model-View-ViewModel"
    CLEAN = "Clean Architecture"
    HEXAGONAL = "Hexagonal Architecture"
    MICROSERVICES = "Microservices"
    SERVERLESS = "Serverless"
    EVENT_DRIVEN = "Event-Driven"

class DesignPatternSelector:
    """Selects appropriate design patterns"""
    
    def __init__(self):
        self.patterns = {
            ArchitecturePattern.MVC: {
                "use_cases": ["web_apps", "traditional_apps"],
                "pros": ["Simple", "Well-known", "Good separation"],
                "cons": ["Can become complex", "Tight coupling possible"],
                "complexity": "low",
                "scalability": "medium"
            },
            ArchitecturePattern.CLEAN: {
                "use_cases": ["enterprise", "complex_domains"],
                "pros": ["Testable", "Independent of frameworks", "Flexible"],
                "cons": ["Complex", "More code", "Learning curve"],
                "complexity": "high",
                "scalability": "high"
            },
            ArchitecturePattern.MICROSERVICES: {
                "use_cases": ["large_scale", "multiple_teams"],
                "pros": ["Independent deployment", "Technology diversity", "Scalable"],
                "cons": ["Complex", "Network overhead", "Data consistency"],
                "complexity": "very_high",
                "scalability": "very_high"
            }
        }
        
        self.design_patterns = {
            "creational": ["Singleton", "Factory", "Builder", "Prototype"],
            "structural": ["Adapter", "Decorator", "Facade", "Proxy"],
            "behavioral": ["Observer", "Strategy", "Command", "Iterator"]
        }
    
    async def select_architecture(
        self,
        requirements: Dict[str, Any],
        constraints: List[str]
    ) -> Dict[str, Any]:
        """Select architecture pattern"""
        
        # Analyze requirements
        scores = {}
        
        for pattern, config in self.patterns.items():
            score = self._calculate_pattern_score(pattern, requirements, constraints)
            scores[pattern] = score
        
        # Select best pattern
        best_pattern = max(scores.items(), key=lambda x: x[1])
        
        # Get implementation details
        implementation = self._get_implementation_guide(best_pattern[0], requirements)
        
        # Recommend specific design patterns
        recommended_patterns = self._recommend_design_patterns(
            best_pattern[0],
            requirements
        )
        
        return {
            "architecture": best_pattern[0].value,
            "confidence": best_pattern[1],
            "implementation": implementation,
            "design_patterns": recommended_patterns,
            "folder_structure": self._generate_folder_structure(best_pattern[0]),
            "boilerplate": self._generate_boilerplate(best_pattern[0])
        }
    
    def _calculate_pattern_score(
        self,
        pattern: ArchitecturePattern,
        requirements: Dict,
        constraints: List[str]
    ) -> float:
        """Calculate pattern suitability score"""
        
        score = 0.5  # Base score
        config = self.patterns[pattern]
        
        # Check use cases
        project_type = requirements.get("project_type", "")
        if project_type in config["use_cases"]:
            score += 0.2
        
        # Check scalability requirements
        if requirements.get("scalability") == "high":
            if config["scalability"] in ["high", "very_high"]:
                score += 0.15
        
        # Check complexity tolerance
        team_size = requirements.get("team_size", 1)
        if team_size > 5 and config["complexity"] in ["high", "very_high"]:
            score += 0.1
        elif team_size <= 2 and config["complexity"] == "low":
            score += 0.15
        
        # Check constraints
        for constraint in constraints:
            if "simple" in constraint.lower() and config["complexity"] == "low":
                score += 0.1
            elif "enterprise" in constraint.lower() and pattern == ArchitecturePattern.CLEAN:
                score += 0.2
        
        return min(score, 1.0)
    
    def _get_implementation_guide(
        self,
        pattern: ArchitecturePattern,
        requirements: Dict
    ) -> Dict[str, Any]:
        """Get implementation guide for pattern"""
        
        guides = {
            ArchitecturePattern.CLEAN: {
                "layers": [
                    {"name": "Domain", "responsibility": "Business logic and entities"},
                    {"name": "Application", "responsibility": "Use cases and application logic"},
                    {"name": "Infrastructure", "responsibility": "External services and frameworks"},
                    {"name": "Presentation", "responsibility": "UI and API endpoints"}
                ],
                "dependencies": "Inner layers don't depend on outer layers",
                "testing": "Test each layer independently"
            },
            ArchitecturePattern.MICROSERVICES: {
                "services": self._identify_service_boundaries(requirements),
                "communication": "REST or gRPC for sync, Message Queue for async",
                "data": "Database per service pattern",
                "deployment": "Container orchestration with Kubernetes"
            }
        }
        
        return guides.get(pattern, {})
    
    def _recommend_design_patterns(
        self,
        architecture: ArchitecturePattern,
        requirements: Dict
    ) -> Dict[str, List[str]]:
        """Recommend specific design patterns"""
        
        patterns = {
            "creational": [],
            "structural": [],
            "behavioral": []
        }
        
        # Recommend based on requirements
        if requirements.get("multi_tenant"):
            patterns["creational"].append("Factory")
            patterns["structural"].append("Proxy")
        
        if requirements.get("real_time"):
            patterns["behavioral"].append("Observer")
            patterns["behavioral"].append("Pub-Sub")
        
        if requirements.get("complex_workflows"):
            patterns["behavioral"].append("State Machine")
            patterns["behavioral"].append("Chain of Responsibility")
        
        if requirements.get("caching"):
            patterns["structural"].append("Proxy")
            patterns["creational"].append("Singleton")
        
        return patterns
    
    def _generate_folder_structure(self, pattern: ArchitecturePattern) -> Dict[str, str]:
        """Generate folder structure for pattern"""
        
        if pattern == ArchitecturePattern.CLEAN:
            return {
                "src/domain/": "Entities and business rules",
                "src/application/": "Use cases and DTOs",
                "src/infrastructure/": "Database, external services",
                "src/presentation/": "Controllers, views",
                "tests/unit/": "Unit tests for each layer",
                "tests/integration/": "Integration tests"
            }
        elif pattern == ArchitecturePattern.MVC:
            return {
                "src/models/": "Data models and business logic",
                "src/views/": "UI templates and components",
                "src/controllers/": "Request handlers",
                "src/routes/": "Route definitions",
                "src/services/": "Business services",
                "src/utils/": "Utility functions"
            }
        else:
            return {}
    
    def _generate_boilerplate(self, pattern: ArchitecturePattern) -> Dict[str, str]:
        """Generate boilerplate code for pattern"""
        
        # Return code templates for the pattern
        return {}
    
    def _identify_service_boundaries(self, requirements: Dict) -> List[Dict]:
        """Identify microservice boundaries"""
        
        services = []
        
        # Analyze domain entities
        entities = requirements.get("entities", [])
        
        # Group related entities into services
        # This is a simplified example
        if "user" in str(entities).lower():
            services.append({
                "name": "user-service",
                "responsibilities": ["User management", "Authentication"]
            })
        
        if "product" in str(entities).lower():
            services.append({
                "name": "product-service",
                "responsibilities": ["Product catalog", "Inventory"]
            })
        
        if "order" in str(entities).lower():
            services.append({
                "name": "order-service",
                "responsibilities": ["Order processing", "Payment"]
            })
        
        return services
