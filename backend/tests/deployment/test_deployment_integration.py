import asyncio
import os
import tempfile
import time
import pytest
from unittest.mock import MagicMock, patch

from src.deployment.agentcore_deployer import AgentCoreDeployer, AgentSpec, Status
from src.deployment.deployment_tracker import DeploymentTracker, DeployStatus
from src.deployment.rollback_manager import RollbackManager, RollbackSpec, RollbackReason


class TestDeploymentSystemIntegration:
    @pytest.fixture
    def temp_dbs(self):
        """Create temporary database files for testing"""
        tracker_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        rollback_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        
        yield tracker_db.name, rollback_db.name
        
        # Cleanup
        os.unlink(tracker_db.name)
        os.unlink(rollback_db.name)
    
    @pytest.fixture
    def mock_aws_services(self):
        """Mock all AWS services used by deployment system"""
        with patch('boto3.client') as mock_client:
            mock_bedrock_agent = MagicMock()
            mock_bedrock_runtime = MagicMock()
            
            def client_factory(service_name, **kwargs):
                if service_name == "bedrock-agent":
                    return mock_bedrock_agent
                elif service_name == "bedrock-agent-runtime":
                    return mock_bedrock_runtime
                return MagicMock()
            
            mock_client.side_effect = client_factory
            
            # Setup common successful responses
            mock_bedrock_agent.create_agent_action_group.return_value = {
                "agentActionGroup": {"actionGroupId": "test_ag_123"}
            }
            mock_bedrock_agent.update_agent.return_value = {"agentId": "test_agent_id"}
            mock_bedrock_agent.prepare_agent.return_value = {"agentId": "test_agent_id"}
            mock_bedrock_agent.get_agent.return_value = {
                "agent": {
                    "agentId": "test_agent_id",
                    "agentName": "Test Agent",
                    "description": "Test description",
                    "instruction": "Test instruction"
                }
            }
            mock_bedrock_agent.list_agent_action_groups.return_value = {
                "actionGroupSummaries": []
            }
            mock_bedrock_runtime.invoke_agent.return_value = {
                "response": "Test response"
            }
            
            yield mock_bedrock_agent, mock_bedrock_runtime
    
    @pytest.mark.asyncio
    async def test_complete_deployment_with_tracking(self, temp_dbs, mock_aws_services):
        """Test complete deployment flow with tracking integration"""
        tracker_db, rollback_db = temp_dbs
        mock_bedrock_agent, mock_bedrock_runtime = mock_aws_services
        
        with patch.dict(os.environ, {
            'BEDROCK_AGENT_ID': 'test_agent_id',
            'BEDROCK_AGENT_ALIAS_ID': 'test_alias_id'
        }):
            # Initialize components
            deployer = AgentCoreDeployer()
            tracker = DeploymentTracker(tracker_db)
            
            # Create agent spec
            spec = AgentSpec(
                name="integration_test_agent",
                code='def execute(): return {"status": "success"}',
                version="1.0.0",
                description="Integration test agent"
            )
            
            # Start deployment with tracking
            tracking_record = await tracker.start_tracking(
                "integration_deploy_123",
                spec.name,
                spec.version
            )
            assert tracking_record.status == DeployStatus.PENDING
            
            # Update tracking status to building
            await tracker.update_status(
                "integration_deploy_123",
                DeployStatus.BUILDING,
                "Agent build started"
            )
            
            # Deploy agent
            deployment_result = await deployer.deploy_agent(spec)
            assert deployment_result["status"] == Status.DEPLOYED
            
            # Update tracking status to deployed
            await tracker.update_status(
                "integration_deploy_123",
                DeployStatus.DEPLOYED,
                f"Agent deployed successfully: {deployment_result['id']}"
            )
            
            # Verify tracking record
            final_record = tracker.get_deployment("integration_deploy_123")
            assert final_record.status == DeployStatus.DEPLOYED
            assert len(final_record.events) >= 3  # pending, building, deployed
            assert final_record.end_time is not None
            
            # Test deployed agent
            test_result = await deployer.test_deployment(deployment_result["id"])
            assert test_result["status"] == "success"
            
            # Verify metrics
            metrics = tracker.get_metrics()
            assert metrics["status_counts"]["deployed"] >= 1
            assert metrics["active_count"] == 0  # No active deployments
    
    @pytest.mark.asyncio
    async def test_deployment_failure_with_tracking(self, temp_dbs, mock_aws_services):
        """Test deployment failure handling with tracking"""
        tracker_db, rollback_db = temp_dbs
        mock_bedrock_agent, mock_bedrock_runtime = mock_aws_services
        
        # Make deployment fail
        mock_bedrock_agent.create_agent_action_group.side_effect = Exception("Deployment failed")
        
        with patch.dict(os.environ, {'BEDROCK_AGENT_ID': 'test_agent_id'}):
            deployer = AgentCoreDeployer()
            tracker = DeploymentTracker(tracker_db)
            
            spec = AgentSpec(
                name="failing_agent",
                code='def execute(): pass',
                version="1.0.0"
            )
            
            # Start tracking
            await tracker.start_tracking("failing_deploy_123", spec.name, spec.version)
            await tracker.update_status("failing_deploy_123", DeployStatus.BUILDING, "Starting build")
            
            # Deploy (should fail)
            deployment_result = await deployer.deploy_agent(spec)
            assert deployment_result["status"] == Status.FAILED
            assert "Deployment failed" in deployment_result["error"]
            
            # Update tracking to failed
            await tracker.update_status(
                "failing_deploy_123",
                DeployStatus.FAILED,
                f"Deployment failed: {deployment_result['error']}"
            )
            
            # Verify tracking record
            record = tracker.get_deployment("failing_deploy_123")
            assert record.status == DeployStatus.FAILED
            
            # Verify metrics reflect failure
            metrics = tracker.get_metrics()
            assert metrics["status_counts"]["failed"] >= 1
    
    @pytest.mark.asyncio
    async def test_deployment_rollback_integration(self, temp_dbs, mock_aws_services):
        """Test deployment and rollback integration"""
        tracker_db, rollback_db = temp_dbs
        mock_bedrock_agent, mock_bedrock_runtime = mock_aws_services
        
        with patch.dict(os.environ, {'BEDROCK_AGENT_ID': 'test_agent_id'}):
            deployer = AgentCoreDeployer()
            tracker = DeploymentTracker(tracker_db)
            rollback_manager = RollbackManager()
            
            # Patch rollback manager's database to use temp file
            rollback_manager.db.close()
            rollback_manager.db = rollback_manager.__class__().__dict__['_init_backup_store'](rollback_manager)
            
            # First deployment (v1.0)
            spec_v1 = AgentSpec("rollback_test_agent", 'def v1(): return "v1"', "1.0.0")
            
            await tracker.start_tracking("rollback_deploy_v1", spec_v1.name, spec_v1.version)
            deploy_v1_result = await deployer.deploy_agent(spec_v1)
            assert deploy_v1_result["status"] == Status.DEPLOYED
            
            await tracker.update_status("rollback_deploy_v1", DeployStatus.DEPLOYED, "V1 deployed")
            
            # Create backup of v1 deployment
            backup_result = await rollback_manager.backup_deployment("rollback_deploy_v1", "1.0.0")
            assert backup_result is True
            
            # Second deployment (v2.0) - simulate problematic version
            spec_v2 = AgentSpec("rollback_test_agent", 'def v2(): return "v2"', "2.0.0")
            
            await tracker.start_tracking("rollback_deploy_v2", spec_v2.name, spec_v2.version)
            deploy_v2_result = await deployer.deploy_agent(spec_v2)
            assert deploy_v2_result["status"] == Status.DEPLOYED
            
            await tracker.update_status("rollback_deploy_v2", DeployStatus.DEPLOYED, "V2 deployed")
            
            # Initiate rollback to v1
            rollback_spec = RollbackSpec("rollback_deploy_v1", RollbackReason.FAILURE)
            rollback_result = await rollback_manager.initiate_rollback(rollback_spec)
            
            assert rollback_result["status"] == "completed"
            assert len(rollback_result["steps"]) >= 3
            
            # Update tracking for rollback
            await tracker.start_tracking(
                "rollback_operation_123", 
                "rollback_to_v1", 
                "rollback_1.0.0"
            )
            await tracker.update_status(
                "rollback_operation_123",
                DeployStatus.DEPLOYED,
                f"Rolled back to v1.0.0: {rollback_result['id']}"
            )
            
            # Verify rollback tracking
            rollback_record = tracker.get_deployment("rollback_operation_123")
            assert rollback_record.status == DeployStatus.DEPLOYED
            
            # Verify backup info
            backup_info = rollback_manager.get_backup_info("rollback_deploy_v1")
            assert backup_info is not None
            assert backup_info["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_concurrent_deployments_with_tracking(self, temp_dbs, mock_aws_services):
        """Test multiple concurrent deployments with tracking"""
        tracker_db, rollback_db = temp_dbs
        mock_bedrock_agent, mock_bedrock_runtime = mock_aws_services
        
        with patch.dict(os.environ, {'BEDROCK_AGENT_ID': 'test_agent_id'}):
            deployer = AgentCoreDeployer()
            tracker = DeploymentTracker(tracker_db)
            
            # Create multiple agent specs
            specs = [
                AgentSpec(f"concurrent_agent_{i}", f'def agent_{i}(): return {i}', "1.0.0")
                for i in range(3)
            ]
            
            # Start tracking for all deployments
            deployment_tasks = []
            for i, spec in enumerate(specs):
                deployment_id = f"concurrent_deploy_{i}"
                await tracker.start_tracking(deployment_id, spec.name, spec.version)
                await tracker.update_status(deployment_id, DeployStatus.BUILDING, f"Building agent {i}")
                
                # Create deployment task
                deployment_tasks.append(deployer.deploy_agent(spec))
            
            # Execute all deployments concurrently
            deployment_results = await asyncio.gather(*deployment_tasks, return_exceptions=True)
            
            # Update tracking for all results
            for i, result in enumerate(deployment_results):
                deployment_id = f"concurrent_deploy_{i}"
                if isinstance(result, Exception):
                    await tracker.update_status(deployment_id, DeployStatus.FAILED, str(result))
                else:
                    assert result["status"] == Status.DEPLOYED
                    await tracker.update_status(
                        deployment_id, 
                        DeployStatus.DEPLOYED, 
                        f"Agent {i} deployed: {result['id']}"
                    )
            
            # Verify all deployments were tracked
            metrics = tracker.get_metrics()
            assert metrics["status_counts"]["deployed"] == 3
            assert metrics["active_count"] == 0
            
            # Verify individual records
            for i in range(3):
                record = tracker.get_deployment(f"concurrent_deploy_{i}")
                assert record.status == DeployStatus.DEPLOYED
                assert record.agent_name == f"concurrent_agent_{i}"
    
    @pytest.mark.asyncio
    async def test_system_resilience_to_failures(self, temp_dbs, mock_aws_services):
        """Test system resilience when components fail"""
        tracker_db, rollback_db = temp_dbs
        mock_bedrock_agent, mock_bedrock_runtime = mock_aws_services
        
        with patch.dict(os.environ, {'BEDROCK_AGENT_ID': 'test_agent_id'}):
            deployer = AgentCoreDeployer()
            tracker = DeploymentTracker(tracker_db)
            
            spec = AgentSpec("resilience_test", 'def test(): pass', "1.0.0")
            
            # Start tracking
            await tracker.start_tracking("resilience_test_123", spec.name, spec.version)
            
            # Simulate AWS service intermittent failure
            mock_bedrock_agent.create_agent_action_group.side_effect = [
                Exception("Temporary failure"),  # First call fails
                {"agentActionGroup": {"actionGroupId": "recovered_ag"}}  # Second call succeeds
            ]
            
            # First deployment attempt (should fail)
            result1 = await deployer.deploy_agent(spec)
            assert result1["status"] == Status.FAILED
            
            await tracker.update_status("resilience_test_123", DeployStatus.FAILED, "First attempt failed")
            
            # Second deployment attempt (should succeed)
            result2 = await deployer.deploy_agent(spec)
            assert result2["status"] == Status.DEPLOYED
            
            # Create new tracking record for successful retry
            await tracker.start_tracking("resilience_retry_123", spec.name, spec.version)
            await tracker.update_status("resilience_retry_123", DeployStatus.DEPLOYED, "Retry succeeded")
            
            # Verify both attempts were tracked
            failed_record = tracker.get_deployment("resilience_test_123")
            assert failed_record.status == DeployStatus.FAILED
            
            success_record = tracker.get_deployment("resilience_retry_123")
            assert success_record.status == DeployStatus.DEPLOYED
            
            # Verify metrics show both outcomes
            metrics = tracker.get_metrics()
            assert metrics["status_counts"]["failed"] >= 1
            assert metrics["status_counts"]["deployed"] >= 1


class TestPerformanceIntegration:
    @pytest.mark.asyncio
    async def test_deployment_system_performance(self):
        """Test performance characteristics of integrated deployment system"""
        with patch('boto3.client') as mock_client, \
             patch.dict(os.environ, {'BEDROCK_AGENT_ID': 'test_agent_id'}):
            
            # Setup mocks for fast responses
            mock_bedrock = MagicMock()
            mock_client.return_value = mock_bedrock
            mock_bedrock.create_agent_action_group.return_value = {
                "agentActionGroup": {"actionGroupId": "perf_ag"}
            }
            mock_bedrock.update_agent.return_value = {"agentId": "test_agent_id"}
            mock_bedrock.prepare_agent.return_value = {"agentId": "test_agent_id"}
            
            # Create temporary tracker
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
                tracker_db = tf.name
            
            try:
                deployer = AgentCoreDeployer()
                tracker = DeploymentTracker(tracker_db)
                
                # Measure deployment performance
                start_time = time.perf_counter()
                
                spec = AgentSpec("perf_test", 'def perf(): return "fast"', "1.0.0")
                
                # Full deployment cycle
                await tracker.start_tracking("perf_test_123", spec.name, spec.version)
                deploy_result = await deployer.deploy_agent(spec)
                await tracker.update_status("perf_test_123", DeployStatus.DEPLOYED, "Performance test complete")
                
                end_time = time.perf_counter()
                total_time = end_time - start_time
                
                # Should complete quickly (within reasonable time for mocked operations)
                assert total_time < 1.0, f"Deployment took too long: {total_time:.2f}s"
                assert deploy_result["status"] == Status.DEPLOYED
                
                # Verify tracking overhead is minimal
                record = tracker.get_deployment("perf_test_123")
                assert record is not None
                assert record.status == DeployStatus.DEPLOYED
                
            finally:
                os.unlink(tracker_db)
    
    @pytest.mark.asyncio
    async def test_memory_efficiency_integration(self):
        """Test memory efficiency of integrated deployment system"""
        import psutil
        
        process = psutil.Process(os.getpid())
        base_memory = process.memory_info().rss
        
        with patch('boto3.client') as mock_client, \
             patch.dict(os.environ, {'BEDROCK_AGENT_ID': 'test_agent_id'}):
            
            mock_client.return_value = MagicMock()
            
            # Create multiple instances to test memory usage
            components = []
            for i in range(5):
                with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
                    tracker_db = tf.name
                
                deployer = AgentCoreDeployer()
                tracker = DeploymentTracker(tracker_db)
                rollback_manager = RollbackManager()
                
                components.append((deployer, tracker, rollback_manager, tracker_db))
            
            try:
                current_memory = process.memory_info().rss
                memory_used = current_memory - base_memory
                memory_used_mb = memory_used / (1024 * 1024)
                
                # Should use reasonable memory (under 10MB for 5 instances with mocks)
                assert memory_used_mb < 10, f"Memory usage too high: {memory_used_mb:.2f}MB"
                
                # Verify all components are functional
                for deployer, tracker, rollback_manager, _ in components:
                    assert deployer is not None
                    assert tracker is not None
                    assert rollback_manager is not None
                
            finally:
                # Cleanup
                for _, _, _, tracker_db in components:
                    try:
                        os.unlink(tracker_db)
                    except:
                        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])