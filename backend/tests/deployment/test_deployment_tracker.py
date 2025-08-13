import asyncio
import os
import sqlite3
import tempfile
import time
import pytest
from unittest.mock import AsyncMock, patch

from src.deployment.deployment_tracker import (
    DeploymentTracker, DeployRecord, DeployEvent, DeployStatus
)


class TestDeployStatus:
    def test_enum_values(self):
        assert DeployStatus.PENDING.value == "pending"
        assert DeployStatus.DEPLOYED.value == "deployed"
        assert DeployStatus.FAILED.value == "failed"


class TestDeployEvent:
    def test_event_creation(self):
        event = DeployEvent(
            id="test123",
            timestamp=time.time(),
            status=DeployStatus.BUILDING,
            message="Building agent"
        )
        assert event.id == "test123"
        assert event.status == DeployStatus.BUILDING
        assert event.message == "Building agent"


class TestDeployRecord:
    def test_record_creation(self):
        record = DeployRecord(
            deployment_id="dep123",
            agent_name="test_agent",
            version="1.0.0",
            status=DeployStatus.PENDING,
            start_time=time.time()
        )
        assert record.deployment_id == "dep123"
        assert record.agent_name == "test_agent"
        assert record.status == DeployStatus.PENDING


class TestDeploymentTracker:
    @pytest.fixture
    def temp_db(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            yield tf.name
        os.unlink(tf.name)
    
    @pytest.fixture
    def tracker(self, temp_db):
        return DeploymentTracker(temp_db)
    
    def test_tracker_initialization(self, tracker):
        assert isinstance(tracker.active_tracks, dict)
        assert isinstance(tracker.observers, list)
        assert os.path.exists(tracker.db_path)
        
        # Check database schema
        conn = sqlite3.connect(tracker.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert "deployments" in tables
        assert "events" in tables
    
    @pytest.mark.asyncio
    async def test_start_tracking(self, tracker):
        record = await tracker.start_tracking("dep123", "test_agent", "1.0.0")
        
        assert record.deployment_id == "dep123"
        assert record.agent_name == "test_agent"
        assert record.version == "1.0.0"
        assert record.status == DeployStatus.PENDING
        assert "dep123" in tracker.active_tracks
        
        # Check database persistence
        conn = sqlite3.connect(tracker.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deployments WHERE id=?", ("dep123",))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[1] == "test_agent"  # agent_name
    
    @pytest.mark.asyncio
    async def test_update_status(self, tracker):
        # Start tracking first
        await tracker.start_tracking("dep123", "test_agent", "1.0.0")
        
        # Update status
        await tracker.update_status("dep123", DeployStatus.BUILDING, "Building started")
        
        record = tracker.active_tracks["dep123"]
        assert record.status == DeployStatus.BUILDING
        
        # Check event was logged
        assert len(record.events) >= 2  # Initial + update
        building_events = [e for e in record.events if e.status == DeployStatus.BUILDING]
        assert len(building_events) == 1
        assert building_events[0].message == "Building started"
    
    @pytest.mark.asyncio
    async def test_update_status_completion(self, tracker):
        await tracker.start_tracking("dep123", "test_agent", "1.0.0")
        
        # Update to completed status
        await tracker.update_status("dep123", DeployStatus.DEPLOYED, "Deployment complete")
        
        record = tracker.active_tracks["dep123"]
        assert record.status == DeployStatus.DEPLOYED
        assert record.end_time is not None
        assert record.end_time > record.start_time
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_deployment(self, tracker):
        # Should not raise error, just return silently
        await tracker.update_status("nonexistent", DeployStatus.FAILED, "Should be ignored")
        assert len(tracker.active_tracks) == 0
    
    def test_get_deployment_active(self, tracker):
        # Add active deployment manually
        record = DeployRecord("dep123", "test", "1.0", DeployStatus.PENDING, time.time())
        tracker.active_tracks["dep123"] = record
        
        result = tracker.get_deployment("dep123")
        assert result == record
    
    def test_get_deployment_from_db(self, tracker):
        # Insert into database directly
        conn = sqlite3.connect(tracker.db_path)
        conn.execute('''INSERT INTO deployments VALUES (?,?,?,?,?,?,?)''',
                    ("dep456", "db_agent", "1.0.0", "deployed", 
                     time.time(), time.time(), None))
        conn.execute('''INSERT INTO events VALUES (NULL,?,?,?,?,?)''',
                    ("dep456", time.time(), "deployed", "Test message", "{}"))
        conn.commit()
        conn.close()
        
        result = tracker.get_deployment("dep456")
        assert result is not None
        assert result.deployment_id == "dep456"
        assert result.agent_name == "db_agent"
        assert result.status == DeployStatus.DEPLOYED
        assert len(result.events) == 1
    
    def test_get_deployment_nonexistent(self, tracker):
        result = tracker.get_deployment("nonexistent")
        assert result is None
    
    def test_list_deployments(self, tracker):
        # Insert test data
        conn = sqlite3.connect(tracker.db_path)
        conn.execute('''INSERT INTO deployments VALUES (?,?,?,?,?,?,?)''',
                    ("dep1", "agent1", "1.0", "deployed", time.time(), time.time(), None))
        conn.execute('''INSERT INTO deployments VALUES (?,?,?,?,?,?,?)''',
                    ("dep2", "agent2", "1.0", "failed", time.time(), time.time(), "Error"))
        conn.commit()
        conn.close()
        
        # Test all deployments
        all_deployments = tracker.list_deployments()
        assert len(all_deployments) == 2
        
        # Test filtered deployments
        deployed_only = tracker.list_deployments(DeployStatus.DEPLOYED)
        assert len(deployed_only) == 1
        assert deployed_only[0].status == DeployStatus.DEPLOYED
    
    def test_get_active_deployments(self, tracker):
        # Add various status deployments
        tracker.active_tracks["active1"] = DeployRecord("active1", "test", "1.0", DeployStatus.BUILDING, time.time())
        tracker.active_tracks["active2"] = DeployRecord("active2", "test", "1.0", DeployStatus.DEPLOYING, time.time())
        tracker.active_tracks["completed"] = DeployRecord("completed", "test", "1.0", DeployStatus.DEPLOYED, time.time())
        tracker.active_tracks["failed"] = DeployRecord("failed", "test", "1.0", DeployStatus.FAILED, time.time())
        
        active = tracker.get_active_deployments()
        assert len(active) == 2  # Only BUILDING and DEPLOYING
        active_ids = [r.deployment_id for r in active]
        assert "active1" in active_ids
        assert "active2" in active_ids
        assert "completed" not in active_ids
        assert "failed" not in active_ids
    
    @pytest.mark.asyncio
    async def test_observer_notification(self, tracker):
        # Register mock observer
        observer_calls = []
        
        async def mock_observer(record):
            observer_calls.append(record)
        
        await tracker.register_observer(mock_observer)
        
        # Start tracking and update status
        await tracker.start_tracking("dep123", "test_agent", "1.0.0")
        await tracker.update_status("dep123", DeployStatus.DEPLOYED)
        
        # Observer should have been called for the status update
        assert len(observer_calls) == 1
        assert observer_calls[0].deployment_id == "dep123"
        assert observer_calls[0].status == DeployStatus.DEPLOYED
    
    @pytest.mark.asyncio
    async def test_observer_exception_handling(self, tracker):
        # Register failing observer
        async def failing_observer(record):
            raise Exception("Observer failed")
        
        await tracker.register_observer(failing_observer)
        
        # Should not raise exception
        await tracker.start_tracking("dep123", "test_agent", "1.0.0")
        await tracker.update_status("dep123", DeployStatus.DEPLOYED)
    
    def test_get_metrics(self, tracker):
        # Insert test data
        conn = sqlite3.connect(tracker.db_path)
        current_time = time.time()
        
        # Recent deployments (within 24h)
        conn.execute('''INSERT INTO deployments VALUES (?,?,?,?,?,?,?)''',
                    ("recent1", "agent1", "1.0", "deployed", current_time - 3600, current_time - 3000, None))
        conn.execute('''INSERT INTO deployments VALUES (?,?,?,?,?,?,?)''',
                    ("recent2", "agent2", "1.0", "deployed", current_time - 7200, current_time - 6600, None))
        
        # Old deployment (>24h)
        conn.execute('''INSERT INTO deployments VALUES (?,?,?,?,?,?,?)''',
                    ("old1", "agent3", "1.0", "deployed", current_time - 90000, current_time - 89400, None))
        
        # Failed deployment
        conn.execute('''INSERT INTO deployments VALUES (?,?,?,?,?,?,?)''',
                    ("failed1", "agent4", "1.0", "failed", current_time - 1800, current_time - 1200, "Error"))
        
        conn.commit()
        conn.close()
        
        # Add active deployment
        tracker.active_tracks["active1"] = DeployRecord("active1", "test", "1.0", DeployStatus.BUILDING, time.time())
        
        metrics = tracker.get_metrics()
        
        assert "status_counts" in metrics
        assert metrics["status_counts"]["deployed"] == 3
        assert metrics["status_counts"]["failed"] == 1
        assert metrics["deployments_24h"] == 2  # Only recent deployments
        assert metrics["active_count"] == 1
        assert "avg_duration" in metrics


class TestTrackerIntegration:
    @pytest.mark.asyncio
    async def test_full_tracking_lifecycle(self):
        """Test complete deployment tracking lifecycle"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        
        try:
            tracker = DeploymentTracker(db_path)
            
            # Start tracking
            record = await tracker.start_tracking("lifecycle_test", "test_agent", "2.0.0")
            assert record.status == DeployStatus.PENDING
            
            # Progress through statuses
            await tracker.update_status("lifecycle_test", DeployStatus.BUILDING, "Building agent")
            await tracker.update_status("lifecycle_test", DeployStatus.DEPLOYING, "Deploying to AgentCore")
            await tracker.update_status("lifecycle_test", DeployStatus.DEPLOYED, "Successfully deployed")
            
            # Retrieve final record
            final_record = tracker.get_deployment("lifecycle_test")
            assert final_record.status == DeployStatus.DEPLOYED
            assert final_record.end_time is not None
            assert len(final_record.events) >= 4  # Initial + 3 updates
            
            # Check metrics
            metrics = tracker.get_metrics()
            assert metrics["status_counts"]["deployed"] >= 1
            
        finally:
            os.unlink(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])