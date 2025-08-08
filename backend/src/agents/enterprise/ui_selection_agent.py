"""
Enterprise UI Selection Agent
Selects optimal UI framework based on project requirements
"""

from typing import Dict, Any, Optional, List, Tuple
import asyncio
from datetime import datetime
import json

from .base_agent import EnterpriseBaseAgent, AgentConfig, AgentContext

class EnterpriseUISelectionAgent(EnterpriseBaseAgent):
    """
    UI Framework Selection Agent
    Analyzes requirements and selects the best UI framework/library
    """
    
    def __init__(self):
        config = AgentConfig(
            name="ui_selection_agent",
            version="1.0.0",
            timeout=20,
            retries=3,
            cache_ttl=7200,  # Cache for 2 hours
            rate_limit=200
        )
        super().__init__(config)
        
        # Framework knowledge base
        self.frameworks = {
            "react": {
                "name": "React",
                "type": "library",
                "category": "web",
                "strengths": [
                    "large_ecosystem",
                    "component_reusability",
                    "virtual_dom",
                    "strong_community",
                    "enterprise_ready"
                ],
                "weaknesses": [
                    "learning_curve",
                    "boilerplate",
                    "frequent_updates"
                ],
                "use_cases": [
                    "spa",
                    "complex_ui",
                    "enterprise_apps",
                    "dashboards"
                ],
                "performance_score": 0.85,
                "popularity_score": 0.95,
                "maturity_score": 0.9,
                "ecosystem": {
                    "state_management": ["redux", "mobx", "zustand", "recoil"],
                    "routing": ["react-router", "reach-router"],
                    "ui_libraries": ["material-ui", "ant-design", "chakra-ui"],
                    "build_tools": ["create-react-app", "vite", "next.js"]
                }
            },
            "vue": {
                "name": "Vue.js",
                "type": "framework",
                "category": "web",
                "strengths": [
                    "gentle_learning_curve",
                    "excellent_documentation",
                    "reactive_data_binding",
                    "single_file_components"
                ],
                "weaknesses": [
                    "smaller_ecosystem",
                    "less_enterprise_adoption",
                    "limited_resources"
                ],
                "use_cases": [
                    "small_to_medium_apps",
                    "rapid_prototyping",
                    "progressive_enhancement"
                ],
                "performance_score": 0.88,
                "popularity_score": 0.75,
                "maturity_score": 0.85,
                "ecosystem": {
                    "state_management": ["vuex", "pinia"],
                    "routing": ["vue-router"],
                    "ui_libraries": ["vuetify", "element-ui", "quasar"],
                    "build_tools": ["vue-cli", "vite", "nuxt.js"]
                }
            },
            "angular": {
                "name": "Angular",
                "type": "framework",
                "category": "web",
                "strengths": [
                    "full_framework",
                    "typescript_first",
                    "enterprise_features",
                    "dependency_injection",
                    "cli_tools"
                ],
                "weaknesses": [
                    "steep_learning_curve",
                    "verbose",
                    "large_bundle_size"
                ],
                "use_cases": [
                    "enterprise_apps",
                    "large_teams",
                    "complex_applications"
                ],
                "performance_score": 0.8,
                "popularity_score": 0.7,
                "maturity_score": 0.95,
                "ecosystem": {
                    "state_management": ["ngrx", "akita"],
                    "routing": ["angular-router"],
                    "ui_libraries": ["angular-material", "primeng", "ng-bootstrap"],
                    "build_tools": ["angular-cli", "nx"]
                }
            },
            "svelte": {
                "name": "Svelte",
                "type": "compiler",
                "category": "web",
                "strengths": [
                    "no_virtual_dom",
                    "compile_time_optimization",
                    "small_bundle_size",
                    "simple_syntax"
                ],
                "weaknesses": [
                    "smaller_community",
                    "limited_ecosystem",
                    "less_mature"
                ],
                "use_cases": [
                    "performance_critical",
                    "small_apps",
                    "embedded_widgets"
                ],
                "performance_score": 0.95,
                "popularity_score": 0.5,
                "maturity_score": 0.6,
                "ecosystem": {
                    "state_management": ["svelte/store"],
                    "routing": ["svelte-routing", "svelte-spa-router"],
                    "ui_libraries": ["svelte-material-ui", "carbon-components-svelte"],
                    "build_tools": ["sveltekit", "vite"]
                }
            },
            "nextjs": {
                "name": "Next.js",
                "type": "meta_framework",
                "category": "web",
                "base": "react",
                "strengths": [
                    "ssr_ssg",
                    "file_based_routing",
                    "api_routes",
                    "image_optimization",
                    "vercel_integration"
                ],
                "weaknesses": [
                    "opinionated",
                    "vendor_lock_in_risk"
                ],
                "use_cases": [
                    "seo_critical",
                    "e_commerce",
                    "marketing_sites",
                    "blogs"
                ],
                "performance_score": 0.9,
                "popularity_score": 0.85,
                "maturity_score": 0.85
            },
            "flutter": {
                "name": "Flutter",
                "type": "framework",
                "category": "mobile",
                "strengths": [
                    "cross_platform",
                    "native_performance",
                    "hot_reload",
                    "rich_widgets"
                ],
                "weaknesses": [
                    "dart_language",
                    "large_app_size",
                    "platform_specific_issues"
                ],
                "use_cases": [
                    "mobile_apps",
                    "cross_platform",
                    "mvp"
                ],
                "performance_score": 0.85,
                "popularity_score": 0.7,
                "maturity_score": 0.75
            },
            "react_native": {
                "name": "React Native",
                "type": "framework",
                "category": "mobile",
                "strengths": [
                    "javascript",
                    "code_reuse",
                    "large_community",
                    "live_reload"
                ],
                "weaknesses": [
                    "performance_overhead",
                    "native_module_complexity",
                    "debugging"
                ],
                "use_cases": [
                    "mobile_apps",
                    "rapid_development",
                    "web_to_mobile"
                ],
                "performance_score": 0.75,
                "popularity_score": 0.8,
                "maturity_score": 0.85
            },
            "electron": {
                "name": "Electron",
                "type": "framework",
                "category": "desktop",
                "strengths": [
                    "cross_platform_desktop",
                    "web_technologies",
                    "large_ecosystem"
                ],
                "weaknesses": [
                    "resource_heavy",
                    "large_bundle_size",
                    "security_concerns"
                ],
                "use_cases": [
                    "desktop_apps",
                    "developer_tools",
                    "cross_platform_desktop"
                ],
                "performance_score": 0.6,
                "popularity_score": 0.7,
                "maturity_score": 0.9
            }
        }
        
        # Decision weights
        self.decision_weights = {
            "performance": 0.25,
            "ecosystem": 0.2,
            "community": 0.15,
            "learning_curve": 0.15,
            "project_fit": 0.25
        }
    
    async def process(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Select optimal UI framework based on requirements
        """
        requirements = input_data.get("requirements", {})
        
        if not requirements:
            raise ValueError("No requirements provided for UI selection")
        
        self.logger.info(
            "Selecting UI framework",
            project_type=requirements.get("project_type"),
            trace_id=context.trace_id
        )
        
        # Analyze requirements
        analysis = await self._analyze_requirements(requirements)
        
        # Score frameworks
        scores = await self._score_frameworks(analysis, requirements)
        
        # Select best framework
        selected = await self._select_best_framework(scores, requirements)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            selected,
            scores,
            requirements,
            analysis
        )
        
        return {
            "selected_framework": selected,
            "scores": scores,
            "analysis": analysis,
            "recommendations": recommendations,
            "alternatives": self._get_alternatives(scores, selected),
            "implementation_guide": await self._generate_implementation_guide(selected, requirements)
        }
    
    async def _analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project requirements for UI selection"""
        
        analysis = {
            "project_category": self._determine_category(requirements),
            "complexity_level": requirements.get("estimated_complexity", "medium"),
            "performance_critical": self._is_performance_critical(requirements),
            "seo_required": self._requires_seo(requirements),
            "team_size": self._estimate_team_size(requirements),
            "timeline_pressure": self._assess_timeline_pressure(requirements),
            "existing_expertise": self._detect_existing_expertise(requirements),
            "scalability_needs": self._assess_scalability(requirements),
            "device_targets": self._identify_device_targets(requirements),
            "user_interaction_level": self._assess_interaction_level(requirements)
        }
        
        return analysis
    
    def _determine_category(self, requirements: Dict[str, Any]) -> str:
        """Determine project category"""
        project_type = requirements.get("project_type", "")
        
        category_map = {
            "web_app": "web",
            "mobile_app": "mobile",
            "desktop": "desktop",
            "api": "headless",
            "cli": "headless"
        }
        
        return category_map.get(project_type, "web")
    
    def _is_performance_critical(self, requirements: Dict[str, Any]) -> bool:
        """Check if performance is critical"""
        non_functional = requirements.get("non_functional_requirements", {})
        performance = non_functional.get("performance", {})
        
        # Check for specific performance requirements
        if performance.get("response_time"):
            response_time = performance.get("response_time", "")
            if "ms" in str(response_time):
                try:
                    ms = int(re.findall(r'\d+', str(response_time))[0])
                    return ms < 100
                except:
                    pass
        
        # Check for high concurrent users
        if performance.get("concurrent_users", 0) > 10000:
            return True
        
        # Check for real-time features
        features = requirements.get("features", [])
        real_time_keywords = ["real-time", "realtime", "live", "streaming", "websocket"]
        for feature in features:
            if any(keyword in str(feature).lower() for keyword in real_time_keywords):
                return True
        
        return False
    
    def _requires_seo(self, requirements: Dict[str, Any]) -> bool:
        """Check if SEO is required"""
        # Check project type
        project_type = requirements.get("project_type", "")
        seo_critical_types = ["e-commerce", "blog", "marketing", "content"]
        
        if any(t in project_type.lower() for t in seo_critical_types):
            return True
        
        # Check features
        features = requirements.get("features", [])
        seo_keywords = ["seo", "search engine", "google", "indexing", "crawling"]
        
        for feature in features:
            if any(keyword in str(feature).lower() for keyword in seo_keywords):
                return True
        
        # Check non-functional requirements
        non_functional = requirements.get("non_functional_requirements", {})
        if "seo" in str(non_functional).lower():
            return True
        
        return False
    
    def _estimate_team_size(self, requirements: Dict[str, Any]) -> str:
        """Estimate team size"""
        resources = requirements.get("estimated_resources", {})
        developers = resources.get("developers", 1)
        
        if developers <= 1:
            return "solo"
        elif developers <= 3:
            return "small"
        elif developers <= 10:
            return "medium"
        else:
            return "large"
    
    def _assess_timeline_pressure(self, requirements: Dict[str, Any]) -> str:
        """Assess timeline pressure"""
        constraints = requirements.get("constraints", {})
        timeline = constraints.get("timeline", "")
        
        if "week" in str(timeline).lower():
            weeks = self._extract_number(timeline)
            if weeks and weeks < 4:
                return "high"
            elif weeks and weeks < 12:
                return "medium"
        
        return "low"
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text"""
        import re
        numbers = re.findall(r'\d+', str(text))
        return int(numbers[0]) if numbers else None
    
    def _detect_existing_expertise(self, requirements: Dict[str, Any]) -> List[str]:
        """Detect existing team expertise"""
        tech_reqs = requirements.get("technical_requirements", {})
        frameworks = tech_reqs.get("frameworks", [])
        languages = tech_reqs.get("languages", [])
        
        expertise = []
        
        # Map languages to frameworks
        if "javascript" in languages or "typescript" in languages:
            expertise.extend(["react", "vue", "angular", "svelte"])
        if "dart" in languages:
            expertise.append("flutter")
        
        # Check mentioned frameworks
        for framework in frameworks:
            framework_lower = framework.lower()
            for fw_key in self.frameworks.keys():
                if fw_key in framework_lower:
                    expertise.append(fw_key)
        
        return list(set(expertise))
    
    def _assess_scalability(self, requirements: Dict[str, Any]) -> str:
        """Assess scalability needs"""
        non_functional = requirements.get("non_functional_requirements", {})
        scalability = non_functional.get("scalability", {})
        
        if scalability.get("horizontal") or scalability.get("auto_scaling"):
            return "high"
        
        performance = non_functional.get("performance", {})
        concurrent_users = performance.get("concurrent_users", 0)
        
        if concurrent_users > 10000:
            return "high"
        elif concurrent_users > 1000:
            return "medium"
        
        return "low"
    
    def _identify_device_targets(self, requirements: Dict[str, Any]) -> List[str]:
        """Identify target devices"""
        project_type = requirements.get("project_type", "")
        ui_reqs = requirements.get("ui_requirements", {})
        
        targets = []
        
        if project_type == "web_app":
            targets.append("browser")
            if ui_reqs.get("mobile_friendly") or ui_reqs.get("responsive"):
                targets.append("mobile_browser")
        elif project_type == "mobile_app":
            targets.extend(["ios", "android"])
        elif project_type == "desktop":
            targets.extend(["windows", "mac", "linux"])
        
        return targets if targets else ["browser"]
    
    def _assess_interaction_level(self, requirements: Dict[str, Any]) -> str:
        """Assess user interaction level"""
        features = requirements.get("features", [])
        
        high_interaction_keywords = [
            "real-time", "chat", "collaboration", "drag-drop",
            "interactive", "game", "canvas", "animation", "3d"
        ]
        
        interaction_count = sum(
            1 for feature in features
            if any(keyword in str(feature).lower() for keyword in high_interaction_keywords)
        )
        
        if interaction_count >= 3:
            return "high"
        elif interaction_count >= 1:
            return "medium"
        
        return "low"
    
    async def _score_frameworks(
        self,
        analysis: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, float]:
        """Score each framework based on analysis"""
        
        scores = {}
        category = analysis["project_category"]
        
        for fw_key, fw_data in self.frameworks.items():
            # Skip if wrong category
            if fw_data["category"] != category and category != "headless":
                continue
            
            score = 0.0
            
            # Performance score
            if analysis["performance_critical"]:
                score += fw_data["performance_score"] * self.decision_weights["performance"] * 1.5
            else:
                score += fw_data["performance_score"] * self.decision_weights["performance"]
            
            # Ecosystem score
            ecosystem_size = len(fw_data.get("ecosystem", {}))
            ecosystem_score = min(ecosystem_size / 4, 1.0)  # Normalize to 0-1
            score += ecosystem_score * self.decision_weights["ecosystem"]
            
            # Community score
            score += fw_data["popularity_score"] * self.decision_weights["community"]
            
            # Learning curve score
            if analysis["timeline_pressure"] == "high":
                if "gentle_learning_curve" in fw_data.get("strengths", []):
                    score += 1.0 * self.decision_weights["learning_curve"]
                elif "steep_learning_curve" in fw_data.get("weaknesses", []):
                    score += 0.3 * self.decision_weights["learning_curve"]
                else:
                    score += 0.6 * self.decision_weights["learning_curve"]
            else:
                score += 0.7 * self.decision_weights["learning_curve"]
            
            # Project fit score
            fit_score = await self._calculate_fit_score(fw_key, fw_data, analysis, requirements)
            score += fit_score * self.decision_weights["project_fit"]
            
            # Bonus for existing expertise
            if fw_key in analysis.get("existing_expertise", []):
                score *= 1.2
            
            # Penalty for immature frameworks in enterprise context
            if analysis["complexity_level"] in ["high", "very_high"]:
                if fw_data["maturity_score"] < 0.7:
                    score *= 0.7
            
            scores[fw_key] = round(score, 3)
        
        return scores
    
    async def _calculate_fit_score(
        self,
        fw_key: str,
        fw_data: Dict,
        analysis: Dict,
        requirements: Dict
    ) -> float:
        """Calculate project fit score"""
        
        fit_score = 0.5  # Base score
        
        # Check use cases match
        project_type = requirements.get("project_type", "")
        use_cases = fw_data.get("use_cases", [])
        
        use_case_map = {
            "web_app": ["spa", "complex_ui", "dashboards"],
            "mobile_app": ["mobile_apps", "cross_platform"],
            "desktop": ["desktop_apps", "developer_tools"],
            "e-commerce": ["e_commerce", "seo_critical"],
            "dashboard": ["dashboards", "analytics", "complex_ui"]
        }
        
        for mapped_type, mapped_cases in use_case_map.items():
            if mapped_type in project_type.lower():
                matching_cases = set(use_cases) & set(mapped_cases)
                if matching_cases:
                    fit_score += 0.3
                    break
        
        # SEO requirements
        if analysis["seo_required"]:
            if fw_key in ["nextjs", "nuxtjs"]:
                fit_score += 0.2
            elif fw_key in ["react", "vue", "angular"] and fw_key != "nextjs":
                fit_score -= 0.1
        
        # Team size considerations
        if analysis["team_size"] == "large":
            if "enterprise_ready" in fw_data.get("strengths", []):
                fit_score += 0.15
            if "typescript_first" in fw_data.get("strengths", []):
                fit_score += 0.1
        
        # Interaction level
        if analysis["user_interaction_level"] == "high":
            if fw_data["performance_score"] > 0.85:
                fit_score += 0.15
        
        return min(fit_score, 1.0)
    
    async def _select_best_framework(
        self,
        scores: Dict[str, float],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Select the best framework"""
        
        if not scores:
            # Fallback selection
            project_type = requirements.get("project_type", "web_app")
            if project_type == "mobile_app":
                return self._create_framework_selection("react_native")
            elif project_type == "desktop":
                return self._create_framework_selection("electron")
            else:
                return self._create_framework_selection("react")
        
        # Get highest scoring framework
        best_fw = max(scores, key=scores.get)
        
        return self._create_framework_selection(best_fw)
    
    def _create_framework_selection(self, fw_key: str) -> Dict[str, Any]:
        """Create framework selection object"""
        fw_data = self.frameworks.get(fw_key, {})
        
        return {
            "id": fw_key,
            "name": fw_data.get("name", fw_key),
            "type": fw_data.get("type", "framework"),
            "category": fw_data.get("category", "web"),
            "confidence": 0.85,  # Will be calculated based on score
            "reasons": self._generate_selection_reasons(fw_key, fw_data)
        }
    
    def _generate_selection_reasons(self, fw_key: str, fw_data: Dict) -> List[str]:
        """Generate reasons for selection"""
        reasons = []
        
        if fw_data.get("performance_score", 0) > 0.85:
            reasons.append("Excellent performance characteristics")
        
        if fw_data.get("popularity_score", 0) > 0.8:
            reasons.append("Large community and ecosystem")
        
        if fw_data.get("maturity_score", 0) > 0.85:
            reasons.append("Mature and stable framework")
        
        if "enterprise_ready" in fw_data.get("strengths", []):
            reasons.append("Enterprise-ready with proven track record")
        
        return reasons if reasons else ["Best overall fit for requirements"]
    
    async def _generate_recommendations(
        self,
        selected: Dict[str, Any],
        scores: Dict[str, float],
        requirements: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed recommendations"""
        
        fw_key = selected["id"]
        fw_data = self.frameworks.get(fw_key, {})
        
        recommendations = {
            "primary_framework": selected,
            "ecosystem_recommendations": self._recommend_ecosystem(fw_key, fw_data, requirements),
            "architecture_pattern": self._recommend_architecture(fw_key, analysis),
            "tooling": self._recommend_tooling(fw_key, fw_data),
            "testing_strategy": self._recommend_testing(fw_key),
            "deployment_strategy": self._recommend_deployment(fw_key, requirements),
            "performance_optimizations": self._recommend_optimizations(fw_key, analysis),
            "security_considerations": self._recommend_security(fw_key),
            "monitoring_tools": self._recommend_monitoring(fw_key)
        }
        
        return recommendations
    
    def _recommend_ecosystem(
        self,
        fw_key: str,
        fw_data: Dict,
        requirements: Dict
    ) -> Dict[str, List[str]]:
        """Recommend ecosystem tools"""
        ecosystem = fw_data.get("ecosystem", {})
        
        recommendations = {}
        
        # State management
        if ecosystem.get("state_management"):
            complexity = requirements.get("estimated_complexity", "medium")
            if complexity in ["high", "very_high"]:
                recommendations["state_management"] = ecosystem["state_management"][:1]
            else:
                recommendations["state_management"] = ["context_api"] if fw_key == "react" else []
        
        # UI libraries
        if ecosystem.get("ui_libraries"):
            recommendations["ui_library"] = ecosystem["ui_libraries"][:2]
        
        # Routing
        if ecosystem.get("routing"):
            recommendations["routing"] = ecosystem["routing"][:1]
        
        # Build tools
        if ecosystem.get("build_tools"):
            recommendations["build_tool"] = ecosystem["build_tools"][:1]
        
        return recommendations
    
    def _recommend_architecture(self, fw_key: str, analysis: Dict) -> str:
        """Recommend architecture pattern"""
        complexity = analysis.get("complexity_level", "medium")
        
        architecture_map = {
            "react": {
                "low": "component-based",
                "medium": "container-component",
                "high": "flux-architecture",
                "very_high": "micro-frontends"
            },
            "vue": {
                "low": "single-file-components",
                "medium": "vuex-modular",
                "high": "composition-api",
                "very_high": "micro-frontends"
            },
            "angular": {
                "low": "mvc",
                "medium": "feature-modules",
                "high": "ngrx-store",
                "very_high": "nx-monorepo"
            }
        }
        
        return architecture_map.get(fw_key, {}).get(complexity, "modular")
    
    def _recommend_tooling(self, fw_key: str, fw_data: Dict) -> Dict[str, Any]:
        """Recommend development tooling"""
        return {
            "ide": self._recommend_ide(fw_key),
            "linting": self._recommend_linting(fw_key),
            "formatting": "prettier",
            "debugging": self._recommend_debugging(fw_key),
            "bundler": fw_data.get("ecosystem", {}).get("build_tools", ["webpack"])[0]
        }
    
    def _recommend_ide(self, fw_key: str) -> str:
        """Recommend IDE"""
        ide_map = {
            "react": "vscode",
            "vue": "vscode",
            "angular": "webstorm",
            "svelte": "vscode",
            "flutter": "android_studio",
            "react_native": "vscode"
        }
        return ide_map.get(fw_key, "vscode")
    
    def _recommend_linting(self, fw_key: str) -> str:
        """Recommend linting tool"""
        lint_map = {
            "react": "eslint",
            "vue": "eslint-plugin-vue",
            "angular": "tslint",
            "svelte": "eslint-plugin-svelte3",
            "flutter": "flutter_lints",
            "react_native": "eslint"
        }
        return lint_map.get(fw_key, "eslint")
    
    def _recommend_debugging(self, fw_key: str) -> List[str]:
        """Recommend debugging tools"""
        debug_map = {
            "react": ["react-devtools", "redux-devtools"],
            "vue": ["vue-devtools"],
            "angular": ["augury"],
            "flutter": ["flutter-inspector"],
            "react_native": ["react-native-debugger", "flipper"]
        }
        return debug_map.get(fw_key, ["chrome-devtools"])
    
    def _recommend_testing(self, fw_key: str) -> Dict[str, str]:
        """Recommend testing strategy"""
        testing_map = {
            "react": {
                "unit": "jest",
                "component": "react-testing-library",
                "e2e": "cypress",
                "visual": "storybook"
            },
            "vue": {
                "unit": "jest",
                "component": "vue-test-utils",
                "e2e": "cypress",
                "visual": "storybook"
            },
            "angular": {
                "unit": "jasmine",
                "component": "karma",
                "e2e": "protractor",
                "visual": "storybook"
            },
            "flutter": {
                "unit": "flutter_test",
                "widget": "flutter_test",
                "integration": "integration_test"
            }
        }
        return testing_map.get(fw_key, {"unit": "jest", "e2e": "cypress"})
    
    def _recommend_deployment(self, fw_key: str, requirements: Dict) -> Dict[str, Any]:
        """Recommend deployment strategy"""
        cloud = requirements.get("deployment", {}).get("environment", "cloud")
        
        if fw_key == "nextjs":
            return {
                "platform": "vercel",
                "alternative": "aws_amplify",
                "containerization": "docker",
                "ci_cd": "github_actions"
            }
        elif fw_key in ["react", "vue", "angular", "svelte"]:
            return {
                "platform": "netlify" if cloud != "aws" else "aws_s3_cloudfront",
                "alternative": "vercel",
                "containerization": "docker",
                "ci_cd": "github_actions"
            }
        elif fw_key in ["flutter", "react_native"]:
            return {
                "platform": "app_store_google_play",
                "distribution": "fastlane",
                "ci_cd": "codemagic"
            }
        else:
            return {
                "platform": "aws",
                "containerization": "docker",
                "ci_cd": "github_actions"
            }
    
    def _recommend_optimizations(self, fw_key: str, analysis: Dict) -> List[str]:
        """Recommend performance optimizations"""
        optimizations = []
        
        if analysis.get("performance_critical"):
            optimizations.extend([
                "code_splitting",
                "lazy_loading",
                "tree_shaking",
                "bundle_analysis",
                "cdn_hosting"
            ])
        
        if fw_key == "react":
            optimizations.extend([
                "react.memo",
                "useMemo_useCallback",
                "virtual_scrolling"
            ])
        elif fw_key == "vue":
            optimizations.extend([
                "async_components",
                "keep_alive",
                "v_once_directive"
            ])
        elif fw_key == "angular":
            optimizations.extend([
                "onPush_strategy",
                "trackBy_functions",
                "preloading_strategies"
            ])
        
        return optimizations
    
    def _recommend_security(self, fw_key: str) -> List[str]:
        """Recommend security measures"""
        return [
            "content_security_policy",
            "input_sanitization",
            "xss_protection",
            "dependency_scanning",
            "secure_headers",
            "https_enforcement"
        ]
    
    def _recommend_monitoring(self, fw_key: str) -> List[str]:
        """Recommend monitoring tools"""
        return [
            "sentry",
            "datadog",
            "new_relic",
            "google_analytics",
            "hotjar"
        ]
    
    def _get_alternatives(
        self,
        scores: Dict[str, float],
        selected: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get alternative framework suggestions"""
        alternatives = []
        selected_id = selected["id"]
        
        # Sort frameworks by score
        sorted_frameworks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get top 3 alternatives (excluding selected)
        for fw_key, score in sorted_frameworks:
            if fw_key != selected_id and len(alternatives) < 3:
                fw_data = self.frameworks.get(fw_key, {})
                alternatives.append({
                    "id": fw_key,
                    "name": fw_data.get("name", fw_key),
                    "score": score,
                    "pros": fw_data.get("strengths", [])[:3],
                    "cons": fw_data.get("weaknesses", [])[:2]
                })
        
        return alternatives
    
    async def _generate_implementation_guide(
        self,
        selected: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate implementation guide"""
        fw_key = selected["id"]
        
        return {
            "setup_steps": self._get_setup_steps(fw_key),
            "project_structure": self._get_project_structure(fw_key),
            "best_practices": self._get_best_practices(fw_key),
            "common_pitfalls": self._get_common_pitfalls(fw_key),
            "learning_resources": self._get_learning_resources(fw_key)
        }
    
    def _get_setup_steps(self, fw_key: str) -> List[str]:
        """Get setup steps"""
        setup_map = {
            "react": [
                "npx create-react-app my-app",
                "cd my-app",
                "npm install required-dependencies",
                "npm start"
            ],
            "vue": [
                "npm create vue@latest",
                "cd project-name",
                "npm install",
                "npm run dev"
            ],
            "angular": [
                "npm install -g @angular/cli",
                "ng new my-app",
                "cd my-app",
                "ng serve"
            ],
            "nextjs": [
                "npx create-next-app@latest",
                "cd my-app",
                "npm run dev"
            ]
        }
        return setup_map.get(fw_key, ["npm init", "npm install framework", "npm start"])
    
    def _get_project_structure(self, fw_key: str) -> Dict[str, Any]:
        """Get recommended project structure"""
        return {
            "src": {
                "components": "Reusable UI components",
                "pages": "Page components/routes" if fw_key != "angular" else "Feature modules",
                "services": "API and business logic",
                "utils": "Helper functions",
                "styles": "Global styles",
                "assets": "Static assets"
            },
            "public": "Public assets",
            "tests": "Test files"
        }
    
    def _get_best_practices(self, fw_key: str) -> List[str]:
        """Get best practices"""
        return [
            "Component composition over inheritance",
            "Keep components small and focused",
            "Use proper state management",
            "Implement proper error boundaries",
            "Write comprehensive tests",
            "Document component APIs",
            "Use TypeScript for large projects"
        ]
    
    def _get_common_pitfalls(self, fw_key: str) -> List[str]:
        """Get common pitfalls"""
        pitfalls_map = {
            "react": [
                "Unnecessary re-renders",
                "Direct state mutation",
                "Missing dependency arrays",
                "Not using keys in lists"
            ],
            "vue": [
                "Modifying props directly",
                "Not using computed properties",
                "Forgetting reactivity caveats"
            ],
            "angular": [
                "Not unsubscribing from observables",
                "Overusing two-way binding",
                "Not using OnPush change detection"
            ]
        }
        return pitfalls_map.get(fw_key, ["Framework-specific issues"])
    
    def _get_learning_resources(self, fw_key: str) -> Dict[str, List[str]]:
        """Get learning resources"""
        return {
            "official_docs": [f"https://{fw_key}.dev" if fw_key != "angular" else "https://angular.io"],
            "tutorials": [
                "Official tutorial",
                "YouTube courses",
                "Udemy courses"
            ],
            "communities": [
                "Discord server",
                "Reddit community",
                "Stack Overflow"
            ]
        }