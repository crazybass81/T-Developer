"""
Optimization Engine Module for Generation Agent
Optimizes generated code for performance, bundle size, and efficiency
"""

from typing import Dict, List, Any, Optional, Tuple, Set, Union
import asyncio
import json
import re
import ast
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import hashlib


class OptimizationType(Enum):
    BUNDLE_SIZE = "bundle_size"
    RUNTIME_PERFORMANCE = "runtime_performance"
    BUILD_TIME = "build_time"
    MEMORY_USAGE = "memory_usage"
    NETWORK_OPTIMIZATION = "network_optimization"
    CODE_SPLITTING = "code_splitting"
    TREE_SHAKING = "tree_shaking"
    MINIFICATION = "minification"
    COMPRESSION = "compression"
    CACHING = "caching"


@dataclass
class OptimizationAction:
    type: OptimizationType
    description: str
    file_path: str
    original_code: str
    optimized_code: str
    impact_score: float  # 0-100
    estimated_improvement: str
    trade_offs: List[str]


@dataclass
class OptimizationMetrics:
    bundle_size_reduction: float  # Percentage
    performance_improvement: float  # Percentage
    build_time_improvement: float  # Percentage
    memory_savings: float  # Percentage
    network_requests_reduced: int
    code_duplication_removed: float  # Percentage
    unused_code_removed: float  # Percentage
    compression_ratio: float


@dataclass
class OptimizationResult:
    success: bool
    actions_applied: List[OptimizationAction]
    metrics: OptimizationMetrics
    optimized_files: Dict[str, str]
    configuration_updates: Dict[str, Any]
    overall_improvement: float
    recommendations: List[str]
    processing_time: float
    metadata: Dict[str, Any]
    error: str = ""


class OptimizationEngine:
    """Advanced code optimization engine"""

    def __init__(self):
        self.version = "1.0.0"

        # Optimization strategies by framework
        self.optimization_strategies = {
            "react": [
                OptimizationType.CODE_SPLITTING,
                OptimizationType.TREE_SHAKING,
                OptimizationType.BUNDLE_SIZE,
                OptimizationType.RUNTIME_PERFORMANCE,
                OptimizationType.CACHING,
            ],
            "vue": [
                OptimizationType.CODE_SPLITTING,
                OptimizationType.TREE_SHAKING,
                OptimizationType.BUNDLE_SIZE,
                OptimizationType.RUNTIME_PERFORMANCE,
            ],
            "angular": [
                OptimizationType.TREE_SHAKING,
                OptimizationType.BUNDLE_SIZE,
                OptimizationType.BUILD_TIME,
                OptimizationType.CODE_SPLITTING,
            ],
            "express": [
                OptimizationType.RUNTIME_PERFORMANCE,
                OptimizationType.MEMORY_USAGE,
                OptimizationType.CACHING,
                OptimizationType.COMPRESSION,
            ],
            "fastapi": [
                OptimizationType.RUNTIME_PERFORMANCE,
                OptimizationType.MEMORY_USAGE,
                OptimizationType.CACHING,
            ],
            "django": [
                OptimizationType.RUNTIME_PERFORMANCE,
                OptimizationType.MEMORY_USAGE,
                OptimizationType.CACHING,
            ],
            "flask": [
                OptimizationType.RUNTIME_PERFORMANCE,
                OptimizationType.MEMORY_USAGE,
                OptimizationType.CACHING,
            ],
        }

        # Performance patterns to optimize
        self.performance_patterns = {
            "react": {
                "unnecessary_rerenders": [
                    r"<[A-Za-z]+[^>]*>\s*{[^}]+}\s*</[A-Za-z]+>",  # Inline functions in JSX
                    r"onClick=\{.*=>\s*.*\}",  # Inline arrow functions
                ],
                "missing_memo": [
                    r"export default function\s+\w+\([^)]*\)\s*\{",
                    r"const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{",
                ],
                "inefficient_state": [
                    r"useState\(\[\]\)",  # Empty array as initial state
                    r"useState\(\{\}\)",  # Empty object as initial state
                ],
            },
            "vue": {
                "unnecessary_watchers": [
                    r"watch\(\s*\(\)\s*=>\s*.*,\s*\(\)\s*=>\s*.*\)"
                ],
                "inefficient_computed": [
                    r"computed\(\(\)\s*=>\s*.*\.filter\(.*\)\.map\(.*\)\)"
                ],
            },
            "node": {
                "synchronous_operations": [
                    r"fs\.readFileSync\(",
                    r"fs\.writeFileSync\(",
                    r"\.sync\(\)",
                ],
                "memory_leaks": [
                    r"setInterval\(",
                    r"setTimeout\(",
                    r"new\s+Array\(\d{4,}\)",
                ],
                "inefficient_loops": [
                    r"for\s*\(\s*let\s+\w+\s+in\s+.*\)\s*\{[^}]*\.hasOwnProperty\(",
                    r"Object\.keys\([^)]+\)\.forEach\(",
                ],
            },
            "python": {
                "inefficient_loops": [
                    r"for\s+\w+\s+in\s+range\(len\([^)]+\)\)",
                    r"for\s+\w+\s+in\s+.*\.keys\(\)",
                ],
                "memory_issues": [
                    r"\[\s*.*\s*for\s+.*\s+in\s+.*\]",  # List comprehension that could be generator
                    r"\.join\(\s*\[\s*.*\s*for\s+.*\s+in\s+.*\]\)",
                ],
                "database_inefficiencies": [
                    r"\.all\(\)\[0\]",  # Should use .first()
                    r"for\s+\w+\s+in\s+.*\.all\(\):",  # N+1 query pattern
                ],
            },
        }

        # Bundle optimization patterns
        self.bundle_patterns = {
            "large_dependencies": [
                r'import\s+.*\s+from\s+[\'"]lodash[\'"]',
                r'import\s+.*\s+from\s+[\'"]moment[\'"]',
                r'import\s+.*\s+from\s+[\'"]rxjs[\'"]',
            ],
            "unused_imports": [r'import\s+\{[^}]+\}\s+from\s+[\'"][^\'\"]+[\'"]'],
            "dynamic_imports": [r'import\([\'"][^\'\"]+[\'"]\)'],
        }

        # Optimization templates
        self.optimization_templates = {
            OptimizationType.CODE_SPLITTING: self._apply_code_splitting,
            OptimizationType.TREE_SHAKING: self._apply_tree_shaking,
            OptimizationType.BUNDLE_SIZE: self._optimize_bundle_size,
            OptimizationType.RUNTIME_PERFORMANCE: self._optimize_runtime_performance,
            OptimizationType.MEMORY_USAGE: self._optimize_memory_usage,
            OptimizationType.CACHING: self._apply_caching_optimizations,
            OptimizationType.COMPRESSION: self._apply_compression,
            OptimizationType.MINIFICATION: self._apply_minification,
        }

    async def optimize_project(
        self, project_path: str, context: Dict[str, Any], quality_result: Any = None
    ) -> OptimizationResult:
        """Optimize the generated project"""

        start_time = datetime.now()

        try:
            framework = context.get("target_framework", "react")
            language = context.get("target_language", "javascript")

            # Get optimization strategies for framework
            strategies = self.optimization_strategies.get(framework, [])

            actions_applied = []
            optimized_files = {}
            configuration_updates = {}

            # Apply each optimization strategy
            for optimization_type in strategies:
                if optimization_type in self.optimization_templates:
                    actions = await self.optimization_templates[optimization_type](
                        project_path, context, quality_result
                    )
                    actions_applied.extend(actions)

                    # Collect optimized files
                    for action in actions:
                        optimized_files[action.file_path] = action.optimized_code

            # Generate configuration updates
            configuration_updates = await self._generate_config_optimizations(
                framework, actions_applied, context
            )

            # Calculate optimization metrics
            metrics = await self._calculate_optimization_metrics(actions_applied)

            # Calculate overall improvement
            overall_improvement = self._calculate_overall_improvement(metrics)

            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(
                framework, actions_applied, metrics
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            return OptimizationResult(
                success=True,
                actions_applied=actions_applied,
                metrics=metrics,
                optimized_files=optimized_files,
                configuration_updates=configuration_updates,
                overall_improvement=overall_improvement,
                recommendations=recommendations,
                processing_time=processing_time,
                metadata={
                    "framework": framework,
                    "language": language,
                    "optimization_strategies": [s.value for s in strategies],
                    "actions_count": len(actions_applied),
                },
            )

        except Exception as e:
            return OptimizationResult(
                success=False,
                actions_applied=[],
                metrics=OptimizationMetrics(0, 0, 0, 0, 0, 0, 0, 0),
                optimized_files={},
                configuration_updates={},
                overall_improvement=0.0,
                recommendations=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={},
                error=str(e),
            )

    # Optimization strategy implementations
    async def _apply_code_splitting(
        self, project_path: str, context: Dict[str, Any], quality_result: Any = None
    ) -> List[OptimizationAction]:
        """Apply code splitting optimizations"""

        actions = []
        framework = context.get("target_framework", "react")

        if framework == "react":
            # Example: Add lazy loading to components
            original_code = """import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';"""

            optimized_code = """import { lazy } from 'react';

const HomePage = lazy(() => import('./pages/HomePage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const ContactPage = lazy(() => import('./pages/ContactPage'));"""

            actions.append(
                OptimizationAction(
                    type=OptimizationType.CODE_SPLITTING,
                    description="Convert static imports to lazy imports for code splitting",
                    file_path="src/App.tsx",
                    original_code=original_code,
                    optimized_code=optimized_code,
                    impact_score=75.0,
                    estimated_improvement="25% reduction in initial bundle size",
                    trade_offs=[
                        "Slightly longer loading time for subsequent pages",
                        "Need to handle loading states",
                    ],
                )
            )

        elif framework == "vue":
            original_code = """import HomePage from './pages/HomePage.vue';
import AboutPage from './pages/AboutPage.vue';"""

            optimized_code = """const HomePage = () => import('./pages/HomePage.vue');
const AboutPage = () => import('./pages/AboutPage.vue');"""

            actions.append(
                OptimizationAction(
                    type=OptimizationType.CODE_SPLITTING,
                    description="Convert to dynamic imports in Vue router",
                    file_path="src/router/index.ts",
                    original_code=original_code,
                    optimized_code=optimized_code,
                    impact_score=70.0,
                    estimated_improvement="20% reduction in initial bundle size",
                    trade_offs=["Loading states needed for route transitions"],
                )
            )

        return actions

    async def _apply_tree_shaking(
        self, project_path: str, context: Dict[str, Any], quality_result: Any = None
    ) -> List[OptimizationAction]:
        """Apply tree shaking optimizations"""

        actions = []

        # Optimize lodash imports
        original_code = "import _ from 'lodash';"
        optimized_code = "import { debounce, throttle } from 'lodash';"

        actions.append(
            OptimizationAction(
                type=OptimizationType.TREE_SHAKING,
                description="Replace full lodash import with specific function imports",
                file_path="src/utils/helpers.ts",
                original_code=original_code,
                optimized_code=optimized_code,
                impact_score=85.0,
                estimated_improvement="60-80% reduction in lodash bundle size",
                trade_offs=["Need to explicitly import each function used"],
            )
        )

        # Optimize Material-UI imports
        if context.get("target_framework") == "react":
            original_code = "import { Button, TextField, Dialog } from '@mui/material';"
            optimized_code = """import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';"""

            actions.append(
                OptimizationAction(
                    type=OptimizationType.TREE_SHAKING,
                    description="Use individual Material-UI component imports",
                    file_path="src/components/Form.tsx",
                    original_code=original_code,
                    optimized_code=optimized_code,
                    impact_score=70.0,
                    estimated_improvement="40% reduction in Material-UI bundle size",
                    trade_offs=["More import statements", "Better tree shaking"],
                )
            )

        return actions

    async def _optimize_bundle_size(
        self, project_path: str, context: Dict[str, Any], quality_result: Any = None
    ) -> List[OptimizationAction]:
        """Optimize overall bundle size"""

        actions = []

        # Replace moment.js with date-fns
        original_code = "import moment from 'moment';"
        optimized_code = "import { format, parseISO } from 'date-fns';"

        actions.append(
            OptimizationAction(
                type=OptimizationType.BUNDLE_SIZE,
                description="Replace moment.js with lighter date-fns",
                file_path="src/utils/dateHelpers.ts",
                original_code=original_code,
                optimized_code=optimized_code,
                impact_score=90.0,
                estimated_improvement="67% smaller bundle size for date operations",
                trade_offs=["Different API", "Need to import individual functions"],
            )
        )

        # Optimize image imports
        original_code = "import largeImage from './assets/hero-image.png';"
        optimized_code = "const largeImage = import('./assets/hero-image.webp');"

        actions.append(
            OptimizationAction(
                type=OptimizationType.BUNDLE_SIZE,
                description="Convert images to WebP format and use dynamic imports",
                file_path="src/components/Hero.tsx",
                original_code=original_code,
                optimized_code=optimized_code,
                impact_score=60.0,
                estimated_improvement="30-50% smaller image file sizes",
                trade_offs=[
                    "Need fallback for older browsers",
                    "More complex image handling",
                ],
            )
        )

        return actions

    async def _optimize_runtime_performance(
        self, project_path: str, context: Dict[str, Any], quality_result: Any = None
    ) -> List[OptimizationAction]:
        """Optimize runtime performance"""

        actions = []
        framework = context.get("target_framework", "react")

        if framework == "react":
            # Optimize component re-renders
            original_code = """const MyComponent = ({ items, onItemClick }) => {
  return (
    <div>
      {items.map(item =>
        <Item
          key={item.id}
          data={item}
          onClick={() => onItemClick(item.id)}
        />
      )}
    </div>
  );
};"""

            optimized_code = """const MyComponent = ({ items, onItemClick }) => {
  const handleItemClick = useCallback((id) => {
    onItemClick(id);
  }, [onItemClick]);

  return (
    <div>
      {items.map(item =>
        <MemoizedItem
          key={item.id}
          data={item}
          onClick={handleItemClick}
        />
      )}
    </div>
  );
};

const MemoizedItem = React.memo(Item);"""

            actions.append(
                OptimizationAction(
                    type=OptimizationType.RUNTIME_PERFORMANCE,
                    description="Add memoization and useCallback to prevent unnecessary re-renders",
                    file_path="src/components/ItemList.tsx",
                    original_code=original_code,
                    optimized_code=optimized_code,
                    impact_score=80.0,
                    estimated_improvement="40-60% reduction in render cycles",
                    trade_offs=[
                        "Slightly more complex code",
                        "Memory overhead for memoization",
                    ],
                )
            )

        elif framework in ["express", "fastapi", "django", "flask"]:
            # Database query optimization
            if framework == "express":
                original_code = """app.get('/api/users', async (req, res) => {
  const users = await User.findAll();
  const usersWithPosts = [];

  for (const user of users) {
    const posts = await Post.findAll({ where: { userId: user.id } });
    usersWithPosts.push({ ...user, posts });
  }

  res.json(usersWithPosts);
});"""

                optimized_code = """app.get('/api/users', async (req, res) => {
  const users = await User.findAll({
    include: [{
      model: Post,
      as: 'posts'
    }]
  });

  res.json(users);
});"""

                actions.append(
                    OptimizationAction(
                        type=OptimizationType.RUNTIME_PERFORMANCE,
                        description="Fix N+1 query problem with eager loading",
                        file_path="src/routes/users.ts",
                        original_code=original_code,
                        optimized_code=optimized_code,
                        impact_score=95.0,
                        estimated_improvement="80-90% faster database queries",
                        trade_offs=[
                            "More complex query",
                            "Potentially more data transferred",
                        ],
                    )
                )

        return actions

    async def _optimize_memory_usage(
        self, project_path: str, context: Dict[str, Any], quality_result: Any = None
    ) -> List[OptimizationAction]:
        """Optimize memory usage"""

        actions = []
        language = context.get("target_language", "javascript")

        if language in ["javascript", "typescript"]:
            # Fix memory leaks
            original_code = """useEffect(() => {
  const interval = setInterval(() => {
    fetchData();
  }, 1000);

  const listener = (event) => {
    handleEvent(event);
  };

  window.addEventListener('resize', listener);
}, []);"""

            optimized_code = """useEffect(() => {
  const interval = setInterval(() => {
    fetchData();
  }, 1000);

  const listener = (event) => {
    handleEvent(event);
  };

  window.addEventListener('resize', listener);

  return () => {
    clearInterval(interval);
    window.removeEventListener('resize', listener);
  };
}, []);"""

            actions.append(
                OptimizationAction(
                    type=OptimizationType.MEMORY_USAGE,
                    description="Add cleanup functions to prevent memory leaks",
                    file_path="src/hooks/useData.ts",
                    original_code=original_code,
                    optimized_code=optimized_code,
                    impact_score=85.0,
                    estimated_improvement="Prevent memory leaks and browser crashes",
                    trade_offs=["Slightly more boilerplate code"],
                )
            )

        elif language == "python":
            # Generator optimization
            original_code = """def process_large_dataset(data):
    processed_items = []
    for item in data:
        processed = expensive_operation(item)
        processed_items.append(processed)
    return processed_items"""

            optimized_code = """def process_large_dataset(data):
    for item in data:
        yield expensive_operation(item)"""

            actions.append(
                OptimizationAction(
                    type=OptimizationType.MEMORY_USAGE,
                    description="Use generator to process large datasets without storing all in memory",
                    file_path="src/services/data_processor.py",
                    original_code=original_code,
                    optimized_code=optimized_code,
                    impact_score=75.0,
                    estimated_improvement="90% reduction in memory usage for large datasets",
                    trade_offs=[
                        "Can only iterate once",
                        "Need to handle generators in calling code",
                    ],
                )
            )

        return actions

    async def _apply_caching_optimizations(
        self, project_path: str, context: Dict[str, Any], quality_result: Any = None
    ) -> List[OptimizationAction]:
        """Apply caching optimizations"""

        actions = []
        framework = context.get("target_framework", "react")

        if framework in ["express", "fastapi", "django", "flask"]:
            # API response caching
            if framework == "express":
                original_code = """app.get('/api/stats', async (req, res) => {
  const stats = await calculateExpensiveStats();
  res.json(stats);
});"""

                optimized_code = """const cache = new Map();

app.get('/api/stats', async (req, res) => {
  const cacheKey = 'stats';

  if (cache.has(cacheKey)) {
    const cached = cache.get(cacheKey);
    if (Date.now() - cached.timestamp < 5 * 60 * 1000) { // 5 minutes
      return res.json(cached.data);
    }
  }

  const stats = await calculateExpensiveStats();
  cache.set(cacheKey, { data: stats, timestamp: Date.now() });

  res.set('Cache-Control', 'public, max-age=300'); // 5 minutes
  res.json(stats);
});"""

                actions.append(
                    OptimizationAction(
                        type=OptimizationType.CACHING,
                        description="Add memory caching and HTTP caching headers",
                        file_path="src/routes/stats.ts",
                        original_code=original_code,
                        optimized_code=optimized_code,
                        impact_score=90.0,
                        estimated_improvement="95% faster response time for cached requests",
                        trade_offs=["Memory usage for cache", "Potential stale data"],
                    )
                )

        elif framework in ["react", "vue", "angular"]:
            # Browser caching optimization
            original_code = """const fetchUserData = async (userId) => {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
};"""

            optimized_code = """const userCache = new Map();

const fetchUserData = async (userId) => {
  if (userCache.has(userId)) {
    const cached = userCache.get(userId);
    if (Date.now() - cached.timestamp < 2 * 60 * 1000) { // 2 minutes
      return cached.data;
    }
  }

  const response = await fetch(`/api/users/${userId}`);
  const data = await response.json();

  userCache.set(userId, { data, timestamp: Date.now() });
  return data;
};"""

            actions.append(
                OptimizationAction(
                    type=OptimizationType.CACHING,
                    description="Add client-side caching for API requests",
                    file_path="src/services/api.ts",
                    original_code=original_code,
                    optimized_code=optimized_code,
                    impact_score=70.0,
                    estimated_improvement="Instant loading for repeated requests",
                    trade_offs=["Memory usage", "Need cache invalidation strategy"],
                )
            )

        return actions

    # Additional optimization methods (simplified)
    async def _apply_compression(
        self, project_path: str, context: Dict[str, Any], quality_result: Any = None
    ) -> List[OptimizationAction]:
        """Apply compression optimizations"""
        return []

    async def _apply_minification(
        self, project_path: str, context: Dict[str, Any], quality_result: Any = None
    ) -> List[OptimizationAction]:
        """Apply minification optimizations"""
        return []

    async def _generate_config_optimizations(
        self, framework: str, actions: List[OptimizationAction], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate configuration file optimizations"""

        config_updates = {}

        if framework in ["react", "vue"]:
            # Vite/Webpack optimizations
            config_updates["vite.config.ts"] = {
                "build": {
                    "rollupOptions": {
                        "output": {
                            "manualChunks": {
                                "vendor": ["react", "react-dom"],
                                "ui": ["@mui/material"],
                            }
                        }
                    },
                    "chunkSizeWarningLimit": 1000,
                    "minify": "terser",
                    "sourcemap": True,
                }
            }

        elif framework in ["express", "fastapi", "django", "flask"]:
            # Server optimizations
            config_updates["optimization.conf"] = {
                "compression": True,
                "caching": {"static_files": "1y", "api_responses": "5m"},
                "minification": True,
            }

        return config_updates

    async def _calculate_optimization_metrics(
        self, actions: List[OptimizationAction]
    ) -> OptimizationMetrics:
        """Calculate optimization metrics from applied actions"""

        bundle_size_reduction = 0.0
        performance_improvement = 0.0
        build_time_improvement = 0.0
        memory_savings = 0.0
        network_requests_reduced = 0

        for action in actions:
            if action.type == OptimizationType.BUNDLE_SIZE:
                bundle_size_reduction += action.impact_score * 0.5
            elif action.type == OptimizationType.RUNTIME_PERFORMANCE:
                performance_improvement += action.impact_score * 0.6
            elif action.type == OptimizationType.BUILD_TIME:
                build_time_improvement += action.impact_score * 0.3
            elif action.type == OptimizationType.MEMORY_USAGE:
                memory_savings += action.impact_score * 0.4
            elif action.type == OptimizationType.CODE_SPLITTING:
                network_requests_reduced += 2

        return OptimizationMetrics(
            bundle_size_reduction=min(bundle_size_reduction, 70.0),
            performance_improvement=min(performance_improvement, 80.0),
            build_time_improvement=min(build_time_improvement, 50.0),
            memory_savings=min(memory_savings, 60.0),
            network_requests_reduced=network_requests_reduced,
            code_duplication_removed=15.0,  # Estimated
            unused_code_removed=25.0,  # Estimated
            compression_ratio=0.7,  # 70% of original size
        )

    def _calculate_overall_improvement(self, metrics: OptimizationMetrics) -> float:
        """Calculate overall improvement score"""

        weights = {
            "bundle_size": 0.25,
            "performance": 0.30,
            "build_time": 0.15,
            "memory": 0.20,
            "network": 0.10,
        }

        network_score = min(metrics.network_requests_reduced * 10, 50)  # Max 50 points

        overall = (
            metrics.bundle_size_reduction * weights["bundle_size"]
            + metrics.performance_improvement * weights["performance"]
            + metrics.build_time_improvement * weights["build_time"]
            + metrics.memory_savings * weights["memory"]
            + network_score * weights["network"]
        )

        return min(overall, 100.0)

    async def _generate_optimization_recommendations(
        self,
        framework: str,
        actions: List[OptimizationAction],
        metrics: OptimizationMetrics,
    ) -> List[str]:
        """Generate optimization recommendations"""

        recommendations = []

        # Bundle size recommendations
        if metrics.bundle_size_reduction < 20:
            recommendations.append(
                "Consider implementing code splitting and tree shaking for better bundle optimization"
            )

        # Performance recommendations
        if metrics.performance_improvement < 30:
            recommendations.append(
                "Add performance monitoring and optimize critical rendering paths"
            )

        # Framework-specific recommendations
        if framework == "react":
            recommendations.extend(
                [
                    "Use React.memo for expensive components",
                    "Implement virtual scrolling for large lists",
                    "Consider using React.lazy for route-based code splitting",
                ]
            )
        elif framework in ["express", "fastapi"]:
            recommendations.extend(
                [
                    "Implement database connection pooling",
                    "Add response compression middleware",
                    "Use clustering for multi-core CPU utilization",
                ]
            )

        # Caching recommendations
        if not any(a.type == OptimizationType.CACHING for a in actions):
            recommendations.append(
                "Implement caching strategy for improved response times"
            )

        return recommendations[:8]  # Limit to top 8 recommendations
