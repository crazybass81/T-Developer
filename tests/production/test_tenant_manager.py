"""
Tests for tenant_manager module.

This module tests the multi-tenancy management system including tenant
creation, isolation, resource quotas, and lifecycle management.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from packages.production.tenant_manager import (
    TenantManager,
    Tenant,
    TenantTier,
    TenantStatus,
    ResourceType,
    ResourceQuota,
    TenantMetadata
)


@pytest.fixture
async def tenant_manager():
    """Create tenant manager instance for testing."""
    manager = TenantManager()
    await manager.initialize()
    yield manager


@pytest.fixture
def sample_tenant():
    """Create sample tenant for testing."""
    return Tenant(
        id="test-tenant-123",
        name="Test Corp",
        tier=TenantTier.PROFESSIONAL,
        status=TenantStatus.PENDING
    )


class TestTenant:
    """Test Tenant class functionality."""
    
    def test_tenant_creation(self):
        """Test tenant creation with default values."""
        tenant = Tenant(
            id="test-123",
            name="Test Company",
            tier=TenantTier.STARTER
        )
        
        assert tenant.id == "test-123"
        assert tenant.name == "Test Company"
        assert tenant.tier == TenantTier.STARTER
        assert tenant.status == TenantStatus.PENDING
        assert len(tenant.quotas) > 0  # Should have default quotas
        
    def test_default_quotas_by_tier(self):
        """Test that default quotas are set based on tier."""
        starter_tenant = Tenant(id="1", name="Starter", tier=TenantTier.STARTER)
        enterprise_tenant = Tenant(id="2", name="Enterprise", tier=TenantTier.ENTERPRISE)
        
        # Enterprise should have higher quotas
        starter_cpu = starter_tenant.quotas[ResourceType.CPU_CORES].limit
        enterprise_cpu = enterprise_tenant.quotas[ResourceType.CPU_CORES].limit
        
        assert enterprise_cpu > starter_cpu
        assert enterprise_tenant.quotas[ResourceType.CPU_CORES].auto_scale is True
        assert starter_tenant.quotas[ResourceType.CPU_CORES].auto_scale is False
        
    def test_add_quota(self, sample_tenant):
        """Test adding custom resource quota."""
        sample_tenant.add_quota(ResourceType.DATA_TRANSFER_GB, 500.0, auto_scale=True)
        
        quota = sample_tenant.quotas[ResourceType.DATA_TRANSFER_GB]
        assert quota.limit == 500.0
        assert quota.auto_scale is True
        
    def test_check_quota(self, sample_tenant):
        """Test quota checking functionality."""
        # Set a small quota for testing
        sample_tenant.add_quota(ResourceType.CPU_CORES, 4.0)
        
        # Should allow request within quota
        assert sample_tenant.check_quota(ResourceType.CPU_CORES, 2.0) is True
        
        # Should deny request exceeding quota
        assert sample_tenant.check_quota(ResourceType.CPU_CORES, 6.0) is False
        
    def test_update_usage(self, sample_tenant):
        """Test updating resource usage."""
        sample_tenant.add_quota(ResourceType.MEMORY_GB, 16.0)
        
        # Update usage
        sample_tenant.update_usage(ResourceType.MEMORY_GB, 8.0)
        assert sample_tenant.quotas[ResourceType.MEMORY_GB].current_usage == 8.0
        
        # Add more usage
        sample_tenant.update_usage(ResourceType.MEMORY_GB, 4.0)
        assert sample_tenant.quotas[ResourceType.MEMORY_GB].current_usage == 12.0
        
        # Negative usage (freeing resources)
        sample_tenant.update_usage(ResourceType.MEMORY_GB, -2.0)
        assert sample_tenant.quotas[ResourceType.MEMORY_GB].current_usage == 10.0
        
    def test_namespace_generation(self, sample_tenant):
        """Test Kubernetes namespace generation."""
        namespace = sample_tenant.get_namespace()
        assert namespace.startswith("tenant-")
        assert "test-tenant-123" in namespace
        
    def test_database_name_generation(self, sample_tenant):
        """Test database name generation."""
        db_name = sample_tenant.get_database_name()
        assert db_name.startswith("tdev_")
        assert "-" not in db_name  # Should replace hyphens with underscores
        
    def test_quota_exceeded_detection(self, sample_tenant):
        """Test detection of exceeded quotas."""
        # Set quota and exceed it
        sample_tenant.add_quota(ResourceType.STORAGE_GB, 100.0)
        sample_tenant.update_usage(ResourceType.STORAGE_GB, 150.0)
        
        exceeded = sample_tenant.is_quota_exceeded()
        assert ResourceType.STORAGE_GB in exceeded


class TestResourceQuota:
    """Test ResourceQuota class functionality."""
    
    def test_quota_creation(self):
        """Test resource quota creation."""
        quota = ResourceQuota(
            resource_type=ResourceType.CPU_CORES,
            limit=8.0,
            warning_threshold=0.8
        )
        
        assert quota.resource_type == ResourceType.CPU_CORES
        assert quota.limit == 8.0
        assert quota.current_usage == 0.0
        assert quota.warning_threshold == 0.8
        
    def test_usage_percentage_calculation(self):
        """Test usage percentage calculation."""
        quota = ResourceQuota(ResourceType.MEMORY_GB, 16.0, current_usage=12.0)
        
        assert quota.usage_percentage == 0.75  # 12/16 = 0.75
        
    def test_warning_threshold_detection(self):
        """Test warning threshold detection."""
        quota = ResourceQuota(
            ResourceType.MEMORY_GB, 
            limit=16.0, 
            current_usage=13.0,  # 81.25% usage
            warning_threshold=0.8
        )
        
        assert quota.is_over_warning is True
        
        quota.current_usage = 10.0  # 62.5% usage
        assert quota.is_over_warning is False
        
    def test_limit_detection(self):
        """Test limit detection."""
        quota = ResourceQuota(ResourceType.STORAGE_GB, 100.0, current_usage=100.0)
        
        assert quota.is_at_limit is True
        
        quota.current_usage = 110.0
        assert quota.is_at_limit is True
        
        quota.current_usage = 90.0
        assert quota.is_at_limit is False


class TestTenantManager:
    """Test TenantManager class functionality."""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test tenant manager initialization."""
        manager = TenantManager()
        await manager.initialize()
        
        # Should have initialized successfully
        assert manager._tenants is not None
        assert manager._cipher is not None
        
    @pytest.mark.asyncio
    async def test_create_tenant(self, tenant_manager):
        """Test tenant creation."""
        tenant = await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.PROFESSIONAL,
            "admin@test.com"
        )
        
        assert tenant.name == "Test Company"
        assert tenant.tier == TenantTier.PROFESSIONAL
        assert "admin@test.com" in tenant.admin_users
        assert tenant.status == TenantStatus.PENDING
        assert tenant.id in tenant_manager._tenants
        
    @pytest.mark.asyncio
    async def test_create_duplicate_tenant(self, tenant_manager):
        """Test that creating duplicate tenant fails."""
        # Create first tenant
        await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.STARTER,
            "admin@test.com"
        )
        
        # Try to create duplicate
        with pytest.raises(ValueError, match="already exists"):
            await tenant_manager.create_tenant(
                "Test Company",
                TenantTier.STARTER,
                "admin2@test.com"
            )
            
    @pytest.mark.asyncio
    async def test_invalid_tenant_name(self, tenant_manager):
        """Test that invalid tenant names are rejected."""
        with pytest.raises(ValueError, match="Invalid tenant name"):
            await tenant_manager.create_tenant(
                "",  # Empty name
                TenantTier.STARTER,
                "admin@test.com"
            )
            
        with pytest.raises(ValueError, match="Invalid tenant name"):
            await tenant_manager.create_tenant(
                "A",  # Too short
                TenantTier.STARTER,
                "admin@test.com"
            )
            
    @pytest.mark.asyncio
    async def test_activate_tenant(self, tenant_manager):
        """Test tenant activation."""
        # Create tenant
        tenant = await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.STARTER,
            "admin@test.com"
        )
        
        # Activate tenant
        result = await tenant_manager.activate_tenant(tenant.id)
        
        assert result is True
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.metadata.last_active_at is not None
        
    @pytest.mark.asyncio
    async def test_activate_nonexistent_tenant(self, tenant_manager):
        """Test that activating non-existent tenant fails."""
        with pytest.raises(ValueError, match="Tenant not found"):
            await tenant_manager.activate_tenant("nonexistent-tenant")
            
    @pytest.mark.asyncio
    async def test_suspend_tenant(self, tenant_manager):
        """Test tenant suspension."""
        # Create and activate tenant
        tenant = await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.STARTER,
            "admin@test.com"
        )
        await tenant_manager.activate_tenant(tenant.id)
        
        # Suspend tenant
        result = await tenant_manager.suspend_tenant(tenant.id, "Testing suspension")
        
        assert result is True
        assert tenant.status == TenantStatus.SUSPENDED
        
    @pytest.mark.asyncio
    async def test_terminate_tenant(self, tenant_manager):
        """Test tenant termination."""
        # Create tenant
        tenant = await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.STARTER,
            "admin@test.com"
        )
        
        # Terminate with data preservation
        result = await tenant_manager.terminate_tenant(tenant.id, preserve_data=True)
        
        assert result is True
        assert tenant.status == TenantStatus.TERMINATED
        assert tenant.id in tenant_manager._tenants  # Still in system
        
        # Terminate without data preservation
        result = await tenant_manager.terminate_tenant(tenant.id, preserve_data=False)
        
        assert result is True
        assert tenant.id not in tenant_manager._tenants  # Removed from system
        
    @pytest.mark.asyncio
    async def test_get_tenant(self, tenant_manager):
        """Test tenant retrieval."""
        # Create tenant
        created_tenant = await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.STARTER,
            "admin@test.com"
        )
        
        # Get tenant by ID
        retrieved_tenant = tenant_manager.get_tenant(created_tenant.id)
        assert retrieved_tenant is not None
        assert retrieved_tenant.id == created_tenant.id
        
        # Get non-existent tenant
        assert tenant_manager.get_tenant("nonexistent") is None
        
    @pytest.mark.asyncio
    async def test_get_tenant_by_name(self, tenant_manager):
        """Test tenant retrieval by name."""
        # Create tenant
        await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.STARTER,
            "admin@test.com"
        )
        
        # Get tenant by name
        tenant = tenant_manager.get_tenant_by_name("Test Company")
        assert tenant is not None
        assert tenant.name == "Test Company"
        
        # Get non-existent tenant
        assert tenant_manager.get_tenant_by_name("Nonexistent") is None
        
    @pytest.mark.asyncio
    async def test_list_tenants(self, tenant_manager):
        """Test listing tenants with filtering."""
        # Create tenants with different statuses
        tenant1 = await tenant_manager.create_tenant(
            "Company 1", TenantTier.STARTER, "admin1@test.com"
        )
        tenant2 = await tenant_manager.create_tenant(
            "Company 2", TenantTier.PROFESSIONAL, "admin2@test.com"
        )
        
        await tenant_manager.activate_tenant(tenant1.id)
        # Leave tenant2 as pending
        
        # List all tenants
        all_tenants = tenant_manager.list_tenants()
        assert len(all_tenants) == 2
        
        # List only active tenants
        active_tenants = tenant_manager.list_tenants(TenantStatus.ACTIVE)
        assert len(active_tenants) == 1
        assert active_tenants[0].id == tenant1.id
        
        # List only pending tenants
        pending_tenants = tenant_manager.list_tenants(TenantStatus.PENDING)
        assert len(pending_tenants) == 1
        assert pending_tenants[0].id == tenant2.id
        
    @pytest.mark.asyncio
    async def test_check_resource_usage(self, tenant_manager):
        """Test resource usage checking."""
        # Create tenant
        tenant = await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.STARTER,
            "admin@test.com"
        )
        
        # Check resource usage
        usage = await tenant_manager.check_resource_usage(tenant.id)
        
        assert isinstance(usage, dict)
        assert ResourceType.CPU_CORES in usage
        assert ResourceType.MEMORY_GB in usage
        
        # All usage should be percentages (0-100)
        for resource_type, percentage in usage.items():
            assert 0 <= percentage <= 100
            
    @pytest.mark.asyncio
    async def test_enforce_quotas(self, tenant_manager):
        """Test quota enforcement."""
        # Create tenant
        tenant = await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.STARTER,
            "admin@test.com"
        )
        
        # Simulate quota exceeded
        tenant.update_usage(ResourceType.CPU_CORES, 999.0)  # Exceed quota
        
        # Enforce quotas
        actions = await tenant_manager.enforce_quotas(tenant.id)
        
        assert isinstance(actions, list)
        # Should have taken some action for exceeded quota
        
    @pytest.mark.asyncio
    async def test_get_tenant_metrics(self, tenant_manager):
        """Test tenant metrics retrieval."""
        # Create and activate tenant
        tenant = await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.STARTER,
            "admin@test.com"
        )
        await tenant_manager.activate_tenant(tenant.id)
        
        # Get metrics
        metrics = await tenant_manager.get_tenant_metrics(tenant.id)
        
        assert "tenant_id" in metrics
        assert "status" in metrics
        assert "tier" in metrics
        assert "uptime_hours" in metrics
        assert "resource_usage" in metrics
        assert "quota_violations" in metrics
        
        assert metrics["tenant_id"] == tenant.id
        assert metrics["status"] == TenantStatus.ACTIVE.value
        assert metrics["tier"] == TenantTier.STARTER.value
        
    @pytest.mark.asyncio
    async def test_migrate_tenant(self, tenant_manager):
        """Test tenant migration between regions."""
        # Create tenant
        tenant = await tenant_manager.create_tenant(
            "Test Company",
            TenantTier.STARTER,
            "admin@test.com"
        )
        
        original_region = tenant.config.get('data_residency', 'us-east-1')
        target_region = 'eu-west-1'
        
        # Migrate tenant
        result = await tenant_manager.migrate_tenant(tenant.id, target_region)
        
        assert result is True
        assert tenant.config['data_residency'] == target_region
        assert tenant.status == TenantStatus.ACTIVE
        
    @pytest.mark.asyncio
    async def test_migrate_nonexistent_tenant(self, tenant_manager):
        """Test that migrating non-existent tenant fails."""
        with pytest.raises(ValueError, match="Tenant not found"):
            await tenant_manager.migrate_tenant("nonexistent", "eu-west-1")


class TestTenantManagerIntegration:
    """Integration tests for tenant manager."""
    
    @pytest.mark.asyncio
    async def test_full_tenant_lifecycle(self):
        """Test complete tenant lifecycle."""
        manager = TenantManager()
        await manager.initialize()
        
        # Create tenant
        tenant = await manager.create_tenant(
            "Lifecycle Test Corp",
            TenantTier.PROFESSIONAL,
            "admin@lifecycle.com"
        )
        
        assert tenant.status == TenantStatus.PENDING
        
        # Activate tenant
        await manager.activate_tenant(tenant.id)
        assert tenant.status == TenantStatus.ACTIVE
        
        # Check metrics
        metrics = await manager.get_tenant_metrics(tenant.id)
        assert metrics["status"] == TenantStatus.ACTIVE.value
        
        # Suspend tenant
        await manager.suspend_tenant(tenant.id, "Maintenance")
        assert tenant.status == TenantStatus.SUSPENDED
        
        # Reactivate
        await manager.activate_tenant(tenant.id)
        assert tenant.status == TenantStatus.ACTIVE
        
        # Terminate
        await manager.terminate_tenant(tenant.id, preserve_data=False)
        assert manager.get_tenant(tenant.id) is None
        
    @pytest.mark.asyncio
    async def test_concurrent_tenant_operations(self):
        """Test concurrent tenant operations."""
        manager = TenantManager()
        await manager.initialize()
        
        # Create multiple tenants concurrently
        tasks = []
        for i in range(5):
            task = manager.create_tenant(
                f"Concurrent Corp {i}",
                TenantTier.STARTER,
                f"admin{i}@concurrent.com"
            )
            tasks.append(task)
            
        tenants = await asyncio.gather(*tasks)
        
        # All tenants should be created successfully
        assert len(tenants) == 5
        assert len(set(t.id for t in tenants)) == 5  # All unique IDs
        
        # Activate all tenants concurrently
        activation_tasks = [
            manager.activate_tenant(tenant.id) for tenant in tenants
        ]
        results = await asyncio.gather(*activation_tasks)
        
        # All activations should succeed
        assert all(results)
        assert all(t.status == TenantStatus.ACTIVE for t in tenants)
        
    @pytest.mark.asyncio
    async def test_tenant_quota_enforcement_integration(self):
        """Test integration between tenant creation and quota enforcement."""
        manager = TenantManager()
        await manager.initialize()
        
        # Create enterprise tenant (should have auto-scaling)
        enterprise_tenant = await manager.create_tenant(
            "Enterprise Corp",
            TenantTier.ENTERPRISE,
            "admin@enterprise.com"
        )
        
        # Create starter tenant (no auto-scaling)
        starter_tenant = await manager.create_tenant(
            "Starter Corp",
            TenantTier.STARTER,
            "admin@starter.com"
        )
        
        # Exceed quotas for both
        enterprise_tenant.update_usage(ResourceType.CPU_CORES, 999.0)
        starter_tenant.update_usage(ResourceType.CPU_CORES, 999.0)
        
        # Enforce quotas
        enterprise_actions = await manager.enforce_quotas(enterprise_tenant.id)
        starter_actions = await manager.enforce_quotas(starter_tenant.id)
        
        # Enterprise should auto-scale, starter should be throttled
        assert any("Auto-scaled" in action for action in enterprise_actions)
        assert any("Throttled" in action for action in starter_actions)


if __name__ == "__main__":
    pytest.main([__file__])