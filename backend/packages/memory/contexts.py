"""Memory context definitions for T-Developer v2.

This module defines the 5 types of memory contexts and their data structures
following the AGCORE-001 specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class ContextType(Enum):
    """Memory context types as defined in AGCORE-001.
    
    Each context serves a specific purpose in the system:
    - O_CTX: Orchestrator decisions and gate records
    - A_CTX: Agent-specific history and learning
    - S_CTX: Shared working memory for current tasks
    - U_CTX: User/team specific preferences and history
    - OBS_CTX: Observability data including metrics and anomalies
    """
    
    O_CTX = "orchestrator"
    A_CTX = "agent"
    S_CTX = "shared"
    U_CTX = "user"
    OBS_CTX = "observer"


@dataclass
class MemoryEntry:
    """A single memory entry in a context.
    
    Attributes:
        id: Unique identifier for the entry
        context_type: Type of context this entry belongs to
        key: Unique key within the context
        value: The actual memory data
        metadata: Additional metadata about the entry
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        ttl_seconds: Time to live in seconds (None = permanent)
        tags: List of tags for categorization and search
    """
    
    id: str = field(default_factory=lambda: str(uuid4()))
    context_type: ContextType = ContextType.S_CTX
    key: str = ""
    value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    ttl_seconds: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    
    def is_expired(self) -> bool:
        """Check if the memory entry has expired.
        
        Returns:
            True if the entry has expired, False otherwise
        """
        if self.ttl_seconds is None:
            return False
        
        age_seconds = (datetime.utcnow() - self.created_at).total_seconds()
        return age_seconds > self.ttl_seconds
    
    def update(self, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update the memory entry value and metadata.
        
        Args:
            value: New value for the entry
            metadata: Optional new metadata to merge with existing
        """
        self.value = value
        self.updated_at = datetime.utcnow()
        
        if metadata:
            self.metadata.update(metadata)


@dataclass
class MemoryContext:
    """A memory context containing multiple entries.
    
    Attributes:
        type: The type of this context
        entries: Dictionary of entries keyed by their unique key
        max_entries: Maximum number of entries allowed (None = unlimited)
        total_size_bytes: Current total size of all entries
        max_size_bytes: Maximum total size allowed (None = unlimited)
    """
    
    type: ContextType
    entries: Dict[str, MemoryEntry] = field(default_factory=dict)
    max_entries: Optional[int] = None
    total_size_bytes: int = 0
    max_size_bytes: Optional[int] = None
    
    def add_entry(self, key: str, value: Any, **kwargs: Any) -> MemoryEntry:
        """Add a new entry to the context.
        
        Args:
            key: Unique key for the entry
            value: The value to store
            **kwargs: Additional arguments for MemoryEntry
            
        Returns:
            The created MemoryEntry
            
        Raises:
            ValueError: If max_entries would be exceeded
        """
        if self.max_entries and len(self.entries) >= self.max_entries:
            raise ValueError(f"Context {self.type.value} has reached maximum entries limit")
        
        entry = MemoryEntry(
            context_type=self.type,
            key=key,
            value=value,
            **kwargs
        )
        
        self.entries[key] = entry
        return entry
    
    def get_entry(self, key: str) -> Optional[MemoryEntry]:
        """Get an entry by key.
        
        Args:
            key: The key to look up
            
        Returns:
            The MemoryEntry if found and not expired, None otherwise
        """
        entry = self.entries.get(key)
        
        if entry and entry.is_expired():
            del self.entries[key]
            return None
        
        return entry
    
    def remove_entry(self, key: str) -> bool:
        """Remove an entry by key.
        
        Args:
            key: The key to remove
            
        Returns:
            True if removed, False if not found
        """
        if key in self.entries:
            del self.entries[key]
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self.entries.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.entries[key]
        
        return len(expired_keys)
    
    def search_by_tags(self, tags: List[str]) -> List[MemoryEntry]:
        """Search entries by tags.
        
        Args:
            tags: List of tags to search for (OR operation)
            
        Returns:
            List of matching entries
        """
        results = []
        
        for entry in self.entries.values():
            if not entry.is_expired() and any(tag in entry.tags for tag in tags):
                results.append(entry)
        
        return results