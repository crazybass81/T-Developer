"""
🧬 T-Developer Dynamic Agent Loader
S3-based agent storage with runtime loading <6.5KB
"""
import hashlib
import importlib
import inspect
import json
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Type


@dataclass
class AgentInfo:
    """Agent metadata"""

    id: str
    name: str
    version: str
    size_bytes: int
    checksum: str
    capabilities: List[str]
    loaded_at: float = 0.0


@dataclass
class LoadResult:
    """Agent loading result"""

    success: bool
    agent_class: Optional[Type] = None
    agent_info: Optional[AgentInfo] = None
    error: Optional[str] = None
    load_time_us: float = 0.0


class AgentLoader:
    """Ultra-fast dynamic agent loader with 6.5KB constraint"""

    def __init__(self, cache_size: int = 100):
        self.loaded_agents: Dict[str, Type] = {}
        self.agent_info_cache: Dict[str, AgentInfo] = {}
        self.cache_size = cache_size
        self.load_stats = {"hits": 0, "misses": 0, "total_time": 0.0}

    def load_agent(self, agent_id: str, code: str, metadata: Dict[str, Any] = None) -> LoadResult:
        """Load agent from code with memory/performance validation"""
        start_time = time.perf_counter()

        try:
            # Check cache first
            if agent_id in self.loaded_agents:
                self.load_stats["hits"] += 1
                elapsed_us = (time.perf_counter() - start_time) * 1_000_000
                return LoadResult(
                    success=True,
                    agent_class=self.loaded_agents[agent_id],
                    agent_info=self.agent_info_cache.get(agent_id),
                    load_time_us=elapsed_us,
                )

            # Validate size constraint
            code_size = len(code.encode("utf-8"))
            if code_size > 6656:  # 6.5KB
                return LoadResult(
                    success=False, error=f"Agent exceeds 6.5KB limit: {code_size} bytes"
                )

            # Create agent info
            agent_info = AgentInfo(
                id=agent_id,
                name=metadata.get("name", agent_id) if metadata else agent_id,
                version=metadata.get("version", "1.0.0") if metadata else "1.0.0",
                size_bytes=code_size,
                checksum=hashlib.sha256(code.encode()).hexdigest()[:16],
                capabilities=metadata.get("capabilities", []) if metadata else [],
                loaded_at=time.time(),
            )

            # Load agent class
            agent_class = self._compile_and_load(code, agent_id)
            if not agent_class:
                return LoadResult(success=False, error="Failed to compile agent code")

            # Cache results
            self._cache_agent(agent_id, agent_class, agent_info)

            elapsed_us = (time.perf_counter() - start_time) * 1_000_000
            self.load_stats["misses"] += 1
            self.load_stats["total_time"] += elapsed_us

            return LoadResult(
                success=True,
                agent_class=agent_class,
                agent_info=agent_info,
                load_time_us=elapsed_us,
            )

        except Exception as e:
            elapsed_us = (time.perf_counter() - start_time) * 1_000_000
            return LoadResult(success=False, error=f"Load error: {str(e)}", load_time_us=elapsed_us)

    def load_from_file(self, file_path: Path, agent_id: str = None) -> LoadResult:
        """Load agent from Python file"""
        try:
            code = file_path.read_text()
            agent_id = agent_id or file_path.stem

            # Extract metadata from docstring
            metadata = self._extract_metadata(code)

            return self.load_agent(agent_id, code, metadata)
        except Exception as e:
            return LoadResult(success=False, error=f"File load error: {str(e)}")

    def instantiate_agent(self, agent_id: str, *args, **kwargs) -> Any:
        """Instantiate loaded agent with <3μs target"""
        start_time = time.perf_counter()

        if agent_id not in self.loaded_agents:
            raise ValueError(f"Agent {agent_id} not loaded")

        agent_class = self.loaded_agents[agent_id]
        instance = agent_class(*args, **kwargs)

        elapsed_us = (time.perf_counter() - start_time) * 1_000_000

        # Log if exceeds 3μs target
        if elapsed_us > 3.0:
            print(f"⚠️ Agent {agent_id} instantiation took {elapsed_us:.2f}μs (target: <3μs)")

        return instance

    def unload_agent(self, agent_id: str) -> bool:
        """Unload agent from memory"""
        if agent_id in self.loaded_agents:
            del self.loaded_agents[agent_id]
            self.agent_info_cache.pop(agent_id, None)
            return True
        return False

    def list_loaded_agents(self) -> List[AgentInfo]:
        """List all loaded agents"""
        return list(self.agent_info_cache.values())

    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information"""
        return self.agent_info_cache.get(agent_id)

    def get_load_stats(self) -> Dict[str, Any]:
        """Get loader performance statistics"""
        total_loads = self.load_stats["hits"] + self.load_stats["misses"]
        avg_time = self.load_stats["total_time"] / max(1, self.load_stats["misses"])

        return {
            "cache_hits": self.load_stats["hits"],
            "cache_misses": self.load_stats["misses"],
            "hit_rate": self.load_stats["hits"] / max(1, total_loads),
            "avg_load_time_us": avg_time,
            "total_agents": len(self.loaded_agents),
        }

    def clear_cache(self):
        """Clear agent cache"""
        self.loaded_agents.clear()
        self.agent_info_cache.clear()
        self.load_stats = {"hits": 0, "misses": 0, "total_time": 0.0}

    def _compile_and_load(self, code: str, agent_id: str) -> Optional[Type]:
        """Compile code and extract agent class"""
        try:
            # Create temporary module
            module_name = f"agent_{agent_id}_{int(time.time())}"

            # Compile code
            compiled = compile(code, f"<agent_{agent_id}>", "exec")

            # Create module namespace
            namespace = {"__name__": module_name}
            exec(compiled, namespace)

            # Find agent class (assume class with 'Agent' in name or first class)
            agent_class = None
            for name, obj in namespace.items():
                if (
                    inspect.isclass(obj)
                    and not name.startswith("_")
                    and ("agent" in name.lower() or agent_class is None)
                ):
                    agent_class = obj
                    if "agent" in name.lower():
                        break

            return agent_class

        except Exception as e:
            print(f"Compile error for {agent_id}: {e}")
            return None

    def _extract_metadata(self, code: str) -> Dict[str, Any]:
        """Extract metadata from code docstring"""
        try:
            # Simple regex-based extraction
            import re

            # Extract docstring
            docstring_match = re.search(r'"""(.*?)"""', code, re.DOTALL)
            if not docstring_match:
                return {}

            docstring = docstring_match.group(1)
            metadata = {}

            # Extract common metadata patterns
            if "capabilities:" in docstring.lower():
                caps_match = re.search(r"capabilities:\s*(.+)", docstring, re.IGNORECASE)
                if caps_match:
                    capabilities = [c.strip() for c in caps_match.group(1).split(",")]
                    metadata["capabilities"] = capabilities

            if "version:" in docstring.lower():
                ver_match = re.search(r"version:\s*(\S+)", docstring, re.IGNORECASE)
                if ver_match:
                    metadata["version"] = ver_match.group(1)

            return metadata

        except Exception:
            return {}

    def _cache_agent(self, agent_id: str, agent_class: Type, agent_info: AgentInfo):
        """Cache loaded agent with size limit"""
        # Enforce cache size limit
        if len(self.loaded_agents) >= self.cache_size:
            # Remove oldest agent (simple FIFO)
            oldest_id = min(
                self.agent_info_cache.keys(), key=lambda x: self.agent_info_cache[x].loaded_at
            )
            self.unload_agent(oldest_id)

        self.loaded_agents[agent_id] = agent_class
        self.agent_info_cache[agent_id] = agent_info


# Factory function
def create_loader(cache_size: int = 100) -> AgentLoader:
    """Create agent loader instance"""
    return AgentLoader(cache_size)


# Global loader instance
_global_loader = None


def get_global_loader() -> AgentLoader:
    """Get or create global loader instance"""
    global _global_loader
    if _global_loader is None:
        _global_loader = create_loader()
    return _global_loader


# Convenience functions
def load_agent(agent_id: str, code: str, metadata: Dict[str, Any] = None) -> LoadResult:
    """Load agent using global loader"""
    return get_global_loader().load_agent(agent_id, code, metadata)


def load_agent_file(file_path: Path, agent_id: str = None) -> LoadResult:
    """Load agent from file using global loader"""
    return get_global_loader().load_from_file(file_path, agent_id)


def instantiate(agent_id: str, *args, **kwargs) -> Any:
    """Instantiate agent using global loader"""
    return get_global_loader().instantiate_agent(agent_id, *args, **kwargs)
