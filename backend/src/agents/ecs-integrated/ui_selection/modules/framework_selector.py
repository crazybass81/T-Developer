"""
Framework Selector Module
Selects the most appropriate UI framework based on requirements
"""

from typing import Dict, Any, List, Optional

class FrameworkSelector:
    """Selects UI frameworks based on project requirements"""
    
    def __init__(self):
        self.frameworks = {
            "React": {
                "type": "library",
                "ecosystem": "excellent",
                "learning_curve": "moderate",
                "performance": "high",
                "community": "very_large",
                "use_cases": ["spa", "complex_ui", "real_time", "mobile"],
                "strengths": ["component_reusability", "virtual_dom", "ecosystem"],
                "weaknesses": ["setup_complexity", "state_management"],
                "compatible_with": ["Next.js", "Gatsby", "React Native"]
            },
            "Vue": {
                "type": "framework",
                "ecosystem": "good",
                "learning_curve": "easy",
                "performance": "high",
                "community": "large",
                "use_cases": ["spa", "progressive_enhancement", "small_to_medium"],
                "strengths": ["gentle_learning_curve", "flexibility", "documentation"],
                "weaknesses": ["smaller_ecosystem", "enterprise_adoption"],
                "compatible_with": ["Nuxt.js", "Quasar"]
            },
            "Angular": {
                "type": "framework",
                "ecosystem": "comprehensive",
                "learning_curve": "steep",
                "performance": "good",
                "community": "large",
                "use_cases": ["enterprise", "large_scale", "complex_forms"],
                "strengths": ["full_framework", "typescript_first", "tooling"],
                "weaknesses": ["complexity", "bundle_size", "learning_curve"],
                "compatible_with": ["Ionic", "NativeScript"]
            },
            "Svelte": {
                "type": "compiler",
                "ecosystem": "growing",
                "learning_curve": "easy",
                "performance": "excellent",
                "community": "growing",
                "use_cases": ["performance_critical", "small_apps", "widgets"],
                "strengths": ["no_virtual_dom", "small_bundle", "simplicity"],
                "weaknesses": ["smaller_ecosystem", "less_mature"],
                "compatible_with": ["SvelteKit"]
            },
            "Next.js": {
                "type": "meta_framework",
                "ecosystem": "excellent",
                "learning_curve": "moderate",
                "performance": "excellent",
                "community": "large",
                "use_cases": ["ssr", "ssg", "full_stack", "seo"],
                "strengths": ["ssr_ssg", "api_routes", "optimizations"],
                "weaknesses": ["opinionated", "vendor_lock"],
                "compatible_with": ["React"]
            },
            "Nuxt.js": {
                "type": "meta_framework",
                "ecosystem": "good",
                "learning_curve": "moderate",
                "performance": "high",
                "community": "medium",
                "use_cases": ["ssr", "ssg", "full_stack", "seo"],
                "strengths": ["vue_based", "auto_routing", "modules"],
                "weaknesses": ["vue_limited"],
                "compatible_with": ["Vue"]
            },
            "Remix": {
                "type": "meta_framework",
                "ecosystem": "growing",
                "learning_curve": "moderate",
                "performance": "excellent",
                "community": "growing",
                "use_cases": ["ssr", "progressive_enhancement", "forms"],
                "strengths": ["nested_routing", "form_handling", "edge_ready"],
                "weaknesses": ["newer_framework", "smaller_ecosystem"],
                "compatible_with": ["React"]
            }
        }
        
        self.project_type_preferences = {
            "web_app": ["React", "Vue", "Next.js"],
            "e_commerce": ["Next.js", "React", "Nuxt.js"],
            "saas": ["React", "Next.js", "Angular"],
            "enterprise": ["Angular", "React", "Vue"],
            "blog": ["Next.js", "Nuxt.js", "Gatsby"],
            "dashboard": ["React", "Vue", "Angular"],
            "mobile_web": ["React", "Vue", "Svelte"],
            "marketing": ["Next.js", "Nuxt.js", "Gatsby"],
            "admin_panel": ["React", "Vue", "Angular"]
        }
    
    async def initialize(self):
        """Initialize framework selector"""
        pass
    
    async def select(
        self,
        project_type: str,
        requirements: Dict[str, Any],
        tech_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Select the most appropriate framework
        
        Args:
            project_type: Type of project
            requirements: Project requirements
            tech_preferences: Technology preferences
            
        Returns:
            Selected framework with details
        """
        
        # Score each framework
        scores = {}
        for framework_name, framework_info in self.frameworks.items():
            score = self._calculate_framework_score(
                framework_name,
                framework_info,
                project_type,
                requirements,
                tech_preferences
            )
            scores[framework_name] = score
        
        # Select best framework
        best_framework = max(scores.items(), key=lambda x: x[1]["total"])
        framework_name = best_framework[0]
        framework_info = self.frameworks[framework_name]
        
        return {
            "name": framework_name,
            "type": framework_info["type"],
            "match_score": best_framework[1]["total"],
            "score_breakdown": best_framework[1],
            "ecosystem": framework_info["ecosystem"],
            "performance": framework_info["performance"],
            "strengths": framework_info["strengths"],
            "weaknesses": framework_info["weaknesses"],
            "setup_config": self._generate_setup_config(framework_name, requirements),
            "dependencies": self._get_dependencies(framework_name, requirements),
            "build_config": self._get_build_config(framework_name)
        }
    
    def _calculate_framework_score(
        self,
        framework_name: str,
        framework_info: Dict,
        project_type: str,
        requirements: Dict,
        tech_preferences: Optional[Dict]
    ) -> Dict[str, float]:
        """Calculate framework suitability score"""
        
        scores = {
            "project_type": 0.0,
            "requirements": 0.0,
            "performance": 0.0,
            "ecosystem": 0.0,
            "preferences": 0.0,
            "total": 0.0
        }
        
        # Project type match
        if framework_name in self.project_type_preferences.get(project_type, []):
            position = self.project_type_preferences[project_type].index(framework_name)
            scores["project_type"] = 1.0 - (position * 0.2)
        
        # Requirements match
        req_score = 0
        req_count = 0
        
        if requirements.get("seo_important") and framework_info["type"] == "meta_framework":
            req_score += 1
            req_count += 1
        
        if requirements.get("real_time") and framework_name in ["React", "Vue"]:
            req_score += 1
            req_count += 1
        
        if requirements.get("enterprise") and framework_name == "Angular":
            req_score += 1
            req_count += 1
        
        if requirements.get("performance_critical") and framework_name == "Svelte":
            req_score += 1
            req_count += 1
        
        if req_count > 0:
            scores["requirements"] = req_score / req_count
        
        # Performance score
        performance_scores = {
            "excellent": 1.0,
            "high": 0.8,
            "good": 0.6,
            "moderate": 0.4
        }
        scores["performance"] = performance_scores.get(framework_info["performance"], 0.5)
        
        # Ecosystem score
        ecosystem_scores = {
            "excellent": 1.0,
            "comprehensive": 0.9,
            "good": 0.7,
            "growing": 0.5
        }
        scores["ecosystem"] = ecosystem_scores.get(framework_info["ecosystem"], 0.5)
        
        # Preferences match
        if tech_preferences:
            frontend_pref = tech_preferences.get("frontend", [])
            if isinstance(frontend_pref, list) and framework_name in frontend_pref:
                scores["preferences"] = 1.0
            elif isinstance(frontend_pref, str) and framework_name == frontend_pref:
                scores["preferences"] = 1.0
        
        # Calculate total score
        weights = {
            "project_type": 0.3,
            "requirements": 0.25,
            "performance": 0.15,
            "ecosystem": 0.15,
            "preferences": 0.15
        }
        
        scores["total"] = sum(scores[key] * weights[key] for key in weights)
        
        return scores
    
    def _generate_setup_config(self, framework: str, requirements: Dict) -> Dict:
        """Generate framework setup configuration"""
        
        config = {
            "React": {
                "create_command": "npx create-react-app",
                "typescript": requirements.get("typescript", True),
                "state_management": "Redux Toolkit" if requirements.get("complex_state") else "Context API",
                "routing": "React Router",
                "styling": "CSS Modules"
            },
            "Vue": {
                "create_command": "npm create vue@latest",
                "typescript": requirements.get("typescript", False),
                "state_management": "Pinia",
                "routing": "Vue Router",
                "styling": "Scoped CSS"
            },
            "Angular": {
                "create_command": "ng new",
                "typescript": True,
                "state_management": "NgRx" if requirements.get("complex_state") else "Services",
                "routing": "Angular Router",
                "styling": "SCSS"
            },
            "Next.js": {
                "create_command": "npx create-next-app",
                "typescript": requirements.get("typescript", True),
                "state_management": "Zustand",
                "routing": "File-based",
                "styling": "CSS Modules",
                "rendering": "SSR" if requirements.get("seo_important") else "SSG"
            },
            "Svelte": {
                "create_command": "npm create vite@latest",
                "typescript": requirements.get("typescript", False),
                "state_management": "Stores",
                "routing": "SvelteKit",
                "styling": "Scoped styles"
            }
        }
        
        return config.get(framework, {})
    
    def _get_dependencies(self, framework: str, requirements: Dict) -> List[str]:
        """Get framework dependencies"""
        
        base_deps = {
            "React": ["react", "react-dom", "react-router-dom"],
            "Vue": ["vue", "vue-router"],
            "Angular": ["@angular/core", "@angular/common", "@angular/router"],
            "Next.js": ["next", "react", "react-dom"],
            "Svelte": ["svelte"],
            "Nuxt.js": ["nuxt", "vue"],
            "Remix": ["@remix-run/react", "@remix-run/node"]
        }
        
        deps = base_deps.get(framework, [])
        
        # Add conditional dependencies
        if requirements.get("typescript"):
            deps.append("typescript")
            
        if requirements.get("testing"):
            if framework in ["React", "Next.js"]:
                deps.extend(["@testing-library/react", "jest"])
            elif framework == "Vue":
                deps.extend(["@testing-library/vue", "vitest"])
        
        if requirements.get("forms") and framework in ["React", "Next.js"]:
            deps.append("react-hook-form")
        
        return deps
    
    def _get_build_config(self, framework: str) -> Dict:
        """Get build configuration for framework"""
        
        configs = {
            "React": {
                "bundler": "Webpack",
                "dev_server": "webpack-dev-server",
                "build_command": "npm run build",
                "output_dir": "build"
            },
            "Vue": {
                "bundler": "Vite",
                "dev_server": "vite",
                "build_command": "npm run build",
                "output_dir": "dist"
            },
            "Angular": {
                "bundler": "Angular CLI",
                "dev_server": "ng serve",
                "build_command": "ng build",
                "output_dir": "dist"
            },
            "Next.js": {
                "bundler": "Next.js",
                "dev_server": "next dev",
                "build_command": "next build",
                "output_dir": ".next"
            },
            "Svelte": {
                "bundler": "Vite",
                "dev_server": "vite",
                "build_command": "vite build",
                "output_dir": "dist"
            }
        }
        
        return configs.get(framework, {})