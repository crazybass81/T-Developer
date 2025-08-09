"""
WebSocket Connection Manager
연결 관리 및 메시지 브로드캐스팅
"""

from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
import redis.asyncio as aioredis
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/4"):
        # Active connections by user
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        
        # Room/channel subscriptions
        self.room_connections: Dict[str, Set[str]] = defaultdict(set)
        
        # User metadata
        self.user_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Redis for pub/sub across multiple servers
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.client.PubSub] = None
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0
        }
        
    async def initialize(self):
        """Initialize Redis connection for scaling"""
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
            
            # Subscribe to broadcast channel
            await self.pubsub.subscribe("websocket:broadcast")
            
            # Start listening for Redis messages
            asyncio.create_task(self._redis_listener())
            
            logger.info("WebSocket manager initialized with Redis")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        metadata: Dict[str, Any] = None
    ):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        # Store connection
        self.active_connections[user_id].append(websocket)
        
        # Store metadata
        self.user_metadata[user_id] = metadata or {}
        self.user_metadata[user_id]['connected_at'] = datetime.utcnow().isoformat()
        
        # Update stats
        self.stats['total_connections'] += 1
        
        # Notify others
        await self.broadcast_to_room(
            "system",
            {
                "type": "user_connected",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
        
        logger.info(f"User {user_id} connected via WebSocket")
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        """Handle WebSocket disconnection"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Clean up if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
                # Clean up rooms
                for room in list(self.room_connections.keys()):
                    if user_id in self.room_connections[room]:
                        self.room_connections[room].remove(user_id)
                        if not self.room_connections[room]:
                            del self.room_connections[room]
                
                # Clean up metadata
                if user_id in self.user_metadata:
                    del self.user_metadata[user_id]
                
                # Notify others
                await self.broadcast_to_room(
                    "system",
                    {
                        "type": "user_disconnected",
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
        
        logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(
        self,
        user_id: str,
        message: Dict[str, Any]
    ):
        """Send message to specific user"""
        if user_id in self.active_connections:
            message_str = json.dumps(message)
            
            # Send to all connections of this user
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message_str)
                    self.stats['messages_sent'] += 1
                except WebSocketDisconnect:
                    disconnected.append(connection)
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {e}")
                    self.stats['errors'] += 1
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                await self.disconnect(conn, user_id)
    
    async def broadcast(
        self,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None
    ):
        """Broadcast message to all connected users"""
        message_str = json.dumps(message)
        
        # Publish to Redis for other servers
        if self.redis_client:
            await self.redis_client.publish(
                "websocket:broadcast",
                json.dumps({
                    "message": message,
                    "exclude_user": exclude_user,
                    "server_id": id(self)
                })
            )
        
        # Send to local connections
        for user_id, connections in list(self.active_connections.items()):
            if user_id == exclude_user:
                continue
            
            disconnected = []
            for connection in connections:
                try:
                    await connection.send_text(message_str)
                    self.stats['messages_sent'] += 1
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected
            for conn in disconnected:
                await self.disconnect(conn, user_id)
    
    async def join_room(self, user_id: str, room: str):
        """Join a room/channel"""
        self.room_connections[room].add(user_id)
        
        # Notify room members
        await self.broadcast_to_room(
            room,
            {
                "type": "user_joined_room",
                "user_id": user_id,
                "room": room,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
        
        logger.info(f"User {user_id} joined room {room}")
    
    async def leave_room(self, user_id: str, room: str):
        """Leave a room/channel"""
        if room in self.room_connections:
            if user_id in self.room_connections[room]:
                self.room_connections[room].remove(user_id)
                
                # Clean up empty room
                if not self.room_connections[room]:
                    del self.room_connections[room]
                
                # Notify room members
                await self.broadcast_to_room(
                    room,
                    {
                        "type": "user_left_room",
                        "user_id": user_id,
                        "room": room,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
        
        logger.info(f"User {user_id} left room {room}")
    
    async def broadcast_to_room(
        self,
        room: str,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None
    ):
        """Broadcast message to all users in a room"""
        if room not in self.room_connections:
            return
        
        for user_id in self.room_connections[room]:
            if user_id == exclude_user:
                continue
            
            await self.send_personal_message(user_id, message)
    
    async def send_project_update(
        self,
        project_id: str,
        update: Dict[str, Any]
    ):
        """Send project status update"""
        await self.broadcast_to_room(
            f"project:{project_id}",
            {
                "type": "project_update",
                "project_id": project_id,
                "update": update,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def send_agent_progress(
        self,
        project_id: str,
        agent_name: str,
        progress: int,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Send agent execution progress"""
        await self.broadcast_to_room(
            f"project:{project_id}",
            {
                "type": "agent_progress",
                "project_id": project_id,
                "agent": agent_name,
                "progress": progress,
                "status": status,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def handle_message(
        self,
        websocket: WebSocket,
        user_id: str,
        message: str
    ):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            self.stats['messages_received'] += 1
            
            message_type = data.get('type')
            
            if message_type == 'ping':
                # Respond with pong
                await websocket.send_json({"type": "pong"})
                
            elif message_type == 'join_room':
                room = data.get('room')
                if room:
                    await self.join_room(user_id, room)
                    
            elif message_type == 'leave_room':
                room = data.get('room')
                if room:
                    await self.leave_room(user_id, room)
                    
            elif message_type == 'room_message':
                room = data.get('room')
                content = data.get('content')
                if room and content:
                    await self.broadcast_to_room(
                        room,
                        {
                            "type": "room_message",
                            "room": room,
                            "user_id": user_id,
                            "content": content,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        exclude_user=user_id
                    )
                    
            elif message_type == 'private_message':
                recipient = data.get('recipient')
                content = data.get('content')
                if recipient and content:
                    await self.send_personal_message(
                        recipient,
                        {
                            "type": "private_message",
                            "from": user_id,
                            "content": content,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
            
            else:
                # Unknown message type
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
                
        except json.JSONDecodeError:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid JSON"
            })
        except Exception as e:
            logger.error(f"Error handling message from {user_id}: {e}")
            self.stats['errors'] += 1
            await websocket.send_json({
                "type": "error",
                "message": "Internal server error"
            })
    
    async def _redis_listener(self):
        """Listen for Redis pub/sub messages"""
        if not self.pubsub:
            return
        
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        
                        # Don't process our own messages
                        if data.get('server_id') == id(self):
                            continue
                        
                        # Broadcast to local connections
                        msg = data.get('message')
                        exclude = data.get('exclude_user')
                        
                        for user_id, connections in self.active_connections.items():
                            if user_id == exclude:
                                continue
                            
                            for conn in connections:
                                try:
                                    await conn.send_text(json.dumps(msg))
                                except:
                                    pass
                                    
                    except Exception as e:
                        logger.error(f"Error processing Redis message: {e}")
                        
        except Exception as e:
            logger.error(f"Redis listener error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            **self.stats,
            'active_users': len(self.active_connections),
            'total_connections_now': sum(
                len(conns) for conns in self.active_connections.values()
            ),
            'active_rooms': len(self.room_connections)
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        # Close all connections
        for user_id, connections in list(self.active_connections.items()):
            for conn in connections:
                try:
                    await conn.close()
                except:
                    pass
        
        # Clear data
        self.active_connections.clear()
        self.room_connections.clear()
        self.user_metadata.clear()
        
        # Close Redis
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        
        if self.redis_client:
            await self.redis_client.close()


# Global instance
connection_manager = ConnectionManager()

# Dependency
async def get_connection_manager() -> ConnectionManager:
    """Get connection manager instance"""
    if not connection_manager.redis_client:
        await connection_manager.initialize()
    return connection_manager