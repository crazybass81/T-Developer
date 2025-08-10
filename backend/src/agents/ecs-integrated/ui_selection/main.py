"""
UI Selection Agent - ECS Integrated Version
Selects appropriate UI frameworks and components based on project requirements
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Base agent import
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent, AgentConfig, AgentContext, AgentResult, AgentStatus

# Module imports
# from .modules.framework_selector import FrameworkSelector  # 임시로 비활성화
FrameworkSelector = None  # 임시 스텁
# from .modules.component_library_matcher import ComponentLibraryMatcher  # 임시로 비활성화
ComponentLibraryMatcher = None  # 임시 스텁
# from .modules.design_system_analyzer import DesignSystemAnalyzer  # 임시로 비활성화
DesignSystemAnalyzer = None  # 임시 스텁
# from .modules.responsive_strategy import ResponsiveStrategy  # 임시로 비활성화
ResponsiveStrategy = None  # 임시 스텁
# from .modules.accessibility_checker import AccessibilityChecker  # 임시로 비활성화
AccessibilityChecker = None  # 임시 스텁
# from .modules.performance_optimizer import PerformanceOptimizer  # 임시로 비활성화
PerformanceOptimizer = None  # 임시 스텁
# from .modules.theme_generator import ThemeGenerator  # 임시로 비활성화
ThemeGenerator = None  # 임시 스텁

@dataclass
class UISelectionResult:
    """Result from UI Selection Agent"""
    framework: Dict[str, Any]
    component_library: Dict[str, Any]
    design_system: Dict[str, Any]
    responsive_config: Dict[str, Any]
    accessibility_config: Dict[str, Any]
    performance_config: Dict[str, Any]
    theme: Dict[str, Any]
    recommendations: List[str]
    estimated_complexity: str
    confidence_score: float

class UISelectionAgent(BaseAgent):
    """
    Selects UI frameworks and components for the project
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize UI Selection Agent with configuration"""
        
        if not config:
            config = AgentConfig(
                name="UISelectionAgent",
                version="2.0.0",
                capabilities=[
                    "framework_selection",
                    "component_library_matching",
                    "design_system_analysis",
                    "responsive_design",
                    "accessibility_compliance",
                    "performance_optimization",
                    "theme_generation"
                ],
                resource_requirements={
                    "cpu": "1 vCPU",
                    "memory": "2GB",
                    "timeout": 300
                },
                service_group="analysis"
            )
        
        super().__init__(config)
        
        # Initialize modules
        self.framework_selector = FrameworkSelector() if FrameworkSelector else None
        self.component_matcher = ComponentLibraryMatcher() if ComponentLibraryMatcher else None
        self.design_analyzer = DesignSystemAnalyzer() if DesignSystemAnalyzer else None
        self.responsive_strategy = ResponsiveStrategy() if ResponsiveStrategy else None
        self.accessibility_checker = AccessibilityChecker() if AccessibilityChecker else None
        self.performance_optimizer = PerformanceOptimizer() if PerformanceOptimizer else None
        self.theme_generator = ThemeGenerator() if ThemeGenerator else None
    
    async def initialize(self) -> bool:
        """Initialize agent and its modules"""
        
        try:
            self.logger.info("Initializing UI Selection Agent modules...")
            
            # Initialize all modules
            await asyncio.gather(
                self.framework_selector.initialize(),
                self.component_matcher.initialize(),
                self.design_analyzer.initialize(),
                self.responsive_strategy.initialize(),
                self.accessibility_checker.initialize(),
                self.performance_optimizer.initialize(),
                self.theme_generator.initialize()
            )
            
            self.status = AgentStatus.READY
            self.logger.info("UI Selection Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize UI Selection Agent: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def _custom_initialize(self):
        """Custom initialization for agent"""
        pass

    async def process(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> AgentResult[UISelectionResult]:
        """
        Process UI selection request
        
        Args:
            input_data: Requirements from NL Input Agent
            context: Processing context
            
        Returns:
            UI selection results
        """
        
        self.status = AgentStatus.PROCESSING
        start_time = datetime.now()
        
        try:
            # Extract requirements
            requirements = input_data.get("requirements", {})
            project_type = requirements.get("project_type", "web_app")
            target_users = requirements.get("target_users", {})
            
            # Step 1: Select framework
            self.logger.info("Selecting UI framework...")
            framework = await self.framework_selector.select(
                project_type=project_type,
                requirements=requirements,
                tech_preferences=requirements.get("technology_preferences", {})
            )
            
            # Step 2: Match component libraries
            self.logger.info("Matching component libraries...")
            component_library = await self.component_matcher.match(
                framework=framework,
                requirements=requirements,
                design_preferences=requirements.get("design_preferences", {})
            )
            
            # Step 3: Analyze design system needs
            self.logger.info("Analyzing design system requirements...")
            design_system = await self.design_analyzer.analyze(
                project_type=project_type,
                brand_guidelines=requirements.get("brand_guidelines", {}),
                target_users=target_users
            )
            
            # Step 4: Create responsive strategy
            self.logger.info("Creating responsive design strategy...")
            responsive_config = await self.responsive_strategy.create(
                target_devices=requirements.get("target_devices", ["desktop", "mobile"]),
                user_demographics=target_users
            )
            
            # Step 5: Check accessibility requirements
            self.logger.info("Checking accessibility compliance...")
            accessibility_config = await self.accessibility_checker.check(
                compliance_level=requirements.get("accessibility_level", "WCAG 2.1 AA"),
                target_users=target_users
            )
            
            # Step 6: Optimize for performance
            self.logger.info("Optimizing performance configuration...")
            performance_config = await self.performance_optimizer.optimize(
                framework=framework,
                target_metrics=requirements.get("performance_metrics", {}),
                expected_traffic=requirements.get("expected_traffic", {})
            )
            
            # Step 7: Generate theme
            self.logger.info("Generating theme configuration...")
            theme = await self.theme_generator.generate(
                brand_colors=requirements.get("brand_colors", {}),
                design_style=requirements.get("design_style", "modern"),
                component_library=component_library
            )
            
            # Step 8: Generate recommendations
            recommendations = self._generate_recommendations(
                framework,
                component_library,
                design_system,
                requirements
            )
            
            # Step 9: Assess complexity
            complexity = self._assess_complexity(
                framework,
                component_library,
                requirements
            )
            
            # Step 10: Calculate confidence
            confidence = self._calculate_confidence(
                framework,
                component_library,
                design_system
            )
            
            # Create result
            result = UISelectionResult(
                framework=framework,
                component_library=component_library,
                design_system=design_system,
                responsive_config=responsive_config,
                accessibility_config=accessibility_config,
                performance_config=performance_config,
                theme=theme,
                recommendations=recommendations,
                estimated_complexity=complexity,
                confidence_score=confidence
            )
            
            # Cache result
            cache_key = f"ui_selection:{context.request_id}"
            await self.cache_result(cache_key, asdict(result))
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.update_metrics({
                "processing_time": processing_time,
                "framework_selected": framework["name"],
                "component_library": component_library["name"],
                "confidence_score": confidence
            })
            
            self.status = AgentStatus.COMPLETED
            self.logger.info(f"UI selection completed in {processing_time:.2f}s")
            
            return AgentResult(
                success=True,
                data=result,
                metadata={
                    "processing_time": processing_time,
                    "confidence": confidence,
                    "complexity": complexity
                }
            )
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"UI selection failed: {e}")
            
            return AgentResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"error_type": type(e).__name__}
            )
    
    def _generate_recommendations(
        self,
        framework: Dict,
        component_library: Dict,
        design_system: Dict,
        requirements: Dict
    ) -> List[str]:
        """Generate UI recommendations"""
        
        recommendations = []
        
        # Framework recommendations
        if framework["name"] == "React":
            recommendations.append("Use React Hooks for state management in functional components")
            if requirements.get("real_time"):
                recommendations.append("Consider React Query for server state management")
        elif framework["name"] == "Vue":
            recommendations.append("Use Composition API for better TypeScript support")
        elif framework["name"] == "Angular":
            recommendations.append("Implement lazy loading for better initial load performance")
        
        # Component library recommendations
        if component_library["name"] == "Material-UI":
            recommendations.append("Customize Material-UI theme to match brand identity")
        elif component_library["name"] == "Ant Design":
            recommendations.append("Use Ant Design Pro for enterprise features")
        elif component_library["name"] == "Tailwind CSS":
            recommendations.append("Create custom component library with Tailwind utilities")
        
        # Design system recommendations
        if design_system.get("custom_needed"):
            recommendations.append("Develop custom design system for brand consistency")
        
        # Performance recommendations
        if requirements.get("expected_traffic", {}).get("concurrent_users", 0) > 1000:
            recommendations.append("Implement code splitting and lazy loading")
            recommendations.append("Use CDN for static assets")
        
        # Accessibility recommendations
        if requirements.get("accessibility_level"):
            recommendations.append("Implement keyboard navigation for all interactive elements")
            recommendations.append("Ensure proper ARIA labels and roles")
        
        # Mobile recommendations
        if "mobile" in requirements.get("target_devices", []):
            recommendations.append("Implement touch-friendly interactions")
            recommendations.append("Optimize for mobile performance with smaller bundles")
        
        return recommendations
    
    def _assess_complexity(
        self,
        framework: Dict,
        component_library: Dict,
        requirements: Dict
    ) -> str:
        """Assess UI implementation complexity"""
        
        complexity_score = 0
        
        # Framework complexity
        framework_complexity = {
            "React": 2,
            "Vue": 1,
            "Angular": 3,
            "Svelte": 1,
            "Next.js": 2
        }
        complexity_score += framework_complexity.get(framework["name"], 2)
        
        # Component library complexity
        if component_library.get("custom_components_needed", 0) > 10:
            complexity_score += 2
        elif component_library.get("custom_components_needed", 0) > 5:
            complexity_score += 1
        
        # Feature complexity
        if requirements.get("real_time"):
            complexity_score += 2
        if requirements.get("offline_support"):
            complexity_score += 2
        if requirements.get("multi_language"):
            complexity_score += 1
        if requirements.get("custom_animations"):
            complexity_score += 1
        
        # Responsiveness complexity
        device_count = len(requirements.get("target_devices", []))
        if device_count > 3:
            complexity_score += 2
        elif device_count > 2:
            complexity_score += 1
        
        # Determine complexity level
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 6:
            return "medium"
        elif complexity_score <= 9:
            return "high"
        else:
            return "very_high"
    
    def _calculate_confidence(
        self,
        framework: Dict,
        component_library: Dict,
        design_system: Dict
    ) -> float:
        """Calculate confidence score for UI selection"""
        
        confidence = 0.5
        
        # Framework confidence
        if framework.get("match_score", 0) > 0.8:
            confidence += 0.2
        elif framework.get("match_score", 0) > 0.6:
            confidence += 0.1
        
        # Component library confidence
        if component_library.get("compatibility_score", 0) > 0.8:
            confidence += 0.15
        elif component_library.get("compatibility_score", 0) > 0.6:
            confidence += 0.08
        
        # Design system confidence
        if design_system.get("clarity_score", 0) > 0.7:
            confidence += 0.1
        
        # Popular combination bonus
        popular_combos = [
            ("React", "Material-UI"),
            ("React", "Ant Design"),
            ("Vue", "Vuetify"),
            ("Angular", "Angular Material")
        ]
        
        if (framework["name"], component_library["name"]) in popular_combos:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data"""
        
        required_fields = ["requirements"]
        for field in required_fields:
            if field not in input_data:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        requirements = input_data["requirements"]
        if not isinstance(requirements, dict):
            self.logger.error("Requirements must be a dictionary")
            return False
        
        return True
    
    async def cleanup(self) -> None:
        """Cleanup agent resources"""
        
        self.logger.info("Cleaning up UI Selection Agent...")
        # Cleanup modules if needed
        pass