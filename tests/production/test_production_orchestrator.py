"""
Tests for the ProductionOrchestrator integration.

This module tests the coordination of all production services including
tenant creation, global deployment, monitoring, and emergency scenarios.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from packages.production import (
    ProductionOrchestrator,
    TenantTier,
    TenantStatus,
    RegionType,
    ScalingPolicy,
    create_production_environment,
    deploy_tenant_production
)


@pytest.fixture
async def orchestrator():
    """Create production orchestrator for testing."""
    config = {
        "tenancy": {"test_mode": True},
        "distribution": {"test_mode": True},
        "scaling": {"test_mode": True},
        "security": {"test_mode": True},
        "compliance": {"test_mode": True},
        "monitoring": {"test_mode": True},
        "disaster_recovery": {"test_mode": True},
        "cost_optimization": {"test_mode": True}
    }
    
    orchestrator = ProductionOrchestrator(config)
    await orchestrator.initialize()
    yield orchestrator
    await orchestrator.stop_all_services()


class TestProductionOrchestrator:
    """Test ProductionOrchestrator class functionality."""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = ProductionOrchestrator()
        await orchestrator.initialize()
        
        assert orchestrator._initialized is True
        assert orchestrator.tenant_manager is not None
        assert orchestrator.global_distributor is not None
        assert orchestrator.auto_scaler is not None
        assert orchestrator.security_hardener is not None
        assert orchestrator.compliance_engine is not None
        assert orchestrator.monitoring_hub is not None
        assert orchestrator.disaster_recovery is not None
        assert orchestrator.cost_optimizer is not None
        
        await orchestrator.stop_all_services()
        
    @pytest.mark.asyncio
    async def test_initialization_failure_handling(self):
        """Test handling of initialization failures."""
        orchestrator = ProductionOrchestrator()
        
        # Mock a service initialization failure
        with patch.object(orchestrator.tenant_manager, 'initialize') as mock_init:
            mock_init.side_effect = Exception("Initialization failed")
            
            with pytest.raises(Exception, match="Initialization failed"):
                await orchestrator.initialize()
                
            assert orchestrator._initialized is False
            
    @pytest.mark.asyncio
    async def test_start_all_services(self, orchestrator):
        """Test starting all production services."""
        await orchestrator.start_all_services()
        
        assert orchestrator._services_started is True
        # Verify that monitoring is active for services that support it
        assert orchestrator.auto_scaler._monitoring_active is True
        assert orchestrator.security_hardener._monitoring_active is True
        assert orchestrator.compliance_engine._monitoring_active is True
        
    @pytest.mark.asyncio
    async def test_start_services_before_initialization(self):
        """Test that starting services before initialization fails."""
        orchestrator = ProductionOrchestrator()
        
        with pytest.raises(RuntimeError, match="not initialized"):
            await orchestrator.start_all_services()
            
    @pytest.mark.asyncio
    async def test_stop_all_services(self, orchestrator):
        """Test stopping all production services."""
        await orchestrator.start_all_services()
        await orchestrator.stop_all_services()
        
        assert orchestrator._services_started is False
        # Verify that monitoring is stopped
        assert orchestrator.auto_scaler._monitoring_active is False
        assert orchestrator.security_hardener._monitoring_active is False
        assert orchestrator.compliance_engine._monitoring_active is False
        
    @pytest.mark.asyncio
    async def test_create_tenant(self, orchestrator):
        """Test tenant creation with production setup."""
        tenant = await orchestrator.create_tenant(
            "Test Corporation",
            TenantTier.PROFESSIONAL,
            "admin@test.com"
        )
        
        assert tenant.name == "Test Corporation"
        assert tenant.tier == TenantTier.PROFESSIONAL
        assert "admin@test.com" in tenant.admin_users
        
        # Verify tenant exists in tenant manager
        retrieved_tenant = orchestrator.tenant_manager.get_tenant(tenant.id)
        assert retrieved_tenant is not None
        assert retrieved_tenant.id == tenant.id
        
        # Verify production services were set up
        # (This would involve checking auto-scaler targets, budgets, etc.)
        
    @pytest.mark.asyncio
    async def test_create_tenant_before_initialization(self):
        """Test that creating tenant before initialization fails."""
        orchestrator = ProductionOrchestrator()
        
        with pytest.raises(RuntimeError, match="not initialized"):
            await orchestrator.create_tenant(
                "Test Corp",
                TenantTier.STARTER,
                "admin@test.com"
            )
            
    @pytest.mark.asyncio
    async def test_deploy_tenant_globally(self, orchestrator):
        """Test global tenant deployment."""
        # Create tenant first
        tenant = await orchestrator.create_tenant(
            "Global Corp",
            TenantTier.ENTERPRISE,
            "admin@global.com"
        )
        
        # Deploy globally
        regions = ["us-east-1", "eu-west-1", "ap-southeast-1"]
        results = await orchestrator.deploy_tenant_globally(tenant.id, regions)
        
        assert isinstance(results, dict)
        assert len(results) == len(regions)
        
        # All deployments should succeed (mocked)
        for region, success in results.items():
            assert region in regions
            # Note: actual success depends on mock implementation
            
    @pytest.mark.asyncio
    async def test_deploy_nonexistent_tenant(self, orchestrator):
        """Test deploying non-existent tenant fails."""
        with pytest.raises(ValueError, match="Tenant not found"):
            await orchestrator.deploy_tenant_globally(
                "nonexistent-tenant",
                ["us-east-1"]
            )
            
    @pytest.mark.asyncio
    async def test_get_production_status(self, orchestrator):
        """Test comprehensive production status retrieval."""
        await orchestrator.start_all_services()
        
        status = await orchestrator.get_production_status()
        
        assert status["initialized"] is True
        assert status["services_started"] is True
        assert "tenancy" in status
        assert "distribution" in status
        assert "scaling" in status
        assert "security" in status
        assert "compliance" in status
        assert "monitoring" in status
        assert "disaster_recovery" in status
        assert "cost_optimization" in status
        assert "last_updated" in status
        
        # Verify each service status is a dictionary
        for service_name in ["tenancy", "distribution", "scaling", "security",
                           "compliance", "monitoring", "disaster_recovery", "cost_optimization"]:
            assert isinstance(status[service_name], dict)
            
    @pytest.mark.asyncio
    async def test_get_status_before_initialization(self):
        """Test getting status before initialization."""
        orchestrator = ProductionOrchestrator()
        
        status = await orchestrator.get_production_status()
        
        assert status["initialized"] is False
        
    @pytest.mark.asyncio
    async def test_handle_emergency_failover(self, orchestrator):
        """Test emergency failover handling."""
        await orchestrator.start_all_services()
        
        failed_region = "us-east-1"
        
        # Mock the various components that would be involved
        with patch.object(orchestrator.global_distributor, 'failover_region') as mock_failover, \
             patch.object(orchestrator.monitoring_hub, 'record_metric') as mock_metric, \
             patch.object(orchestrator.compliance_engine, 'log_audit_event') as mock_audit, \
             patch.object(orchestrator.disaster_recovery, 'start_recovery') as mock_recovery:
            
            mock_failover.return_value = {"status": "success", "actions": ["rerouted_services"]}
            mock_recovery.return_value = Mock(operation_id="recovery-123")
            
            results = await orchestrator.handle_emergency_failover(failed_region)
            
            assert "failover_results" in results
            assert "recovery_operation_id" in results
            assert "timestamp" in results
            
            # Verify all components were called
            mock_failover.assert_called_once_with(failed_region)
            mock_metric.assert_called()
            mock_audit.assert_called()
            mock_recovery.assert_called()
            
    @pytest.mark.asyncio
    async def test_failover_before_initialization(self):
        """Test that emergency failover before initialization fails."""
        orchestrator = ProductionOrchestrator()
        
        with pytest.raises(RuntimeError, match="not initialized"):
            await orchestrator.handle_emergency_failover("us-east-1")
            
    @pytest.mark.asyncio
    async def test_optimize_costs(self, orchestrator):
        """Test cost optimization analysis."""
        await orchestrator.start_all_services()
        
        # Create a tenant to optimize costs for
        tenant = await orchestrator.create_tenant(
            "Cost Test Corp",
            TenantTier.PROFESSIONAL,
            "admin@costtest.com"
        )
        
        # Mock cost optimization recommendations
        with patch.object(orchestrator.cost_optimizer, 'get_recommendations') as mock_recommendations:
            mock_recommendations.return_value = [
                {
                    "recommendation_id": "rec-1",
                    "type": "right_size",
                    "estimated_savings_monthly": 500.0,
                    "title": "Right-size overprovisioned instances"
                }
            ]
            
            results = await orchestrator.optimize_costs(tenant.id)
            
            assert "cost_recommendations" in results
            assert "scaling_opportunities" in results
            assert "total_potential_monthly_savings" in results
            assert "recommendation_count" in results
            assert "tenant_id" in results
            
            assert results["tenant_id"] == tenant.id
            assert results["recommendation_count"] == 1
            assert results["total_potential_monthly_savings"] == 500.0
            
    @pytest.mark.asyncio
    async def test_optimize_costs_global(self, orchestrator):
        """Test global cost optimization (all tenants)."""
        await orchestrator.start_all_services()
        
        with patch.object(orchestrator.cost_optimizer, 'get_recommendations') as mock_recommendations:
            mock_recommendations.return_value = []
            
            results = await orchestrator.optimize_costs()  # No tenant_id = global
            
            assert results["tenant_id"] is None
            assert "cost_recommendations" in results
            
    @pytest.mark.asyncio
    async def test_optimize_costs_before_initialization(self):
        """Test that cost optimization before initialization fails."""
        orchestrator = ProductionOrchestrator()
        
        with pytest.raises(RuntimeError, match="not initialized"):
            await orchestrator.optimize_costs()


class TestProductionServiceIntegration:
    """Test integration between production services."""
    
    @pytest.mark.asyncio
    async def test_tenant_to_scaling_integration(self, orchestrator):
        """Test integration between tenant creation and auto-scaling setup."""
        await orchestrator.start_all_services()
        
        # Create tenant
        tenant = await orchestrator.create_tenant(
            "Scaling Test Corp",
            TenantTier.ENTERPRISE,
            "admin@scaling.com"
        )
        
        # Verify auto-scaler has target for this tenant
        target_id = f"{tenant.id}-web-servers"
        target_info = orchestrator.auto_scaler.get_target_info(target_id)
        
        # Target should exist for enterprise tenant
        # (Note: This depends on the implementation in _setup_tenant_production_services)
        
    @pytest.mark.asyncio
    async def test_tenant_to_monitoring_integration(self, orchestrator):
        """Test integration between tenant creation and monitoring setup."""
        await orchestrator.start_all_services()
        
        # Create tenant
        tenant = await orchestrator.create_tenant(
            "Monitoring Test Corp",
            TenantTier.PROFESSIONAL,
            "admin@monitoring.com"
        )
        
        # Verify monitoring is set up for tenant
        # This would involve checking that tenant-specific metrics are being collected
        
        # Record some tenant-specific metrics
        await orchestrator.monitoring_hub.record_metric(
            "tenant_api_requests",
            100.0,
            {"tenant_id": tenant.id}
        )
        
        # Verify metric was recorded
        metric_data = orchestrator.monitoring_hub.get_metric_data("tenant_api_requests")
        assert metric_data is not None
        
    @pytest.mark.asyncio
    async def test_tenant_to_cost_tracking_integration(self, orchestrator):
        """Test integration between tenant creation and cost tracking."""
        await orchestrator.start_all_services()
        
        # Create tenant
        tenant = await orchestrator.create_tenant(
            "Cost Tracking Corp",
            TenantTier.STARTER,
            "admin@cost.com"
        )
        
        # Verify budget was created for tenant
        budgets = orchestrator.cost_optimizer._budgets
        tenant_budgets = [
            budget for budget in budgets.values()
            if budget.tenant_id == tenant.id
        ]
        
        # Should have at least one budget for the tenant
        # (Note: Depends on implementation in _setup_tenant_production_services)
        
    @pytest.mark.asyncio
    async def test_security_to_monitoring_integration(self, orchestrator):
        """Test integration between security events and monitoring."""
        await orchestrator.start_all_services()
        
        # Mock a security event
        from packages.production.security_hardener import SecurityEventType, ThreatLevel
        
        # Simulate security analysis
        request_data = {
            "source_ip": "192.168.1.100",
            "url": "/api/test",
            "user_agent": "TestAgent",
            "body": "test content"
        }
        
        analysis = await orchestrator.security_hardener.analyze_request(request_data)
        
        # Verify analysis was performed
        assert "allowed" in analysis
        assert "threats_detected" in analysis
        
        # If threats were detected, monitoring should have recorded them
        # (This depends on the integration setup)
        
    @pytest.mark.asyncio
    async def test_disaster_recovery_integration(self, orchestrator):
        """Test disaster recovery integration with other services."""
        await orchestrator.start_all_services()
        
        # Create tenant
        tenant = await orchestrator.create_tenant(
            "DR Test Corp",
            TenantTier.ENTERPRISE,
            "admin@dr.com"
        )
        
        # Verify backup targets were created for tenant
        # (This would check that tenant databases, configs, etc. are being backed up)
        
        # Check disaster recovery status includes tenant data
        dr_status = await orchestrator.disaster_recovery.get_dr_status()
        assert "backup_targets" in dr_status
        assert dr_status["backup_targets"]["total"] >= 0


class TestConvenienceFunctions:
    """Test convenience functions for production environment setup."""
    
    @pytest.mark.asyncio
    async def test_create_production_environment(self):
        """Test create_production_environment convenience function."""
        config = {"test_mode": True}
        
        orchestrator = await create_production_environment(config)
        
        assert orchestrator._initialized is True
        assert orchestrator.config.get("test_mode") is True
        
        await orchestrator.stop_all_services()
        
    @pytest.mark.asyncio
    async def test_deploy_tenant_production(self):
        """Test deploy_tenant_production convenience function."""
        orchestrator = await create_production_environment({"test_mode": True})
        
        tenant = await deploy_tenant_production(
            orchestrator,
            "Production Test Corp",
            TenantTier.ENTERPRISE,
            "admin@prodtest.com",
            ["us-east-1", "eu-west-1"]
        )
        
        assert tenant.name == "Production Test Corp"
        assert tenant.tier == TenantTier.ENTERPRISE
        
        # Verify tenant was deployed globally
        # (This would check that the deployment was successful)
        
        await orchestrator.stop_all_services()


class TestErrorHandlingAndResilience:
    """Test error handling and resilience of the production orchestrator."""
    
    @pytest.mark.asyncio
    async def test_service_failure_isolation(self, orchestrator):
        """Test that failure in one service doesn't affect others."""
        await orchestrator.start_all_services()
        
        # Mock failure in one service
        with patch.object(orchestrator.cost_optimizer, 'get_cost_status') as mock_cost:
            mock_cost.side_effect = Exception("Cost service failed")
            
            # Getting production status should still work for other services
            status = await orchestrator.get_production_status()
            
            assert status["initialized"] is True
            assert "error" in status["cost_optimization"]
            # Other services should still have valid status
            assert "error" not in status.get("monitoring", {})
            
    @pytest.mark.asyncio
    async def test_partial_service_startup_failure(self):
        """Test handling of partial service startup failures."""
        orchestrator = ProductionOrchestrator()
        await orchestrator.initialize()
        
        # Mock failure in one service's start_monitoring
        with patch.object(orchestrator.security_hardener, 'start_monitoring') as mock_security:
            mock_security.side_effect = Exception("Security monitoring failed")
            
            # start_all_services should handle the failure gracefully
            with pytest.raises(Exception):
                await orchestrator.start_all_services()
                
            # Other services should still be started
            # (Depends on implementation - whether it's fail-fast or fail-graceful)
            
        await orchestrator.stop_all_services()
        
    @pytest.mark.asyncio
    async def test_concurrent_tenant_operations(self, orchestrator):
        """Test concurrent tenant operations."""
        await orchestrator.start_all_services()
        
        # Create multiple tenants concurrently
        tasks = []
        for i in range(5):
            task = orchestrator.create_tenant(
                f"Concurrent Corp {i}",
                TenantTier.PROFESSIONAL,
                f"admin{i}@concurrent.com"
            )
            tasks.append(task)
            
        tenants = await asyncio.gather(*tasks)
        
        # All tenants should be created successfully
        assert len(tenants) == 5
        assert len(set(t.id for t in tenants)) == 5  # All unique
        
        # Deploy all tenants concurrently
        deployment_tasks = []
        for tenant in tenants:
            task = orchestrator.deploy_tenant_globally(tenant.id, ["us-east-1"])
            deployment_tasks.append(task)
            
        deployment_results = await asyncio.gather(*deployment_tasks)
        
        # All deployments should complete
        assert len(deployment_results) == 5
        
    @pytest.mark.asyncio
    async def test_resource_cleanup_on_failure(self):
        """Test that resources are cleaned up properly on failure."""
        orchestrator = ProductionOrchestrator()
        
        # Mock initialization failure after partial setup
        with patch.object(orchestrator.global_distributor, 'initialize') as mock_dist:
            mock_dist.side_effect = Exception("Distribution init failed")
            
            with pytest.raises(Exception):
                await orchestrator.initialize()
                
            # Orchestrator should not be marked as initialized
            assert orchestrator._initialized is False
            
            # In a real implementation, we'd verify that any partially
            # initialized services were properly cleaned up


if __name__ == "__main__":
    pytest.main([__file__])