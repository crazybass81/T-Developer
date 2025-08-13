"""Streaming Manager for Real-time Workflow Updates < 6.5KB"""
import asyncio
import json
import time
from typing import Dict, List, Optional, Any, AsyncGenerator, Set
from dataclasses import dataclass
from collections import defaultdict
import weakref

@dataclass
class StreamEvent:
    stream_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: float
    
class StreamingManager:
    def __init__(self):
        self.streams: Dict[str, asyncio.Queue] = {}
        self.subscribers: Dict[str, Set[str]] = defaultdict(set)
        self.stream_metadata: Dict[str, Dict] = {}
        self.buffer_size = 100
        self.cleanup_task = None
        self._refs: Dict[str, weakref.ref] = {}
        
    async def create_stream(self, stream_id: str, metadata: Optional[Dict] = None) -> asyncio.Queue:
        """Create new stream"""
        if stream_id in self.streams:
            raise ValueError(f"Stream {stream_id} already exists")
            
        queue = asyncio.Queue(maxsize=self.buffer_size)
        self.streams[stream_id] = queue
        self.stream_metadata[stream_id] = metadata or {}
        self.stream_metadata[stream_id]["created_at"] = time.time()
        
        # Start cleanup if not running
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
        return queue
        
    async def publish(self, stream_id: str, event_type: str, data: Dict[str, Any]):
        """Publish event to stream"""
        if stream_id not in self.streams:
            return
            
        event = StreamEvent(
            stream_id=stream_id,
            event_type=event_type,
            data=data,
            timestamp=time.time()
        )
        
        # Send to stream queue
        queue = self.streams[stream_id]
        try:
            await asyncio.wait_for(queue.put(event), timeout=1.0)
        except asyncio.TimeoutError:
            # Queue is full, drop oldest
            try:
                queue.get_nowait()
                await queue.put(event)
            except:
                pass
                
        # Send to subscribers
        for subscriber_id in self.subscribers[stream_id]:
            if subscriber_id in self.streams:
                subscriber_queue = self.streams[subscriber_id]
                try:
                    await asyncio.wait_for(subscriber_queue.put(event), timeout=0.1)
                except:
                    pass
                    
    async def subscribe(self, stream_id: str, subscriber_id: str):
        """Subscribe to stream events"""
        if stream_id not in self.streams:
            raise ValueError(f"Stream {stream_id} does not exist")
            
        if subscriber_id not in self.streams:
            await self.create_stream(subscriber_id)
            
        self.subscribers[stream_id].add(subscriber_id)
        
    async def unsubscribe(self, stream_id: str, subscriber_id: str):
        """Unsubscribe from stream"""
        if stream_id in self.subscribers:
            self.subscribers[stream_id].discard(subscriber_id)
            
    async def read_stream(self, stream_id: str, timeout: Optional[float] = None) -> AsyncGenerator[StreamEvent, None]:
        """Read events from stream"""
        if stream_id not in self.streams:
            raise ValueError(f"Stream {stream_id} does not exist")
            
        queue = self.streams[stream_id]
        start_time = time.time()
        
        while True:
            try:
                if timeout and (time.time() - start_time) > timeout:
                    break
                    
                event = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield event
                
            except asyncio.TimeoutError:
                if timeout and (time.time() - start_time) > timeout:
                    break
                continue
            except asyncio.CancelledError:
                break
                
    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Broadcast event to all streams"""
        tasks = []
        for stream_id in list(self.streams.keys()):
            tasks.append(self.publish(stream_id, event_type, data))
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    def close_stream(self, stream_id: str):
        """Close and remove stream"""
        if stream_id in self.streams:
            del self.streams[stream_id]
            
        if stream_id in self.stream_metadata:
            del self.stream_metadata[stream_id]
            
        if stream_id in self.subscribers:
            del self.subscribers[stream_id]
            
        # Remove as subscriber
        for subs in self.subscribers.values():
            subs.discard(stream_id)
            
    async def _cleanup_loop(self):
        """Cleanup inactive streams"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = time.time()
                inactive_streams = []
                
                for stream_id, metadata in self.stream_metadata.items():
                    # Remove streams inactive for > 5 minutes
                    if current_time - metadata.get("last_activity", metadata["created_at"]) > 300:
                        inactive_streams.append(stream_id)
                        
                for stream_id in inactive_streams:
                    self.close_stream(stream_id)
                    
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(10)
                
    def get_stream_info(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream information"""
        if stream_id not in self.streams:
            return None
            
        queue = self.streams[stream_id]
        return {
            "stream_id": stream_id,
            "queue_size": queue.qsize(),
            "max_size": queue.maxsize,
            "subscribers": list(self.subscribers.get(stream_id, [])),
            "metadata": self.stream_metadata.get(stream_id, {})
        }
        
    def list_streams(self) -> List[str]:
        """List all active streams"""
        return list(self.streams.keys())
        
    async def wait_for_event(
        self,
        stream_id: str,
        event_type: str,
        timeout: float = 30
    ) -> Optional[StreamEvent]:
        """Wait for specific event type"""
        start_time = time.time()
        
        async for event in self.read_stream(stream_id, timeout):
            if event.event_type == event_type:
                return event
            if time.time() - start_time > timeout:
                break
                
        return None
        
    async def replay_events(
        self,
        stream_id: str,
        from_timestamp: float,
        to_timestamp: Optional[float] = None
    ) -> List[StreamEvent]:
        """Replay events in time range (requires event storage)"""
        # This would require persistent event storage
        # For now, return empty list
        return []
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get streaming statistics"""
        total_queued = sum(q.qsize() for q in self.streams.values())
        total_subscribers = sum(len(subs) for subs in self.subscribers.values())
        
        return {
            "total_streams": len(self.streams),
            "total_queued_events": total_queued,
            "total_subscriptions": total_subscribers,
            "streams": [
                {
                    "id": sid,
                    "queue_size": self.streams[sid].qsize(),
                    "subscribers": len(self.subscribers.get(sid, []))
                }
                for sid in self.streams
            ]
        }

# Example usage
if __name__ == "__main__":
    async def test_streaming():
        manager = StreamingManager()
        
        # Create workflow stream
        await manager.create_stream("workflow_1")
        
        # Create subscriber
        await manager.subscribe("workflow_1", "client_1")
        
        # Publish events
        await manager.publish("workflow_1", "start", {"workflow": "test"})
        await manager.publish("workflow_1", "step", {"step": 1, "status": "running"})
        await manager.publish("workflow_1", "complete", {"result": "success"})
        
        # Read events
        events = []
        async for event in manager.read_stream("client_1", timeout=1):
            events.append(event)
            print(f"Received: {event.event_type} - {event.data}")
            
        # Get statistics
        stats = manager.get_statistics()
        print(f"Stats: {json.dumps(stats, indent=2)}")
        
    asyncio.run(test_streaming())