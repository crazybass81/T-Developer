"""
State Management Advisor Module
Recommends optimal state management solutions based on app complexity
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

class AppComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"

class StateManagementAdvisor:
    """Advises on state management solutions"""
    
    def __init__(self):
        self.solutions = {
            "React": {
                "simple": {
                    "primary": "React Context API",
                    "alternatives": ["useState/useReducer hooks"],
                    "pros": ["Built-in", "No extra dependencies", "Simple API"],
                    "cons": ["Performance issues with frequent updates", "Limited DevTools"],
                    "setup_complexity": "low",
                    "bundle_size": "0KB"
                },
                "moderate": {
                    "primary": "Zustand",
                    "alternatives": ["Jotai", "Valtio"],
                    "pros": ["Small bundle", "Simple API", "TypeScript support", "No boilerplate"],
                    "cons": ["Less ecosystem", "Fewer middleware options"],
                    "setup_complexity": "low",
                    "bundle_size": "8KB"
                },
                "complex": {
                    "primary": "Redux Toolkit",
                    "alternatives": ["MobX", "Recoil"],
                    "pros": ["Predictable state", "Time-travel debugging", "Large ecosystem"],
                    "cons": ["Boilerplate code", "Learning curve", "Bundle size"],
                    "setup_complexity": "medium",
                    "bundle_size": "12KB (RTK) + 2KB (React-Redux)"
                },
                "enterprise": {
                    "primary": "Redux Toolkit + RTK Query",
                    "alternatives": ["MobX State Tree", "Redux + Redux-Saga"],
                    "pros": ["Complete solution", "Cache management", "Optimistic updates"],
                    "cons": ["Complexity", "Bundle size", "Over-engineering risk"],
                    "setup_complexity": "high",
                    "bundle_size": "20KB+"
                }
            },
            "Vue": {
                "simple": {
                    "primary": "Vue Composition API",
                    "alternatives": ["Options API with data()"],
                    "pros": ["Built-in", "Reactive by default", "Simple syntax"],
                    "cons": ["Limited for complex apps"],
                    "setup_complexity": "low",
                    "bundle_size": "0KB"
                },
                "moderate": {
                    "primary": "Pinia",
                    "alternatives": ["Vuex 4"],
                    "pros": ["Official solution", "DevTools support", "TypeScript friendly"],
                    "cons": ["Additional dependency"],
                    "setup_complexity": "low",
                    "bundle_size": "6KB"
                },
                "complex": {
                    "primary": "Pinia + VueUse",
                    "alternatives": ["Vuex with modules"],
                    "pros": ["Composition API support", "Modular", "Tree-shaking"],
                    "cons": ["Multiple libraries to manage"],
                    "setup_complexity": "medium",
                    "bundle_size": "10KB+"
                },
                "enterprise": {
                    "primary": "Pinia + GraphQL (Apollo)",
                    "alternatives": ["Vuex + Vuex-ORM"],
                    "pros": ["Type safety", "Cache management", "Real-time updates"],
                    "cons": ["Complex setup", "Learning curve"],
                    "setup_complexity": "high",
                    "bundle_size": "30KB+"
                }
            },
            "Angular": {
                "simple": {
                    "primary": "Component State",
                    "alternatives": ["Services with BehaviorSubject"],
                    "pros": ["Built-in", "TypeScript native", "RxJS integration"],
                    "cons": ["Limited scope"],
                    "setup_complexity": "low",
                    "bundle_size": "0KB"
                },
                "moderate": {
                    "primary": "Akita",
                    "alternatives": ["NgRx ComponentStore"],
                    "pros": ["Simple API", "Less boilerplate than NgRx"],
                    "cons": ["Smaller community"],
                    "setup_complexity": "medium",
                    "bundle_size": "15KB"
                },
                "complex": {
                    "primary": "NgRx",
                    "alternatives": ["Akita", "NgXS"],
                    "pros": ["Redux pattern", "Powerful effects", "DevTools"],
                    "cons": ["Steep learning curve", "Boilerplate"],
                    "setup_complexity": "high",
                    "bundle_size": "25KB"
                },
                "enterprise": {
                    "primary": "NgRx + NgRx Data",
                    "alternatives": ["NgRx + GraphQL"],
                    "pros": ["Complete solution", "Entity management", "Offline support"],
                    "cons": ["High complexity", "Over-engineering risk"],
                    "setup_complexity": "very high",
                    "bundle_size": "35KB+"
                }
            },
            "Svelte": {
                "simple": {
                    "primary": "Svelte Stores",
                    "alternatives": ["Component state"],
                    "pros": ["Built-in", "Simple API", "No dependencies"],
                    "cons": ["Basic features only"],
                    "setup_complexity": "low",
                    "bundle_size": "0KB"
                },
                "moderate": {
                    "primary": "Svelte Stores + Context",
                    "alternatives": ["svelte-asyncable"],
                    "pros": ["Built on native features", "Good DX"],
                    "cons": ["Manual patterns needed"],
                    "setup_complexity": "low",
                    "bundle_size": "0KB"
                },
                "complex": {
                    "primary": "svelte-state",
                    "alternatives": ["Storeon", "Custom store factories"],
                    "pros": ["Advanced patterns", "Middleware support"],
                    "cons": ["External dependency", "Less mature"],
                    "setup_complexity": "medium",
                    "bundle_size": "5KB"
                },
                "enterprise": {
                    "primary": "Custom State Management",
                    "alternatives": ["Port from other frameworks"],
                    "pros": ["Tailored solution", "Full control"],
                    "cons": ["Maintenance burden", "No community support"],
                    "setup_complexity": "high",
                    "bundle_size": "Varies"
                }
            }
        }
        
        self.complexity_factors = {
            "data_flow": {
                "unidirectional": 0,
                "bidirectional": 1,
                "multi_directional": 2
            },
            "component_depth": {
                "shallow": 0,  # 1-2 levels
                "moderate": 1,  # 3-4 levels
                "deep": 2  # 5+ levels
            },
            "state_sources": {
                "single": 0,
                "few": 1,  # 2-3 sources
                "many": 2  # 4+ sources
            },
            "update_frequency": {
                "rare": 0,
                "moderate": 1,
                "frequent": 2
            },
            "data_relationships": {
                "independent": 0,
                "some_relations": 1,
                "highly_related": 2
            }
        }
    
    async def recommend(
        self,
        framework: str,
        requirements: Dict[str, Any],
        app_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend state management solution
        
        Args:
            framework: UI framework being used
            requirements: App requirements
            app_metrics: Metrics about app structure
            
        Returns:
            State management recommendation
        """
        
        # Assess complexity
        complexity = self._assess_complexity(requirements, app_metrics)
        
        # Get framework-specific solutions
        framework_solutions = self.solutions.get(framework, self.solutions["React"])
        
        # Get recommendation for complexity level
        recommendation = framework_solutions[complexity.value]
        
        # Enhance with specific features
        enhanced = self._enhance_recommendation(
            recommendation,
            framework,
            requirements,
            complexity
        )
        
        # Add implementation guide
        enhanced["implementation_guide"] = self._generate_implementation_guide(
            framework,
            recommendation["primary"],
            requirements
        )
        
        # Add migration path
        enhanced["migration_path"] = self._generate_migration_path(
            framework,
            complexity
        )
        
        # Add performance considerations
        enhanced["performance_tips"] = self._get_performance_tips(
            recommendation["primary"],
            requirements
        )
        
        return enhanced
    
    def _assess_complexity(
        self,
        requirements: Dict[str, Any],
        app_metrics: Optional[Dict[str, Any]]
    ) -> AppComplexity:
        """Assess application complexity"""
        
        score = 0
        
        # Check requirements
        if requirements.get("real_time"):
            score += 2
        
        if requirements.get("offline_support"):
            score += 2
        
        if requirements.get("multi_tenant"):
            score += 3
        
        if requirements.get("collaborative_features"):
            score += 2
        
        # Check app metrics if provided
        if app_metrics:
            # Component count
            component_count = app_metrics.get("component_count", 0)
            if component_count > 50:
                score += 3
            elif component_count > 20:
                score += 2
            elif component_count > 10:
                score += 1
            
            # Data flow complexity
            data_flow = app_metrics.get("data_flow", "unidirectional")
            score += self.complexity_factors["data_flow"].get(data_flow, 0)
            
            # Component depth
            depth = app_metrics.get("component_depth", "shallow")
            score += self.complexity_factors["component_depth"].get(depth, 0)
        
        # Check features
        features = requirements.get("features", [])
        complex_features = [
            "real-time collaboration",
            "offline sync",
            "undo/redo",
            "time travel",
            "optimistic updates",
            "complex forms",
            "wizard flows"
        ]
        
        for feature in complex_features:
            if any(feature in str(f).lower() for f in features):
                score += 1
        
        # Determine complexity level
        if score <= 2:
            return AppComplexity.SIMPLE
        elif score <= 5:
            return AppComplexity.MODERATE
        elif score <= 8:
            return AppComplexity.COMPLEX
        else:
            return AppComplexity.ENTERPRISE
    
    def _enhance_recommendation(
        self,
        base_recommendation: Dict,
        framework: str,
        requirements: Dict,
        complexity: AppComplexity
    ) -> Dict[str, Any]:
        """Enhance recommendation with specific features"""
        
        enhanced = base_recommendation.copy()
        
        # Add middleware recommendations
        enhanced["middleware"] = []
        
        if requirements.get("logging"):
            enhanced["middleware"].append({
                "name": "Logger Middleware",
                "purpose": "Development debugging",
                "library": "redux-logger" if "Redux" in base_recommendation["primary"] else "custom"
            })
        
        if requirements.get("persistence"):
            enhanced["middleware"].append({
                "name": "Persistence",
                "purpose": "Local storage sync",
                "library": "redux-persist" if "Redux" in base_recommendation["primary"] else "custom"
            })
        
        if requirements.get("real_time"):
            enhanced["middleware"].append({
                "name": "WebSocket Integration",
                "purpose": "Real-time updates",
                "library": "socket.io-client integration"
            })
        
        # Add DevTools recommendations
        enhanced["devtools"] = self._get_devtools_recommendations(
            base_recommendation["primary"],
            framework
        )
        
        # Add testing recommendations
        enhanced["testing"] = {
            "unit_testing": self._get_testing_approach(base_recommendation["primary"]),
            "mocking": "Mock store providers",
            "integration": "Testing Library with store providers"
        }
        
        # Add TypeScript configuration
        if requirements.get("typescript"):
            enhanced["typescript_config"] = self._get_typescript_config(
                base_recommendation["primary"],
                framework
            )
        
        return enhanced
    
    def _generate_implementation_guide(
        self,
        framework: str,
        solution: str,
        requirements: Dict
    ) -> Dict[str, Any]:
        """Generate implementation guide"""
        
        guide = {
            "setup_steps": [],
            "folder_structure": {},
            "code_examples": {},
            "best_practices": []
        }
        
        if "Redux" in solution:
            guide["setup_steps"] = [
                "Install @reduxjs/toolkit and react-redux",
                "Create store configuration",
                "Set up root reducer",
                "Wrap app with Provider",
                "Create feature slices"
            ]
            
            guide["folder_structure"] = {
                "store/": "Redux store configuration",
                "store/slices/": "Feature slices",
                "store/middleware/": "Custom middleware",
                "store/selectors/": "Reusable selectors"
            }
            
            guide["best_practices"] = [
                "Use Redux Toolkit for less boilerplate",
                "Normalize state shape",
                "Use selectors for derived state",
                "Keep components connected at appropriate level"
            ]
        
        elif "Zustand" in solution:
            guide["setup_steps"] = [
                "Install zustand",
                "Create store files",
                "Define store with types",
                "Use hooks in components"
            ]
            
            guide["folder_structure"] = {
                "stores/": "Zustand stores",
                "stores/types/": "TypeScript types",
                "stores/actions/": "Complex actions"
            }
            
            guide["best_practices"] = [
                "Use TypeScript for type safety",
                "Split stores by domain",
                "Use immer for immutable updates",
                "Implement devtools in development"
            ]
        
        elif "Context" in solution:
            guide["setup_steps"] = [
                "Create context providers",
                "Define context hooks",
                "Wrap app with providers",
                "Use contexts in components"
            ]
            
            guide["folder_structure"] = {
                "contexts/": "Context definitions",
                "hooks/": "Custom hooks for contexts",
                "providers/": "Provider components"
            }
            
            guide["best_practices"] = [
                "Split contexts by concern",
                "Memoize context values",
                "Use custom hooks for context access",
                "Avoid unnecessary re-renders"
            ]
        
        return guide
    
    def _generate_migration_path(
        self,
        framework: str,
        complexity: AppComplexity
    ) -> List[Dict[str, str]]:
        """Generate migration path for scaling"""
        
        if complexity == AppComplexity.SIMPLE:
            return [
                {
                    "from": "Component State",
                    "to": "Context API",
                    "when": "State needs to be shared across components"
                },
                {
                    "from": "Context API",
                    "to": "Zustand/Jotai",
                    "when": "Performance issues or need for better DX"
                },
                {
                    "from": "Zustand/Jotai",
                    "to": "Redux Toolkit",
                    "when": "Need for time-travel debugging or complex async"
                }
            ]
        elif complexity == AppComplexity.MODERATE:
            return [
                {
                    "from": "Zustand",
                    "to": "Redux Toolkit",
                    "when": "Team growth or need for stricter patterns"
                },
                {
                    "from": "Redux Toolkit",
                    "to": "Redux Toolkit + RTK Query",
                    "when": "Complex server state management needed"
                }
            ]
        else:
            return [
                {
                    "from": "Current Solution",
                    "to": "Micro-frontends",
                    "when": "Teams need independent deployment"
                },
                {
                    "from": "Single Store",
                    "to": "Domain Stores",
                    "when": "Performance or team boundaries require it"
                }
            ]
    
    def _get_performance_tips(
        self,
        solution: str,
        requirements: Dict
    ) -> List[str]:
        """Get performance optimization tips"""
        
        tips = []
        
        if "Redux" in solution:
            tips.extend([
                "Use reselect for memoized selectors",
                "Normalize state to avoid deep updates",
                "Use Redux Toolkit's createEntityAdapter",
                "Implement code splitting for reducers"
            ])
        
        if "Context" in solution:
            tips.extend([
                "Split contexts to minimize re-renders",
                "Use useMemo and useCallback appropriately",
                "Consider using use-context-selector library",
                "Avoid putting frequently changing values in context"
            ])
        
        if requirements.get("real_time"):
            tips.append("Debounce/throttle real-time updates")
            tips.append("Use optimistic updates for better UX")
        
        if requirements.get("large_lists"):
            tips.append("Implement virtualization for large lists")
            tips.append("Use pagination or infinite scroll")
        
        return tips
    
    def _get_devtools_recommendations(
        self,
        solution: str,
        framework: str
    ) -> Dict[str, Any]:
        """Get DevTools recommendations"""
        
        if "Redux" in solution:
            return {
                "browser_extension": "Redux DevTools",
                "features": ["Time travel", "Action replay", "State diff"],
                "setup": "Automatic with Redux Toolkit"
            }
        elif "Zustand" in solution:
            return {
                "browser_extension": "Redux DevTools (compatible)",
                "features": ["State inspection", "Action logging"],
                "setup": "Add devtools middleware"
            }
        elif "MobX" in solution:
            return {
                "browser_extension": "MobX DevTools",
                "features": ["Dependency tree", "Action logging"],
                "setup": "Install mobx-devtools"
            }
        else:
            return {
                "browser_extension": "React/Vue/Angular DevTools",
                "features": ["Component tree", "Props inspection"],
                "setup": "Install framework DevTools"
            }
    
    def _get_testing_approach(self, solution: str) -> str:
        """Get testing approach for solution"""
        
        if "Redux" in solution:
            return "Test reducers, actions, and selectors separately"
        elif "Zustand" in solution:
            return "Test stores with mock implementations"
        elif "Context" in solution:
            return "Test with custom render wrapper providing context"
        else:
            return "Test components with mocked state"
    
    def _get_typescript_config(
        self,
        solution: str,
        framework: str
    ) -> Dict[str, Any]:
        """Get TypeScript configuration"""
        
        return {
            "strict_mode": True,
            "type_definitions": f"@types/{solution.lower().replace(' ', '-')}",
            "patterns": [
                "Define action types as const",
                "Use discriminated unions for actions",
                "Type selector return values",
                "Use generics for reusable patterns"
            ]
        }