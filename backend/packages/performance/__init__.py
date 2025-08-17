"""Performance Package - Phase 6 Performance Optimization and Reliability Engineering.

This package provides comprehensive performance optimization and reliability
engineering capabilities for T-Developer.

Components:
- profiler: Performance profiling and analysis
- optimizer: Automated performance optimization
- benchmarks: Performance benchmarking suite
- cache: Multi-level caching system
- load_testing: Load testing with k6 integration
- chaos_engineering: Chaos engineering and failure injection
- monitoring: Monitoring, alerting, and observability
"""

from .benchmarks import (
    BenchmarkMetrics,
    BenchmarkReporter,
    BenchmarkRunner,
    BenchmarkSuite,
    PerformanceBaseline,
    PerformanceBenchmarkSuite,
    run_comprehensive_benchmarks,
)
from .cache import (
    CacheBackend,
    CacheEntry,
    CacheManager,
    CacheStats,
    FileCache,
    MemoryCache,
    MultiLevelCache,
    cache_context,
    cache_health_check,
    cache_result,
    cached,
)
from .chaos_engineering import (
    ChaosExperiment,
    ChaosOrchestrator,
    ChaosResult,
    ChaosTarget,
    ExperimentStatus,
    FailureInjector,
    FailureType,
    run_chaos_experiments,
)
from .load_testing import (
    K6Runner,
    LoadTestConfig,
    LoadTestManager,
    LoadTestResult,
    LoadTestSuite,
    run_load_tests,
)
from .monitoring import (
    Alert,
    AlertManager,
    AlertSeverity,
    AlertStatus,
    EmailNotificationChannel,
    Metric,
    MetricCollector,
    MetricType,
    MonitoringDashboard,
    NotificationChannel,
    SlackNotificationChannel,
    start_monitoring_system,
)
from .optimizer import (
    AutoOptimizer,
    CodeAnalyzer,
    OptimizationPatch,
    OptimizationResult,
    PatchApplicator,
    PerformanceBenchmarker,
    optimize_performance,
)
from .profiler import (
    Bottleneck,
    BottleneckAnalyzer,
    OptimizationEngine,
    OptimizationSuggestion,
    PerformanceMetrics,
    PerformanceOptimizer,
    PerformanceProfiler,
    ProfileReport,
)

__version__ = "1.0.0"
__author__ = "T-Developer Team"
__description__ = "Performance optimization and reliability engineering for T-Developer"

# Performance targets
PERFORMANCE_TARGETS = {
    "p95_latency_ms": 200,
    "availability_percent": 99.9,
    "cache_hit_rate_percent": 70,
    "throughput_rps": 100,
    "cpu_usage_percent": 80,
    "memory_usage_percent": 85,
    "error_rate_percent": 1.0,
}

# Default configuration
DEFAULT_CONFIG = {
    "profiling": {"enabled": True, "sample_rate": 0.1, "max_traces": 1000},
    "optimization": {"auto_optimize": False, "safety_threshold": 0.7, "max_cycles": 5},
    "caching": {"memory_cache_size": 1000, "file_cache_size": 5000, "default_ttl": 3600},
    "monitoring": {"collection_interval": 30, "retention_hours": 24, "alert_cooldown": 300},
    "load_testing": {"k6_binary": "k6", "default_duration": 300, "default_vus": 10},
    "chaos_engineering": {"safety_enabled": True, "max_concurrent": 1, "default_duration": 300},
}

__all__ = [
    # Profiler
    "PerformanceProfiler",
    "BottleneckAnalyzer",
    "OptimizationEngine",
    "PerformanceOptimizer",
    "PerformanceMetrics",
    "Bottleneck",
    "OptimizationSuggestion",
    "ProfileReport",
    # Optimizer
    "AutoOptimizer",
    "CodeAnalyzer",
    "PatchApplicator",
    "PerformanceBenchmarker",
    "OptimizationResult",
    "OptimizationPatch",
    "optimize_performance",
    # Benchmarks
    "PerformanceBenchmarkSuite",
    "BenchmarkRunner",
    "BenchmarkReporter",
    "BenchmarkMetrics",
    "BenchmarkSuite",
    "PerformanceBaseline",
    "run_comprehensive_benchmarks",
    # Cache
    "CacheManager",
    "MemoryCache",
    "FileCache",
    "MultiLevelCache",
    "CacheBackend",
    "CacheEntry",
    "CacheStats",
    "cached",
    "cache_result",
    "cache_context",
    "cache_health_check",
    # Load Testing
    "LoadTestManager",
    "K6Runner",
    "LoadTestConfig",
    "LoadTestResult",
    "LoadTestSuite",
    "run_load_tests",
    # Chaos Engineering
    "ChaosOrchestrator",
    "ChaosExperiment",
    "ChaosResult",
    "ChaosTarget",
    "FailureInjector",
    "FailureType",
    "ExperimentStatus",
    "run_chaos_experiments",
    # Monitoring
    "MetricCollector",
    "AlertManager",
    "MonitoringDashboard",
    "Metric",
    "Alert",
    "AlertSeverity",
    "AlertStatus",
    "MetricType",
    "NotificationChannel",
    "SlackNotificationChannel",
    "EmailNotificationChannel",
    "start_monitoring_system",
    # Constants
    "PERFORMANCE_TARGETS",
    "DEFAULT_CONFIG",
]
