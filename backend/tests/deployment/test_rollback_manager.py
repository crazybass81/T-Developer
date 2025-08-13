import asyncio
import json
import os
import sqlite3
import tempfile
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.deployment.rollback_manager import (
    RollbackManager, RollbackSpec, RollbackReason
)


class TestRollbackReason:
    def test_enum_values(self):
        assert RollbackReason.MANUAL.value == "manual"
        assert RollbackReason.FAILURE.value == "failure"
        assert RollbackReason.TIMEOUT.value == "timeout"


class TestRollbackSpec:
    def test_spec_creation(self):
        spec = RollbackSpec(
            deployment_id="dep123",
            reason=RollbackReason.MANUAL,
            target_version="1.0.0"
        )
        assert spec.deployment_id == "dep123"
        assert spec.reason == RollbackReason.MANUAL
        assert spec.target_version == "1.0.0"


class TestRollbackManager:
    @pytest.fixture
    def mock_bedrock_client(self):
        with patch('boto3.client') as mock_client:
            mock_agent_client = MagicMock()
            mock_client.return_value = mock_agent_client
            yield mock_agent_client
    
    @pytest.fixture
    def manager(self, mock_bedrock_client):
        with patch.dict(os.environ, {'BEDROCK_AGENT_ID': 'test_agent_id'}):
            return RollbackManager()
    
    def test_manager_initialization(self, manager):
        assert manager.region == "us-east-1"
        assert manager.aid == "test_agent_id"
        assert isinstance(manager.rollbacks, dict)
        assert hasattr(manager, 'db')
        
        # Check database schema
        cursor = manager.db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "backups" in tables
    
    @pytest.mark.asyncio
    async def test_backup_deployment_success(self, manager, mock_bedrock_client):
        # Mock successful Bedrock responses
        mock_bedrock_client.get_agent.return_value = {
            "agent": {
                "agentId": "test_agent_id",
                "agentName": "Test Agent",
                "description": "Test description",
                "instruction": "Test instruction"
            }
        }
        mock_bedrock_client.list_agent_action_groups.return_value = {
            "actionGroupSummaries": [
                {"actionGroupId": "ag1", "actionGroupName": "Action Group 1"},
                {"actionGroupId": "ag2", "actionGroupName": "Action Group 2"}
            ]
        }
        
        result = await manager.backup_deployment("dep123", "1.0.0")
        
        assert result is True
        mock_bedrock_client.get_agent.assert_called_once_with(agentId="test_agent_id")
        mock_bedrock_client.list_agent_action_groups.assert_called_once()
        
        # Check database entry
        cursor = manager.db.cursor()
        cursor.execute("SELECT * FROM backups WHERE deployment_id=?", ("dep123",))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "dep123"  # deployment_id
        assert row[4] == "1.0.0"   # version
    
    @pytest.mark.asyncio
    async def test_backup_deployment_failure(self, manager, mock_bedrock_client):
        # Mock Bedrock failure
        mock_bedrock_client.get_agent.side_effect = Exception("API Error")
        
        result = await manager.backup_deployment("dep123", "1.0.0")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_initiate_rollback_success(self, manager, mock_bedrock_client):
        # Setup backup data in database
        agent_config = {
            "agentId": "test_agent_id",
            "agentName": "Original Agent",
            "description": "Original description",
            "instruction": "Original instruction"
        }
        action_groups = [{"actionGroupId": "ag1", "actionGroupName": "Original AG"}]
        
        manager.db.execute("INSERT INTO backups VALUES (?,?,?,?,?,?)",
                          ("dep123", json.dumps(agent_config), json.dumps(action_groups),
                           time.time(), "1.0.0", json.dumps({})))
        manager.db.commit()
        
        # Mock Bedrock responses for rollback
        mock_bedrock_client.get_agent.return_value = {"agent": agent_config}
        mock_bedrock_client.list_agent_action_groups.return_value = {
            "actionGroupSummaries": [{"actionGroupId": "current_ag", "actionGroupName": "Current AG"}]
        }
        mock_bedrock_client.update_agent.return_value = {"agentId": "test_agent_id"}
        mock_bedrock_client.delete_agent_action_group.return_value = {}
        mock_bedrock_client.prepare_agent.return_value = {"agentId": "test_agent_id"}
        
        spec = RollbackSpec("dep123", RollbackReason.MANUAL)
        result = await manager.initiate_rollback(spec)
        
        assert result["status"] == "completed"
        assert result["deployment_id"] == "dep123"
        assert result["reason"] == "manual"
        assert len(result["steps"]) >= 3
        assert "duration" in result
        
        # Verify API calls
        mock_bedrock_client.update_agent.assert_called()
        mock_bedrock_client.delete_agent_action_group.assert_called()
        mock_bedrock_client.prepare_agent.assert_called()
    
    @pytest.mark.asyncio
    async def test_initiate_rollback_no_backup(self, manager, mock_bedrock_client):
        # Mock backup creation but no existing backup for rollback target
        mock_bedrock_client.get_agent.return_value = {"agent": {"agentId": "test_agent_id"}}
        mock_bedrock_client.list_agent_action_groups.return_value = {"actionGroupSummaries": []}
        
        spec = RollbackSpec("nonexistent", RollbackReason.FAILURE)
        result = await manager.initiate_rollback(spec)
        
        assert result["status"] == "failed"
        assert "No backup found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_initiate_rollback_restore_failure(self, manager, mock_bedrock_client):
        # Setup backup data
        agent_config = {"agentId": "test_agent_id", "agentName": "Test"}
        manager.db.execute("INSERT INTO backups VALUES (?,?,?,?,?,?)",
                          ("dep123", json.dumps(agent_config), json.dumps([]),
                           time.time(), "1.0.0", json.dumps({})))
        manager.db.commit()
        
        # Mock backup creation success but restore failure
        mock_bedrock_client.get_agent.return_value = {"agent": agent_config}
        mock_bedrock_client.list_agent_action_groups.return_value = {"actionGroupSummaries": []}
        mock_bedrock_client.update_agent.side_effect = Exception("Update failed")
        
        spec = RollbackSpec("dep123", RollbackReason.FAILURE)
        result = await manager.initiate_rollback(spec)
        
        assert result["status"] == "failed"
        assert "Update failed" in result["error"]
    
    def test_get_rollback_status(self, manager):
        # Add mock rollback
        manager.rollbacks["rollback123"] = {
            "id": "rollback123",
            "status": "completed",
            "deployment_id": "dep123"
        }
        
        result = manager.get_rollback_status("rollback123")
        assert result["id"] == "rollback123"
        assert result["status"] == "completed"
        
        # Test nonexistent rollback
        result = manager.get_rollback_status("nonexistent")
        assert result is None
    
    def test_list_rollbacks(self, manager):
        # Add mock rollbacks
        manager.rollbacks["rb1"] = {"id": "rb1", "status": "completed"}
        manager.rollbacks["rb2"] = {"id": "rb2", "status": "failed"}
        
        result = manager.list_rollbacks()
        assert len(result) == 2
        assert any(r["id"] == "rb1" for r in result)
        assert any(r["id"] == "rb2" for r in result)
    
    @pytest.mark.asyncio
    async def test_cleanup_old_backups(self, manager):
        current_time = time.time()
        old_time = current_time - (40 * 86400)  # 40 days ago
        recent_time = current_time - (10 * 86400)  # 10 days ago
        
        # Insert old and recent backups
        manager.db.execute("INSERT INTO backups VALUES (?,?,?,?,?,?)",
                          ("old_backup", "{}", "[]", old_time, "1.0.0", "{}"))
        manager.db.execute("INSERT INTO backups VALUES (?,?,?,?,?,?)",
                          ("recent_backup", "{}", "[]", recent_time, "2.0.0", "{}"))
        manager.db.commit()
        
        # Cleanup backups older than 30 days
        await manager.cleanup_old_backups(30)
        
        # Check only recent backup remains
        cursor = manager.db.cursor()
        cursor.execute("SELECT deployment_id FROM backups")
        remaining = [row[0] for row in cursor.fetchall()]
        
        assert "recent_backup" in remaining
        assert "old_backup" not in remaining
    
    def test_get_backup_info(self, manager):
        # Insert backup
        backup_time = time.time()
        manager.db.execute("INSERT INTO backups VALUES (?,?,?,?,?,?)",
                          ("dep123", "{}", "[]", backup_time, "1.0.0", "{}"))
        manager.db.commit()
        
        result = manager.get_backup_info("dep123")
        assert result is not None
        assert result["deployment_id"] == "dep123"
        assert result["backup_time"] == backup_time
        assert result["version"] == "1.0.0"
        
        # Test nonexistent backup
        result = manager.get_backup_info("nonexistent")
        assert result is None


class TestRollbackIntegration:
    @pytest.mark.asyncio
    async def test_full_rollback_lifecycle(self):
        """Test complete rollback lifecycle with database persistence"""
        with patch('boto3.client') as mock_client, \
             patch.dict(os.environ, {'BEDROCK_AGENT_ID': 'test_id'}):
            
            mock_bedrock = MagicMock()
            mock_client.return_value = mock_bedrock
            
            # Setup mocks
            agent_config = {
                "agentId": "test_id",
                "agentName": "Test Agent",
                "description": "Test description",
                "instruction": "Test instruction"
            }
            
            mock_bedrock.get_agent.return_value = {"agent": agent_config}
            mock_bedrock.list_agent_action_groups.return_value = {"actionGroupSummaries": []}
            mock_bedrock.update_agent.return_value = {"agentId": "test_id"}
            mock_bedrock.prepare_agent.return_value = {"agentId": "test_id"}
            
            manager = RollbackManager()
            
            # Create backup
            backup_result = await manager.backup_deployment("integration_test", "1.0.0")
            assert backup_result is True
            
            # Initiate rollback
            spec = RollbackSpec("integration_test", RollbackReason.MANUAL)
            rollback_result = await manager.initiate_rollback(spec)
            
            assert rollback_result["status"] == "completed"
            assert rollback_result["deployment_id"] == "integration_test"
            
            # Verify rollback is tracked
            rollbacks = manager.list_rollbacks()
            assert len(rollbacks) == 1
            assert rollbacks[0]["deployment_id"] == "integration_test"
            
            # Verify backup info
            backup_info = manager.get_backup_info("integration_test")
            assert backup_info is not None
            assert backup_info["version"] == "1.0.0"


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_database_resilience(self):
        """Test that manager handles database issues gracefully"""
        with patch('boto3.client') as mock_client, \
             patch.dict(os.environ, {'BEDROCK_AGENT_ID': 'test_id'}):
            
            mock_client.return_value = MagicMock()
            
            # Create manager with invalid database path
            with patch('sqlite3.connect') as mock_connect:
                mock_connect.side_effect = Exception("Database error")
                
                # Should not crash during initialization
                try:
                    manager = RollbackManager()
                except Exception as e:
                    # Some database error is expected
                    assert "Database error" in str(e)
    
    @pytest.mark.asyncio
    async def test_aws_api_error_handling(self):
        """Test handling of AWS API errors during rollback"""
        with patch('boto3.client') as mock_client, \
             patch.dict(os.environ, {'BEDROCK_AGENT_ID': 'test_id'}):
            
            mock_bedrock = MagicMock()
            mock_client.return_value = mock_bedrock
            
            # First successful for backup creation
            mock_bedrock.get_agent.return_value = {"agent": {"agentId": "test_id"}}
            mock_bedrock.list_agent_action_groups.return_value = {"actionGroupSummaries": []}
            
            manager = RollbackManager()
            
            # Create backup successfully
            await manager.backup_deployment("error_test", "1.0.0")
            
            # Now make get_agent fail for verification step
            mock_bedrock.get_agent.side_effect = Exception("AWS API Error")
            
            spec = RollbackSpec("error_test", RollbackReason.FAILURE)
            result = await manager.initiate_rollback(spec)
            
            # Should handle the error gracefully
            assert result["status"] == "failed"
            assert "AWS API Error" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])