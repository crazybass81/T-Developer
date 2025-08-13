"""Tests for Streaming Manager"""
import pytest
import asyncio
from src.workflow.streaming_manager import StreamingManager, StreamEvent

class TestStreamingManager:
    def test_manager_initialization(self):
        """Test streaming manager initialization"""
        manager = StreamingManager()
        assert len(manager.streams) == 0
        assert len(manager.subscribers) == 0
        assert manager.buffer_size == 100
        
    @pytest.mark.asyncio
    async def test_create_stream(self):
        """Test stream creation"""
        manager = StreamingManager()
        
        queue = await manager.create_stream("test_stream", {"type": "test"})
        
        assert "test_stream" in manager.streams
        assert queue is not None
        assert manager.stream_metadata["test_stream"]["type"] == "test"
        
    @pytest.mark.asyncio
    async def test_create_duplicate_stream(self):
        """Test creating duplicate stream raises error"""
        manager = StreamingManager()
        
        await manager.create_stream("test_stream")
        
        with pytest.raises(ValueError, match="already exists"):
            await manager.create_stream("test_stream")
            
    @pytest.mark.asyncio
    async def test_publish_event(self):
        """Test publishing event to stream"""
        manager = StreamingManager()
        
        await manager.create_stream("test_stream")
        await manager.publish("test_stream", "test_event", {"data": "test"})
        
        # Read event from stream
        queue = manager.streams["test_stream"]
        assert queue.qsize() > 0
        
        event = await asyncio.wait_for(queue.get(), timeout=1)
        assert event.event_type == "test_event"
        assert event.data == {"data": "test"}
        
    @pytest.mark.asyncio
    async def test_subscribe_to_stream(self):
        """Test subscribing to stream"""
        manager = StreamingManager()
        
        await manager.create_stream("source_stream")
        await manager.subscribe("source_stream", "subscriber_1")
        
        assert "subscriber_1" in manager.subscribers["source_stream"]
        assert "subscriber_1" in manager.streams  # Subscriber stream created
        
    @pytest.mark.asyncio
    async def test_subscriber_receives_events(self):
        """Test subscribers receive published events"""
        manager = StreamingManager()
        
        # Create source and subscribe
        await manager.create_stream("source")
        await manager.subscribe("source", "subscriber")
        
        # Publish event
        await manager.publish("source", "test_event", {"value": 123})
        
        # Check subscriber received event
        subscriber_queue = manager.streams["subscriber"]
        assert subscriber_queue.qsize() > 0
        
        event = await asyncio.wait_for(subscriber_queue.get(), timeout=1)
        assert event.event_type == "test_event"
        assert event.data["value"] == 123
        
    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test unsubscribing from stream"""
        manager = StreamingManager()
        
        await manager.create_stream("source")
        await manager.subscribe("source", "subscriber")
        await manager.unsubscribe("source", "subscriber")
        
        assert "subscriber" not in manager.subscribers["source"]
        
    @pytest.mark.asyncio
    async def test_read_stream(self):
        """Test reading events from stream"""
        manager = StreamingManager()
        
        await manager.create_stream("test_stream")
        
        # Publish multiple events
        for i in range(3):
            await manager.publish("test_stream", f"event_{i}", {"index": i})
            
        # Read events
        events = []
        async for event in manager.read_stream("test_stream", timeout=1):
            events.append(event)
            
        assert len(events) == 3
        assert events[0].event_type == "event_0"
        assert events[2].data["index"] == 2
        
    @pytest.mark.asyncio
    async def test_broadcast(self):
        """Test broadcasting to all streams"""
        manager = StreamingManager()
        
        # Create multiple streams
        await manager.create_stream("stream1")
        await manager.create_stream("stream2")
        await manager.create_stream("stream3")
        
        # Broadcast event
        await manager.broadcast("broadcast_event", {"message": "hello"})
        
        # Check all streams received event
        for stream_id in ["stream1", "stream2", "stream3"]:
            queue = manager.streams[stream_id]
            assert queue.qsize() > 0
            event = await queue.get()
            assert event.event_type == "broadcast_event"
            assert event.data["message"] == "hello"
            
    def test_close_stream(self):
        """Test closing stream"""
        manager = StreamingManager()
        
        asyncio.run(manager.create_stream("test_stream"))
        manager.close_stream("test_stream")
        
        assert "test_stream" not in manager.streams
        assert "test_stream" not in manager.stream_metadata
        
    def test_get_stream_info(self):
        """Test getting stream information"""
        manager = StreamingManager()
        
        asyncio.run(manager.create_stream("test_stream", {"owner": "test"}))
        
        info = manager.get_stream_info("test_stream")
        
        assert info["stream_id"] == "test_stream"
        assert info["queue_size"] == 0
        assert info["max_size"] == 100
        assert info["metadata"]["owner"] == "test"
        
    def test_list_streams(self):
        """Test listing all streams"""
        manager = StreamingManager()
        
        asyncio.run(manager.create_stream("stream1"))
        asyncio.run(manager.create_stream("stream2"))
        
        streams = manager.list_streams()
        
        assert len(streams) == 2
        assert "stream1" in streams
        assert "stream2" in streams
        
    @pytest.mark.asyncio
    async def test_wait_for_event(self):
        """Test waiting for specific event type"""
        manager = StreamingManager()
        
        await manager.create_stream("test_stream")
        
        # Publish events in background
        async def publish_events():
            await asyncio.sleep(0.1)
            await manager.publish("test_stream", "other_event", {})
            await asyncio.sleep(0.1)
            await manager.publish("test_stream", "target_event", {"found": True})
            
        asyncio.create_task(publish_events())
        
        # Wait for specific event
        event = await manager.wait_for_event("test_stream", "target_event", timeout=1)
        
        assert event is not None
        assert event.event_type == "target_event"
        assert event.data["found"] == True
        
    def test_get_statistics(self):
        """Test getting streaming statistics"""
        manager = StreamingManager()
        
        # Create streams and subscriptions
        asyncio.run(manager.create_stream("stream1"))
        asyncio.run(manager.create_stream("stream2"))
        asyncio.run(manager.subscribe("stream1", "sub1"))
        
        stats = manager.get_statistics()
        
        assert stats["total_streams"] == 3  # stream1, stream2, sub1
        assert stats["total_subscriptions"] == 1
        assert len(stats["streams"]) == 3
        
    @pytest.mark.asyncio
    async def test_queue_overflow_handling(self):
        """Test handling of queue overflow"""
        manager = StreamingManager()
        manager.buffer_size = 2  # Small buffer for testing
        
        await manager.create_stream("test_stream")
        
        # Fill queue beyond capacity
        for i in range(5):
            await manager.publish("test_stream", f"event_{i}", {"index": i})
            
        # Queue should contain latest events
        queue = manager.streams["test_stream"]
        assert queue.qsize() <= manager.buffer_size