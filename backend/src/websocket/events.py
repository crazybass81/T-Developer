"""
WebSocket Events
이벤트 타입 및 메시지 정의
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EventType(str, Enum):
    """WebSocket 이벤트 타입"""

    # Connection events
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    ERROR = "error"

    # Project events
    PROJECT_CREATED = "project_created"
    PROJECT_STARTED = "project_started"
    PROJECT_PROGRESS = "project_progress"
    PROJECT_COMPLETED = "project_completed"
    PROJECT_FAILED = "project_failed"

    # Agent events
    AGENT_STARTED = "agent_started"
    AGENT_PROGRESS = "agent_progress"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"

    # Chat events
    CHAT_MESSAGE = "chat_message"
    CHAT_TYPING = "chat_typing"
    CHAT_READ = "chat_read"

    # System events
    NOTIFICATION = "notification"
    ALERT = "alert"
    MAINTENANCE = "maintenance"

    # Room events
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    ROOM_MESSAGE = "room_message"

    # User events
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"
    USER_STATUS_CHANGED = "user_status_changed"


class WebSocketEvent(BaseModel):
    """WebSocket 이벤트 기본 모델"""

    type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)


class ProjectEvent(WebSocketEvent):
    """프로젝트 관련 이벤트"""

    project_id: str
    user_id: str
    status: Optional[str] = None
    progress: Optional[int] = None
    message: Optional[str] = None


class AgentEvent(WebSocketEvent):
    """에이전트 관련 이벤트"""

    agent_name: str
    project_id: str
    status: str
    progress: int = 0
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ChatMessage(WebSocketEvent):
    """채팅 메시지"""

    type: EventType = EventType.CHAT_MESSAGE
    room_id: str
    user_id: str
    content: str
    reply_to: Optional[str] = None
    attachments: Optional[list] = None


class NotificationEvent(WebSocketEvent):
    """알림 이벤트"""

    type: EventType = EventType.NOTIFICATION
    level: str = "info"  # info, warning, error, critical
    title: str
    message: str
    action_url: Optional[str] = None
    auto_dismiss: bool = True
    duration: int = 5000  # milliseconds
