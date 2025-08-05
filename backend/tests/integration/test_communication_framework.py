#!/usr/bin/env python3
"""
Test suite for T-Developer Agent Framework Communication Layer (Tasks 3.6-3.10)
"""

import asyncio
import pytest
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from agents.framework.communication import (
    AgentMessage, MessageType, CommunicationProtocol, AgentCommunicationMixin
)
from agents.framework.message_queue import (
    MessageQueue, MessageRouter, QueueConfig, QueueType
)
from agents.framework.event_bus import (
    EventBus, Event, EventPriority, AgentEventMixin
)
from agents.framework.sync_async_layer import (
    SyncAsyncBridge, CommunicationLayer, CommunicationConfig
)
from agents.framework.data_sharing import (
    DataSharingManager, SharedData, ShareScope, DataType, AgentDataSharingMixin
)

class TestCommunication:
    """Test agent communication protocol"""
    
    def test_agent_message_creation(self):
        """Test AgentMessage creation and serialization"""
        message = AgentMessage(
            id="test-123",
            type=MessageType.REQUEST,
            sender_id="agent-1",
            recipient_id="agent-2",
            content={"action": "test"},
            timestamp=datetime.utcnow()
        )
        
        assert message.id == "test-123"
        assert message.type == MessageType.REQUEST
        assert message.sender_id == "agent-1"
        assert message.recipient_id == "agent-2"
        assert message.content["action"] == "test"
        
        # Test serialization
        data = message.to_dict()
        assert data["type"] == "request"
        assert data["content"]["action"] == "test"
        print("✅ AgentMessage creation and serialization")
    
    @pytest.mark.asyncio
    async def test_communication_protocol(self):
        """Test basic communication protocol"""
        protocol = CommunicationProtocol()
        
        # Register handler
        received_messages = []
        async def test_handler(message):
            received_messages.append(message)
        
        protocol.register_handler("request", test_handler)
        
        # Create test message
        message = AgentMessage(
            id="test-msg",
            type=MessageType.REQUEST,
            sender_id="sender",
            recipient_id="recipient",
            content={"data": "test"},
            timestamp=datetime.utcnow()
        )
        
        # Handle message
        await protocol.handle_message(message)
        
        assert len(received_messages) == 1
        assert received_messages[0].content["data"] == "test"
        print("✅ Communication protocol")

class TestMessageQueue:
    """Test message queue system"""
    
    @pytest.mark.asyncio
    async def test_memory_queue(self):
        """Test in-memory message queue"""
        config = QueueConfig(type=QueueType.MEMORY, max_size=10)
        queue = MessageQueue(config)
        await queue.initialize()
        
        # Create test message
        message = AgentMessage(
            id="queue-test",
            type=MessageType.NOTIFICATION,
            sender_id="sender",
            recipient_id="recipient",
            content={"msg": "hello"},
            timestamp=datetime.utcnow()
        )
        
        # Enqueue and dequeue
        await queue.enqueue("test-queue", message)
        retrieved = await queue.dequeue("test-queue")
        
        assert retrieved is not None
        assert retrieved.id == "queue-test"
        assert retrieved.content["msg"] == "hello"
        print("✅ Memory message queue")
    
    @pytest.mark.asyncio
    async def test_message_router(self):
        """Test message routing"""
        config = QueueConfig(type=QueueType.MEMORY)
        queue = MessageQueue(config)
        await queue.initialize()
        
        router = MessageRouter(queue)
        router.register_agent("agent-1", "queue-1")
        router.register_agent("agent-2", "queue-2")
        
        # Create message for specific agent
        message = AgentMessage(
            id="route-test",
            type=MessageType.REQUEST,
            sender_id="sender",
            recipient_id="agent-1",
            content={"route": "test"},
            timestamp=datetime.utcnow()
        )
        
        await router.route_message(message)
        
        # Check if message was routed to correct queue
        size = await queue.get_queue_size("queue-1")
        assert size == 1
        print("✅ Message routing")

class TestEventBus:
    """Test event bus system"""
    
    @pytest.mark.asyncio
    async def test_event_publishing(self):
        """Test event publishing and subscription"""
        event_bus = EventBus()
        received_events = []
        
        # Subscribe to events
        def event_handler(event):
            received_events.append(event)
        
        event_bus.subscribe("test.event", event_handler)
        
        # Publish event
        event = Event(
            id="event-1",
            type="test.event",
            data={"message": "hello"},
            timestamp=datetime.utcnow(),
            priority=EventPriority.NORMAL
        )
        
        await event_bus.publish(event)
        
        assert len(received_events) == 1
        assert received_events[0].data["message"] == "hello"
        print("✅ Event publishing and subscription")
    
    @pytest.mark.asyncio
    async def test_event_priority(self):
        """Test event priority handling"""
        event_bus = EventBus()
        execution_order = []
        
        # High priority handler
        def high_priority_handler(event):
            execution_order.append("high")
        
        # Low priority handler
        def low_priority_handler(event):
            execution_order.append("low")
        
        event_bus.subscribe("priority.test", high_priority_handler, priority=10)
        event_bus.subscribe("priority.test", low_priority_handler, priority=1)
        
        event = Event(
            id="priority-test",
            type="priority.test",
            data={},
            timestamp=datetime.utcnow()
        )
        
        await event_bus.publish(event)
        
        # High priority should execute first
        assert execution_order[0] == "high"
        assert execution_order[1] == "low"
        print("✅ Event priority handling")

class TestSyncAsyncLayer:
    """Test synchronous/asynchronous communication layer"""
    
    @pytest.mark.asyncio
    async def test_sync_async_bridge(self):
        """Test sync/async bridge"""
        config = CommunicationConfig(sync_timeout=5.0, max_workers=2)
        bridge = SyncAsyncBridge(config)
        bridge.set_event_loop(asyncio.get_event_loop())
        
        # Register sync handler
        def sync_handler(message):
            return {"result": f"processed_{message.content['data']}"}
        
        bridge.register_sync_handler("sync.test", sync_handler)
        
        # Test message
        message = AgentMessage(
            id="sync-test",
            type=MessageType.REQUEST,
            sender_id="sender",
            recipient_id="recipient",
            content={"data": "hello"},
            timestamp=datetime.utcnow()
        )
        message.type = type('MockType', (), {'value': 'sync.test'})()
        
        # Execute sync handler in async context
        result = await bridge.handle_sync_in_async(message)
        
        assert result["result"] == "processed_hello"
        print("✅ Sync/Async bridge")

class TestDataSharing:
    """Test data sharing system"""
    
    @pytest.mark.asyncio
    async def test_data_sharing_basic(self):
        """Test basic data sharing"""
        manager = DataSharingManager()
        
        # Share data
        data_id = await manager.share_data(
            owner_id="agent-1",
            data_type=DataType.STATE,
            content={"key": "value"},
            scope=ShareScope.PROJECT
        )
        
        assert data_id is not None
        
        # Retrieve data
        retrieved = await manager.get_shared_data(data_id, "agent-2")
        
        assert retrieved is not None
        assert retrieved["key"] == "value"
        print("✅ Basic data sharing")
    
    @pytest.mark.asyncio
    async def test_data_access_control(self):
        """Test data access control"""
        manager = DataSharingManager()
        
        # Share private data
        data_id = await manager.share_data(
            owner_id="agent-1",
            data_type=DataType.STATE,
            content={"secret": "data"},
            scope=ShareScope.PRIVATE
        )
        
        # Owner can access
        owner_data = await manager.get_shared_data(data_id, "agent-1")
        assert owner_data is not None
        
        # Other agent cannot access
        other_data = await manager.get_shared_data(data_id, "agent-2")
        assert other_data is None
        print("✅ Data access control")
    
    @pytest.mark.asyncio
    async def test_data_expiration(self):
        """Test data expiration"""
        manager = DataSharingManager()
        
        # Share data with short TTL
        data_id = await manager.share_data(
            owner_id="agent-1",
            data_type=DataType.RESULT,
            content={"temp": "data"},
            scope=ShareScope.GLOBAL,
            ttl_seconds=1  # 1 second TTL
        )
        
        # Should be accessible immediately
        data = await manager.get_shared_data(data_id, "agent-2")
        assert data is not None
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        expired_data = await manager.get_shared_data(data_id, "agent-2")
        assert expired_data is None
        print("✅ Data expiration")

class TestIntegratedCommunication:
    """Test integrated communication features"""
    
    @pytest.mark.asyncio
    async def test_agent_communication_mixin(self):
        """Test AgentCommunicationMixin"""
        
        class TestAgent(AgentCommunicationMixin):
            def __init__(self, agent_id):
                super().__init__()
                self.agent_id = agent_id
        
        agent = TestAgent("test-agent")
        
        # Test sending notification
        await agent.send_notification("recipient", {"message": "hello"})
        
        # Test broadcasting
        await agent.broadcast({"announcement": "system update"})
        
        assert agent.agent_id == "test-agent"
        print("✅ Agent communication mixin")
    
    @pytest.mark.asyncio
    async def test_agent_event_mixin(self):
        """Test AgentEventMixin"""
        
        class TestAgent(AgentEventMixin):
            def __init__(self, agent_id):
                super().__init__()
                self.agent_id = agent_id
        
        agent = TestAgent("event-agent")
        received_events = []
        
        # Register event handler
        @agent.on_event("agent.status")
        def status_handler(event):
            received_events.append(event)
        
        # Emit event
        await agent.emit_event("agent.status", {"status": "ready"})
        
        assert len(received_events) == 1
        assert received_events[0].data["status"] == "ready"
        print("✅ Agent event mixin")
    
    @pytest.mark.asyncio
    async def test_agent_data_sharing_mixin(self):
        """Test AgentDataSharingMixin"""
        
        class TestAgent(AgentDataSharingMixin):
            def __init__(self, agent_id):
                super().__init__()
                self.agent_id = agent_id
        
        agent1 = TestAgent("agent-1")
        agent2 = TestAgent("agent-2")
        
        # Use the same data manager instance for both agents
        shared_manager = agent1.data_manager
        agent2.data_manager = shared_manager
        
        # Share state
        data_id = await agent1.share_state({"counter": 42})
        
        # Retrieve shared state
        shared_state = await agent2.get_shared_state(data_id)
        
        assert shared_state is not None
        assert shared_state["counter"] == 42
        print("✅ Agent data sharing mixin")

async def run_all_tests():
    """Run all communication framework tests"""
    print("🧪 Testing T-Developer Agent Framework Communication Layer")
    print("=" * 60)
    
    # Test communication
    comm_test = TestCommunication()
    comm_test.test_agent_message_creation()
    await comm_test.test_communication_protocol()
    
    # Test message queue
    queue_test = TestMessageQueue()
    await queue_test.test_memory_queue()
    await queue_test.test_message_router()
    
    # Test event bus
    event_test = TestEventBus()
    await event_test.test_event_publishing()
    await event_test.test_event_priority()
    
    # Test sync/async layer
    sync_test = TestSyncAsyncLayer()
    await sync_test.test_sync_async_bridge()
    
    # Test data sharing
    data_test = TestDataSharing()
    await data_test.test_data_sharing_basic()
    await data_test.test_data_access_control()
    await data_test.test_data_expiration()
    
    # Test integrated features
    integrated_test = TestIntegratedCommunication()
    await integrated_test.test_agent_communication_mixin()
    await integrated_test.test_agent_event_mixin()
    await integrated_test.test_agent_data_sharing_mixin()
    
    print("=" * 60)
    print("✅ All communication framework tests passed!")
    print(f"📊 Framework Status:")
    print(f"   - Communication Protocol: ✅ Ready")
    print(f"   - Message Queue System: ✅ Ready")
    print(f"   - Event Bus: ✅ Ready")
    print(f"   - Sync/Async Layer: ✅ Ready")
    print(f"   - Data Sharing: ✅ Ready")
    print(f"   - Integration Mixins: ✅ Ready")

if __name__ == "__main__":
    asyncio.run(run_all_tests())