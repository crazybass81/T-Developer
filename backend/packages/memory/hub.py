"""Memory Hub core implementation for T-Developer v2.

This module provides the central memory management system that all agents
and orchestrators use to store and retrieve context information.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from .contexts import ContextType, MemoryContext, MemoryEntry
from .storage import MemoryStorage, JSONMemoryStorage


class MemoryHub:
    """Central memory management system for T-Developer v2.
    
    The Memory Hub manages 5 types of contexts as defined in AGCORE-001:
    - O_CTX: Orchestrator context for decisions and gates
    - A_CTX: Agent personal history and cache
    - S_CTX: Shared working memory
    - U_CTX: User/team specific context
    - OBS_CTX: Observability and metrics
    
    This class follows the Single Responsibility Principle (SRP) by focusing
    solely on memory management operations.
    
    Attributes:
        storage: The storage backend to use
        contexts: In-memory cache of loaded contexts
        auto_cleanup_interval: Seconds between automatic cleanup cycles
    """
    
    def __init__(
        self,
        storage: Optional[MemoryStorage] = None,
        auto_cleanup_interval: int = 3600
    ) -> None:
        """Initialize the Memory Hub.
        
        Args:
            storage: Storage backend to use (defaults to JSONMemoryStorage)
            auto_cleanup_interval: Seconds between automatic cleanup cycles
        """
        self.storage = storage or JSONMemoryStorage()
        self.contexts: Dict[ContextType, MemoryContext] = {}
        self.auto_cleanup_interval = auto_cleanup_interval
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the Memory Hub by loading existing contexts.
        
        This method should be called once before using the hub.
        It loads all existing contexts from storage and starts
        the automatic cleanup task.
        """
        if self._initialized:
            return
        
        # Load all existing contexts
        for context_type in ContextType:
            context = await self.storage.load_context(context_type)
            if context:
                self.contexts[context_type] = context
            else:
                # Create new empty context
                self.contexts[context_type] = MemoryContext(type=context_type)
        
        # Start cleanup task
        if self.auto_cleanup_interval > 0:
            self._cleanup_task = asyncio.create_task(self._auto_cleanup())
        
        self._initialized = True
    
    async def shutdown(self) -> None:
        """Shutdown the Memory Hub gracefully.
        
        Saves all contexts to storage and cancels the cleanup task.
        """
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Save all contexts
        for context in self.contexts.values():
            await self.storage.save_context(context)
        
        self._initialized = False
    
    async def _auto_cleanup(self) -> None:
        """Automatic cleanup task that runs periodically.
        
        Removes expired entries and saves contexts to storage.
        """
        while True:
            try:
                await asyncio.sleep(self.auto_cleanup_interval)
                
                # Cleanup expired entries in all contexts
                for context in self.contexts.values():
                    removed = context.cleanup_expired()
                    if removed > 0:
                        # Save context if entries were removed
                        await self.storage.save_context(context)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                # In production, use proper logging
                print(f"Error in auto cleanup: {e}")
    
    async def put(
        self,
        context_type: ContextType,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store a value in the specified context.
        
        Args:
            context_type: The context to store in
            key: Unique key for the value
            value: The value to store
            ttl_seconds: Optional time to live in seconds
            tags: Optional tags for categorization
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If hub is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Memory Hub not initialized")
        
        try:
            context = self.contexts[context_type]
            
            # Check if entry exists and update it
            existing = context.get_entry(key)
            if existing:
                existing.update(value, metadata)
            else:
                # Create new entry
                context.add_entry(
                    key=key,
                    value=value,
                    ttl_seconds=ttl_seconds,
                    tags=tags or [],
                    metadata=metadata or {}
                )
            
            # Save to storage
            await self.storage.save_context(context)
            return True
            
        except Exception as e:
            # In production, use proper logging
            print(f"Error storing in {context_type.value}: {e}")
            return False
    
    async def get(
        self,
        context_type: ContextType,
        key: str
    ) -> Optional[Any]:
        """Retrieve a value from the specified context.
        
        Args:
            context_type: The context to retrieve from
            key: The key to look up
            
        Returns:
            The stored value or None if not found/expired
            
        Raises:
            RuntimeError: If hub is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Memory Hub not initialized")
        
        context = self.contexts.get(context_type)
        if not context:
            return None
        
        entry = context.get_entry(key)
        return entry.value if entry else None
    
    # Alias methods for compatibility
    async def write(
        self,
        context_type: ContextType,
        key: str,
        value: Any,
        **kwargs
    ) -> bool:
        """Alias for put() method for backward compatibility.
        
        Args:
            context_type: The context to store in
            key: Unique key for the entry
            value: The value to store
            **kwargs: Additional arguments for MemoryEntry
            
        Returns:
            True if successful, False otherwise
        """
        return await self.put(context_type, key, value, **kwargs)
    
    async def read(
        self,
        context_type: ContextType,
        key: str
    ) -> Optional[Any]:
        """Alias for get() method for backward compatibility.
        
        Args:
            context_type: The context to retrieve from
            key: The key to look up
            
        Returns:
            The stored value or None if not found/expired
        """
        return await self.get(context_type, key)
    
    async def search(
        self,
        context_type: ContextType,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for entries in a context.
        
        Args:
            context_type: The context to search in
            tags: Optional tags to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching entries as dictionaries
            
        Raises:
            RuntimeError: If hub is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Memory Hub not initialized")
        
        context = self.contexts.get(context_type)
        if not context:
            return []
        
        if tags:
            entries = context.search_by_tags(tags)
        else:
            # Return all non-expired entries
            entries = [
                entry for entry in context.entries.values()
                if not entry.is_expired()
            ]
        
        # Convert to dictionaries and limit results
        results = []
        for entry in entries[:limit]:
            results.append({
                "key": entry.key,
                "value": entry.value,
                "tags": entry.tags,
                "metadata": entry.metadata,
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
            })
        
        return results
    
    async def delete(
        self,
        context_type: ContextType,
        key: str
    ) -> bool:
        """Delete an entry from a context.
        
        Args:
            context_type: The context to delete from
            key: The key to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            RuntimeError: If hub is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Memory Hub not initialized")
        
        context = self.contexts.get(context_type)
        if not context:
            return False
        
        success = context.remove_entry(key)
        
        if success:
            # Save to storage
            await self.storage.save_context(context)
        
        return success
    
    async def clear_context(self, context_type: ContextType) -> bool:
        """Clear all entries in a context.
        
        Args:
            context_type: The context to clear
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If hub is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Memory Hub not initialized")
        
        try:
            # Create new empty context
            self.contexts[context_type] = MemoryContext(type=context_type)
            
            # Delete from storage
            await self.storage.delete_context(context_type)
            
            return True
            
        except Exception as e:
            # In production, use proper logging
            print(f"Error clearing context {context_type.value}: {e}")
            return False
    
    async def get_context_stats(self, context_type: ContextType) -> Dict[str, Any]:
        """Get statistics about a context.
        
        Args:
            context_type: The context to get stats for
            
        Returns:
            Dictionary containing context statistics
            
        Raises:
            RuntimeError: If hub is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Memory Hub not initialized")
        
        context = self.contexts.get(context_type)
        if not context:
            return {"exists": False}
        
        # Cleanup expired entries first
        context.cleanup_expired()
        
        return {
            "exists": True,
            "type": context_type.value,
            "total_entries": len(context.entries),
            "max_entries": context.max_entries,
            "total_size_bytes": context.total_size_bytes,
            "max_size_bytes": context.max_size_bytes,
        }