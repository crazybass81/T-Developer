"""
Download Manager Module
Manages secure download operations and file serving
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import os
import json
import aiofiles
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import mimetypes


@dataclass
class DownloadSession:
    token: str
    file_path: str
    client_ip: str
    user_agent: str
    started_at: datetime
    expires_at: datetime
    download_count: int
    bytes_served: int
    completed: bool


@dataclass
class DownloadStats:
    total_downloads: int
    active_sessions: int
    bandwidth_used: int
    most_downloaded_format: str
    average_file_size: float


class DownloadManager:
    """Advanced download session and file serving management"""

    def __init__(self):
        self.version = "1.0.0"
        self.active_sessions = {}
        self.download_history = []

        self.config = {
            "max_concurrent_downloads": 10,
            "max_download_attempts": 3,
            "session_timeout_minutes": 30,
            "rate_limit_per_ip": 5,  # downloads per hour
            "chunk_size": 8192,  # bytes
            "allowed_user_agents": [],
        }

        self.mime_types = {
            ".zip": "application/zip",
            ".tar.gz": "application/gzip",
            ".tar.bz2": "application/x-bzip2",
            ".tar": "application/x-tar",
            ".json": "application/json",
            ".txt": "text/plain",
        }

    async def create_download_session(
        self, token: str, file_path: str, client_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create new download session"""

        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "File not found",
                    "error_code": "FILE_NOT_FOUND",
                }

            # Check rate limiting
            client_ip = client_info.get("client_ip", "unknown")
            if not await self._check_rate_limit(client_ip):
                return {
                    "success": False,
                    "error": "Rate limit exceeded",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                }

            # Check concurrent downloads
            if len(self.active_sessions) >= self.config["max_concurrent_downloads"]:
                return {
                    "success": False,
                    "error": "Too many concurrent downloads",
                    "error_code": "CONCURRENT_LIMIT_EXCEEDED",
                }

            # Create session
            session = DownloadSession(
                token=token,
                file_path=file_path,
                client_ip=client_ip,
                user_agent=client_info.get("user_agent", "unknown"),
                started_at=datetime.now(),
                expires_at=datetime.now()
                + timedelta(minutes=self.config["session_timeout_minutes"]),
                download_count=0,
                bytes_served=0,
                completed=False,
            )

            self.active_sessions[token] = session

            # Get file info
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            mime_type = self._get_mime_type(file_path)

            return {
                "success": True,
                "session_token": token,
                "file_info": {
                    "name": file_name,
                    "size": file_size,
                    "mime_type": mime_type,
                },
                "expires_at": session.expires_at.isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SESSION_CREATION_FAILED",
            }

    async def serve_file(
        self, token: str, range_header: Optional[str] = None
    ) -> Dict[str, Any]:
        """Serve file for download with optional range support"""

        try:
            # Validate session
            session = self.active_sessions.get(token)
            if not session:
                return {
                    "success": False,
                    "error": "Invalid or expired session",
                    "error_code": "INVALID_SESSION",
                }

            # Check session expiration
            if datetime.now() > session.expires_at:
                await self._cleanup_session(token)
                return {
                    "success": False,
                    "error": "Session expired",
                    "error_code": "SESSION_EXPIRED",
                }

            # Check file still exists
            if not os.path.exists(session.file_path):
                await self._cleanup_session(token)
                return {
                    "success": False,
                    "error": "File no longer available",
                    "error_code": "FILE_UNAVAILABLE",
                }

            # Get file info
            file_size = os.path.getsize(session.file_path)
            file_name = os.path.basename(session.file_path)
            mime_type = self._get_mime_type(session.file_path)

            # Handle range request
            start = 0
            end = file_size - 1

            if range_header:
                range_match = self._parse_range_header(range_header, file_size)
                if range_match:
                    start, end = range_match

            content_length = end - start + 1

            # Update session stats
            session.download_count += 1
            session.bytes_served += content_length

            return {
                "success": True,
                "file_path": session.file_path,
                "file_name": file_name,
                "mime_type": mime_type,
                "file_size": file_size,
                "content_range": {"start": start, "end": end, "total": file_size},
                "content_length": content_length,
                "headers": {
                    "Content-Type": mime_type,
                    "Content-Length": str(content_length),
                    "Content-Disposition": f'attachment; filename="{file_name}"',
                    "Accept-Ranges": "bytes",
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "FILE_SERVE_FAILED",
            }

    async def read_file_chunk(self, token: str, start: int, end: int) -> bytes:
        """Read specific chunk of file for streaming"""

        session = self.active_sessions.get(token)
        if not session:
            raise ValueError("Invalid session")

        chunk_size = end - start + 1

        async with aiofiles.open(session.file_path, "rb") as f:
            await f.seek(start)
            chunk = await f.read(chunk_size)
            return chunk

    async def complete_download(self, token: str) -> None:
        """Mark download as completed"""

        session = self.active_sessions.get(token)
        if session:
            session.completed = True

            # Add to history
            self.download_history.append(
                {
                    "token": token,
                    "file_path": session.file_path,
                    "client_ip": session.client_ip,
                    "started_at": session.started_at.isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "bytes_served": session.bytes_served,
                    "download_count": session.download_count,
                }
            )

            # Cleanup session
            await self._cleanup_session(token)

    async def cancel_download(self, token: str) -> None:
        """Cancel active download session"""

        await self._cleanup_session(token)

    async def get_download_stats(self) -> DownloadStats:
        """Get download statistics"""

        total_downloads = len(self.download_history)
        active_sessions = len(self.active_sessions)

        # Calculate bandwidth used
        bandwidth_used = sum(record["bytes_served"] for record in self.download_history)

        # Find most downloaded format
        format_counts = {}
        total_size = 0

        for record in self.download_history:
            file_path = record["file_path"]
            _, ext = os.path.splitext(file_path)
            format_counts[ext] = format_counts.get(ext, 0) + 1
            total_size += record["bytes_served"]

        most_downloaded_format = (
            max(format_counts.items(), key=lambda x: x[1], default=("unknown", 0))[0]
            if format_counts
            else "none"
        )

        average_file_size = total_size / total_downloads if total_downloads > 0 else 0

        return DownloadStats(
            total_downloads=total_downloads,
            active_sessions=active_sessions,
            bandwidth_used=bandwidth_used,
            most_downloaded_format=most_downloaded_format,
            average_file_size=average_file_size,
        )

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired download sessions"""

        current_time = datetime.now()
        expired_tokens = []

        for token, session in self.active_sessions.items():
            if current_time > session.expires_at:
                expired_tokens.append(token)

        for token in expired_tokens:
            await self._cleanup_session(token)

        return len(expired_tokens)

    async def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client IP has exceeded rate limit"""

        if not client_ip or client_ip == "unknown":
            return True  # Allow unknown IPs for now

        # Count downloads from this IP in the last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)

        recent_downloads = [
            record
            for record in self.download_history
            if (
                record["client_ip"] == client_ip
                and datetime.fromisoformat(record["started_at"]) > one_hour_ago
            )
        ]

        return len(recent_downloads) < self.config["rate_limit_per_ip"]

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type for file"""

        _, ext = os.path.splitext(file_path.lower())

        # Check custom MIME types first
        if ext in self.mime_types:
            return self.mime_types[ext]

        # Fallback to Python's mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"

    def _parse_range_header(
        self, range_header: str, file_size: int
    ) -> Optional[Tuple[int, int]]:
        """Parse HTTP Range header"""

        try:
            if not range_header.startswith("bytes="):
                return None

            range_spec = range_header[6:]  # Remove 'bytes='

            if "-" not in range_spec:
                return None

            start_str, end_str = range_spec.split("-", 1)

            if start_str:
                start = int(start_str)
            else:
                start = 0

            if end_str:
                end = min(int(end_str), file_size - 1)
            else:
                end = file_size - 1

            if start < 0 or end < start or start >= file_size:
                return None

            return start, end

        except (ValueError, IndexError):
            return None

    async def _cleanup_session(self, token: str) -> None:
        """Clean up download session"""

        if token in self.active_sessions:
            del self.active_sessions[token]

    def get_session_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get information about download session"""

        session = self.active_sessions.get(token)
        if not session:
            return None

        return {
            "token": session.token,
            "file_path": session.file_path,
            "started_at": session.started_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "download_count": session.download_count,
            "bytes_served": session.bytes_served,
            "completed": session.completed,
        }

    async def extend_session(self, token: str, minutes: int = 30) -> bool:
        """Extend download session expiration"""

        session = self.active_sessions.get(token)
        if not session:
            return False

        session.expires_at = datetime.now() + timedelta(minutes=minutes)
        return True
