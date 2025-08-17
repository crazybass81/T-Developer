"""
Tests for T-Developer Production Package

This package contains comprehensive tests for all production-ready components
including multi-tenancy, global distribution, auto-scaling, security hardening,
compliance, monitoring, disaster recovery, and cost optimization.

Test Organization:
    test_tenant_manager.py: Multi-tenancy management tests
    test_global_distributor.py: Global distribution and edge computing tests
    test_auto_scaler.py: Intelligent auto-scaling system tests
    test_security_hardener.py: Production security hardening tests
    test_compliance_engine.py: Compliance and governance tests
    test_monitoring_hub.py: Production monitoring and observability tests
    test_disaster_recovery.py: Disaster recovery and backup tests
    test_cost_optimizer.py: Cost optimization and FinOps tests
    test_production_orchestrator.py: Integration and orchestration tests

Test Categories:
    - Unit Tests: Individual component functionality
    - Integration Tests: Inter-component interactions
    - End-to-End Tests: Complete workflows
    - Performance Tests: Scalability and performance
    - Security Tests: Security vulnerability testing
    - Compliance Tests: Regulatory compliance validation

Running Tests:
    # Run all production tests
    pytest tests/production/

    # Run specific test module
    pytest tests/production/test_tenant_manager.py

    # Run with coverage
    pytest tests/production/ --cov=packages.production

    # Run with specific markers
    pytest tests/production/ -m "integration"
    pytest tests/production/ -m "security"

Test Fixtures:
    The test modules use various fixtures for setting up test environments:
    - Database fixtures for isolated testing
    - Mock services for external dependencies
    - Sample data fixtures for consistent testing
    - Async fixtures for testing async functionality

Best Practices:
    1. Each test is isolated and doesn't depend on others
    2. Tests use mocks for external dependencies
    3. Tests cover both success and failure scenarios
    4. Tests include edge cases and boundary conditions
    5. Tests verify both functional and non-functional requirements
"""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

# Common test fixtures used across production tests


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_database():
    """Mock database connection for testing."""
    db_mock = AsyncMock()
    db_mock.execute.return_value = Mock()
    db_mock.fetch.return_value = []
    db_mock.fetchone.return_value = None
    return db_mock


@pytest.fixture
async def mock_redis():
    """Mock Redis connection for testing."""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = True
    return redis_mock


@pytest.fixture
def mock_external_api():
    """Mock external API responses."""
    api_mock = Mock()
    api_mock.get.return_value.status_code = 200
    api_mock.get.return_value.json.return_value = {"status": "success"}
    api_mock.post.return_value.status_code = 201
    api_mock.post.return_value.json.return_value = {"id": "created"}
    return api_mock


@pytest.fixture
def sample_tenant_data():
    """Sample tenant data for testing."""
    return {
        "name": "Test Corporation",
        "admin_email": "admin@test.com",
        "tier": "professional",
        "region": "us-east-1",
        "config": {
            "encryption_enabled": True,
            "backup_retention_days": 30,
            "compliance_requirements": ["GDPR", "SOC2"],
        },
    }


@pytest.fixture
def sample_metrics_data():
    """Sample metrics data for testing."""
    return {
        "cpu_utilization": [65.0, 70.0, 68.0, 72.0, 75.0],
        "memory_utilization": [55.0, 58.0, 60.0, 62.0, 65.0],
        "request_rate": [850, 920, 880, 950, 1020],
        "error_rate": [0.5, 0.3, 0.4, 0.6, 0.8],
        "response_time": [120, 135, 125, 140, 150],
    }


@pytest.fixture
def sample_security_events():
    """Sample security events for testing."""
    return [
        {
            "event_type": "sql_injection_attempt",
            "source_ip": "192.168.1.100",
            "target": "/api/users",
            "severity": "high",
            "blocked": True,
            "timestamp": "2024-01-15T10:30:00Z",
        },
        {
            "event_type": "brute_force_attack",
            "source_ip": "10.0.0.50",
            "target": "/login",
            "severity": "medium",
            "blocked": True,
            "timestamp": "2024-01-15T11:15:00Z",
        },
        {
            "event_type": "suspicious_user_agent",
            "source_ip": "203.0.113.10",
            "target": "/api/data",
            "severity": "low",
            "blocked": False,
            "timestamp": "2024-01-15T12:00:00Z",
        },
    ]


@pytest.fixture
def sample_cost_data():
    """Sample cost data for testing."""
    return {
        "daily_costs": [
            {"date": "2024-01-01", "amount": 150.50, "resource": "compute"},
            {"date": "2024-01-01", "amount": 45.20, "resource": "storage"},
            {"date": "2024-01-01", "amount": 30.10, "resource": "network"},
            {"date": "2024-01-02", "amount": 165.75, "resource": "compute"},
            {"date": "2024-01-02", "amount": 47.80, "resource": "storage"},
            {"date": "2024-01-02", "amount": 28.50, "resource": "network"},
        ],
        "budget_limits": {
            "monthly_total": 10000.0,
            "compute": 6000.0,
            "storage": 2000.0,
            "network": 1500.0,
            "other": 500.0,
        },
    }


# Test markers for categorizing tests
pytest_markers = {
    "unit": "Unit tests for individual components",
    "integration": "Integration tests for component interactions",
    "e2e": "End-to-end tests for complete workflows",
    "performance": "Performance and scalability tests",
    "security": "Security vulnerability tests",
    "compliance": "Regulatory compliance tests",
    "slow": "Tests that take longer to run",
    "async": "Tests for async functionality",
}


# Utility functions for tests
def assert_valid_uuid(uuid_string: str) -> bool:
    """Validate that a string is a valid UUID format."""
    import re

    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))


def assert_timestamp_recent(timestamp_str: str, max_age_seconds: int = 60) -> bool:
    """Validate that a timestamp is recent (within max_age_seconds)."""
    from datetime import datetime

    import dateutil.parser

    try:
        timestamp = dateutil.parser.parse(timestamp_str)
        age = (datetime.utcnow().replace(tzinfo=timestamp.tzinfo) - timestamp).total_seconds()
        return age <= max_age_seconds
    except Exception:
        return False


def create_mock_async_context_manager(return_value=None):
    """Create a mock async context manager."""

    class MockAsyncContextManager:
        async def __aenter__(self):
            return return_value

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    return MockAsyncContextManager()


# Configuration for test environment
TEST_CONFIG = {
    "database": {"url": "sqlite:///:memory:", "echo": False},
    "redis": {"url": "redis://localhost:6379/15"},  # Use different DB for tests
    "logging": {
        "level": "WARNING",  # Reduce log noise in tests
        "format": "%(name)s - %(levelname)s - %(message)s",
    },
    "testing": {"mock_external_services": True, "fast_timeouts": True, "skip_slow_tests": False},
}


# Test data generators
def generate_tenant_data(count: int = 1, tier: str = "professional"):
    """Generate test tenant data."""
    tenants = []
    for i in range(count):
        tenant = {
            "name": f"Test Corp {i+1}",
            "admin_email": f"admin{i+1}@test{i+1}.com",
            "tier": tier,
            "region": "us-east-1" if i % 2 == 0 else "eu-west-1",
        }
        tenants.append(tenant)
    return tenants if count > 1 else tenants[0]


def generate_metrics_series(
    metric_name: str, length: int = 100, base_value: float = 50.0, variation: float = 20.0
):
    """Generate a time series of metrics for testing."""
    import datetime
    import random

    series = []
    current_time = datetime.datetime.utcnow()

    for i in range(length):
        timestamp = current_time - datetime.timedelta(minutes=i)
        # Add some realistic variation
        value = base_value + random.uniform(-variation, variation)
        # Add trend if needed
        if metric_name in ["cpu_utilization", "memory_utilization"]:
            value = max(0, min(100, value))  # Clamp to 0-100%
        elif metric_name == "error_rate":
            value = max(0, min(10, value))  # Clamp to 0-10%
        else:
            value = max(0, value)  # Just ensure positive

        series.append({"timestamp": timestamp.isoformat(), "value": value, "metric": metric_name})

    return series


# Test environment setup and teardown
class TestEnvironment:
    """Test environment manager for production tests."""

    def __init__(self):
        self.temp_dirs = []
        self.mock_services = {}
        self.test_data = {}

    async def setup(self):
        """Set up test environment."""
        # Create temporary directories
        import tempfile

        self.temp_dirs.append(tempfile.mkdtemp(prefix="tdev_test_"))

        # Initialize mock services
        self.mock_services["database"] = AsyncMock()
        self.mock_services["redis"] = AsyncMock()
        self.mock_services["s3"] = Mock()

        # Load test data
        self.test_data["tenants"] = generate_tenant_data(5)
        self.test_data["metrics"] = {
            "cpu": generate_metrics_series("cpu_utilization"),
            "memory": generate_metrics_series("memory_utilization"),
            "requests": generate_metrics_series("request_rate", base_value=1000, variation=500),
        }

    async def teardown(self):
        """Clean up test environment."""
        # Clean up temporary directories
        import shutil

        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

        # Reset mock services
        self.mock_services.clear()
        self.test_data.clear()


# Export commonly used items
__all__ = [
    "mock_database",
    "mock_redis",
    "mock_external_api",
    "sample_tenant_data",
    "sample_metrics_data",
    "sample_security_events",
    "sample_cost_data",
    "assert_valid_uuid",
    "assert_timestamp_recent",
    "create_mock_async_context_manager",
    "TEST_CONFIG",
    "generate_tenant_data",
    "generate_metrics_series",
    "TestEnvironment",
]
