"""Memory storage implementations for T-Developer v2.

This module provides storage backends for the Memory Hub,
following the Dependency Inversion Principle (DIP).
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import aiofiles

from .contexts import ContextType, MemoryContext, MemoryEntry


class MemoryStorage(ABC):
    """Abstract base class for memory storage backends.
    
    This interface allows different storage implementations
    (JSON, DynamoDB, Redis, etc.) following the DIP principle.
    """
    
    @abstractmethod
    async def save_context(self, context: MemoryContext) -> bool:
        """Save a memory context to storage.
        
        Args:
            context: The MemoryContext to save
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def load_context(self, context_type: ContextType) -> Optional[MemoryContext]:
        """Load a memory context from storage.
        
        Args:
            context_type: The type of context to load
            
        Returns:
            The loaded MemoryContext or None if not found
        """
        pass
    
    @abstractmethod
    async def delete_context(self, context_type: ContextType) -> bool:
        """Delete a memory context from storage.
        
        Args:
            context_type: The type of context to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def exists(self, context_type: ContextType) -> bool:
        """Check if a context exists in storage.
        
        Args:
            context_type: The type of context to check
            
        Returns:
            True if exists, False otherwise
        """
        pass


class JSONMemoryStorage(MemoryStorage):
    """JSON file-based memory storage implementation.
    
    This is the MVP implementation using local JSON files.
    Suitable for development and small-scale deployments.
    
    Attributes:
        base_path: Base directory for storing JSON files
    """
    
    def __init__(self, base_path: str = "/tmp/t-developer/memory") -> None:
        """Initialize JSON memory storage.
        
        Args:
            base_path: Base directory path for storing memory files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, context_type: ContextType) -> Path:
        """Get the file path for a context type.
        
        Args:
            context_type: The context type
            
        Returns:
            Path to the JSON file for this context
        """
        return self.base_path / f"{context_type.value}.json"
    
    def _serialize_entry(self, entry: MemoryEntry) -> Dict[str, Any]:
        """Serialize a memory entry to JSON-compatible format.
        
        Args:
            entry: The MemoryEntry to serialize
            
        Returns:
            Dictionary representation of the entry
        """
        return {
            "id": entry.id,
            "context_type": entry.context_type.value,
            "key": entry.key,
            "value": entry.value,
            "metadata": entry.metadata,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
            "ttl_seconds": entry.ttl_seconds,
            "tags": entry.tags,
        }
    
    def _deserialize_entry(self, data: Dict[str, Any]) -> MemoryEntry:
        """Deserialize a memory entry from JSON data.
        
        Args:
            data: Dictionary containing entry data
            
        Returns:
            Reconstructed MemoryEntry
        """
        from datetime import datetime
        
        return MemoryEntry(
            id=data["id"],
            context_type=ContextType(data["context_type"]),
            key=data["key"],
            value=data["value"],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            ttl_seconds=data.get("ttl_seconds"),
            tags=data.get("tags", []),
        )
    
    async def save_context(self, context: MemoryContext) -> bool:
        """Save a memory context to a JSON file.
        
        Args:
            context: The MemoryContext to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self._get_file_path(context.type)
            
            # Serialize context data
            data = {
                "type": context.type.value,
                "max_entries": context.max_entries,
                "max_size_bytes": context.max_size_bytes,
                "entries": {
                    key: self._serialize_entry(entry)
                    for key, entry in context.entries.items()
                }
            }
            
            # Write to file asynchronously
            async with aiofiles.open(file_path, mode='w') as f:
                await f.write(json.dumps(data, indent=2))
            
            return True
            
        except Exception as e:
            # In production, use proper logging
            print(f"Error saving context {context.type.value}: {e}")
            return False
    
    async def load_context(self, context_type: ContextType) -> Optional[MemoryContext]:
        """Load a memory context from a JSON file.
        
        Args:
            context_type: The type of context to load
            
        Returns:
            The loaded MemoryContext or None if not found
        """
        try:
            file_path = self._get_file_path(context_type)
            
            if not file_path.exists():
                return None
            
            # Read file asynchronously
            async with aiofiles.open(file_path, mode='r') as f:
                content = await f.read()
                data = json.loads(content)
            
            # Reconstruct context
            context = MemoryContext(
                type=context_type,
                max_entries=data.get("max_entries"),
                max_size_bytes=data.get("max_size_bytes"),
            )
            
            # Reconstruct entries
            for key, entry_data in data.get("entries", {}).items():
                entry = self._deserialize_entry(entry_data)
                context.entries[key] = entry
            
            return context
            
        except Exception as e:
            # In production, use proper logging
            print(f"Error loading context {context_type.value}: {e}")
            return None
    
    async def delete_context(self, context_type: ContextType) -> bool:
        """Delete a memory context JSON file.
        
        Args:
            context_type: The type of context to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            file_path = self._get_file_path(context_type)
            
            if file_path.exists():
                file_path.unlink()
                return True
            
            return False
            
        except Exception as e:
            # In production, use proper logging
            print(f"Error deleting context {context_type.value}: {e}")
            return False
    
    async def exists(self, context_type: ContextType) -> bool:
        """Check if a context JSON file exists.
        
        Args:
            context_type: The type of context to check
            
        Returns:
            True if exists, False otherwise
        """
        file_path = self._get_file_path(context_type)
        return file_path.exists()