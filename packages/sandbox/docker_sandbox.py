"""Docker-based sandbox for safe code execution."""

import asyncio
import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("sandbox.docker")


@dataclass
class ResourceLimits:
    """Resource limits for sandbox."""
    cpu: float = 1.0  # CPU cores
    memory: str = "512m"  # Memory limit
    disk: str = "1g"  # Disk limit
    processes: int = 100  # Max processes


@dataclass
class SecurityPolicy:
    """Security policy for sandbox."""
    allow_network: bool = False
    allow_privileged: bool = False
    allowed_syscalls: List[str] = field(default_factory=list)
    blocked_syscalls: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)


@dataclass
class SandboxConfig:
    """Sandbox configuration."""
    cpu_limit: float = 1.0
    memory_limit: str = "512m"
    timeout: int = 300
    network_mode: str = "none"
    readonly_paths: List[str] = field(default_factory=list)
    writable_paths: List[str] = field(default_factory=lambda: ["/workspace"])
    environment: Dict[str, str] = field(default_factory=dict)
    user: str = "nobody"
    working_dir: str = "/workspace"


@dataclass
class SandboxResult:
    """Result from sandbox execution."""
    exit_code: int
    stdout: str
    stderr: str
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


class DockerSandbox:
    """Docker-based sandbox for safe code execution."""
    
    DANGEROUS_PATTERNS = [
        "rm -rf /",
        ":(){ :|:& };:",  # Fork bomb
        "dd if=/dev/zero",
        "> /etc/passwd",
        "chmod 777",
        "curl | bash",
        "wget | sh"
    ]
    
    def __init__(
        self,
        config: Optional[SandboxConfig] = None,
        security_policy: Optional[SecurityPolicy] = None
    ):
        """Initialize Docker sandbox.
        
        Args:
            config: Sandbox configuration
            security_policy: Security policy
        """
        self.config = config or SandboxConfig()
        self.security_policy = security_policy or SecurityPolicy()
        self._client = None
        self._container = None
    
    def _get_docker_client(self):
        """Get or create Docker client."""
        if self._client is None:
            try:
                import docker
                self._client = docker.from_env()
            except ImportError:
                raise RuntimeError("Docker SDK not installed: pip install docker")
            except Exception as e:
                raise RuntimeError(f"Failed to connect to Docker: {e}")
        return self._client
    
    async def validate_command(self, command: str) -> bool:
        """Validate command for safety.
        
        Args:
            command: Command to validate
            
        Returns:
            True if command is safe
        """
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in command:
                logger.warning(f"Blocked dangerous command pattern: {pattern}")
                return False
        
        return True
    
    def _create_seccomp_profile(self) -> Dict[str, Any]:
        """Create seccomp profile for syscall filtering.
        
        Returns:
            Seccomp profile dictionary
        """
        profile = {
            "defaultAction": "SCMP_ACT_ALLOW",
            "architectures": ["SCMP_ARCH_X86_64"],
            "syscalls": []
        }
        
        # Block dangerous syscalls
        if self.security_policy.blocked_syscalls:
            for syscall in self.security_policy.blocked_syscalls:
                profile["syscalls"].append({
                    "names": [syscall],
                    "action": "SCMP_ACT_ERRNO"
                })
        
        return profile
    
    def _get_container_config(self) -> Dict[str, Any]:
        """Get container configuration.
        
        Returns:
            Container configuration dictionary
        """
        config = {
            "image": "python:3.9-slim",
            "command": "tail -f /dev/null",  # Keep container running
            "detach": True,
            "network_mode": self.config.network_mode,
            "mem_limit": self.config.memory_limit,
            "cpu_quota": int(self.config.cpu_limit * 100000),
            "cpu_period": 100000,
            "user": self.config.user if not self.security_policy.allow_privileged else "root",
            "working_dir": self.config.working_dir,
            "environment": self.config.environment,
            "privileged": self.security_policy.allow_privileged,
            "remove": True,
            "security_opt": []
        }
        
        # Add volumes
        volumes = {}
        for path in self.config.readonly_paths:
            volumes[path] = {"bind": path, "mode": "ro"}
        for path in self.config.writable_paths:
            volumes[path] = {"bind": path, "mode": "rw"}
        
        if volumes:
            config["volumes"] = volumes
        
        # Add security options
        if not self.security_policy.allow_privileged:
            config["security_opt"].append("no-new-privileges")
        
        # Add seccomp profile
        seccomp = self._create_seccomp_profile()
        if seccomp["syscalls"]:
            config["security_opt"].append(f"seccomp={json.dumps(seccomp)}")
        
        # Add capabilities
        if self.security_policy.capabilities:
            config["cap_add"] = self.security_policy.capabilities
        
        return config
    
    async def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None
    ) -> SandboxResult:
        """Execute command in sandbox.
        
        Args:
            command: Command to execute
            timeout: Execution timeout in seconds
            working_dir: Working directory
            
        Returns:
            Execution result
        """
        # Validate command
        if not await self.validate_command(command):
            return SandboxResult(
                exit_code=1,
                stdout="",
                stderr="Command blocked by security policy",
                error="Dangerous command pattern detected"
            )
        
        timeout = timeout or self.config.timeout
        client = self._get_docker_client()
        
        try:
            # Create container
            config = self._get_container_config()
            if working_dir:
                config["working_dir"] = working_dir
            
            self._container = client.containers.run(**config)
            
            # Execute command
            try:
                exit_code, output = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self._container.exec_run(
                            command,
                            workdir=working_dir or self.config.working_dir
                        )
                    ),
                    timeout=timeout
                )
                
                # Decode output
                if isinstance(output, bytes):
                    output = output.decode('utf-8', errors='replace')
                
                return SandboxResult(
                    exit_code=exit_code,
                    stdout=output,
                    stderr="",
                    metrics={
                        "timeout": timeout,
                        "container_id": self._container.short_id
                    }
                )
                
            except asyncio.TimeoutError:
                return SandboxResult(
                    exit_code=-1,
                    stdout="",
                    stderr="Command timed out",
                    error="Command timed out"
                )
            
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return SandboxResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                error=str(e)
            )
        
        finally:
            # Cleanup container
            if self._container:
                try:
                    self._container.stop()
                    self._container.remove()
                except:
                    pass
                self._container = None
    
    async def execute_python(
        self,
        script: str,
        timeout: Optional[int] = None
    ) -> SandboxResult:
        """Execute Python script in sandbox.
        
        Args:
            script: Python script to execute
            timeout: Execution timeout
            
        Returns:
            Execution result
        """
        # Write script to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Execute script
            result = await self.execute(
                f"python {script_path}",
                timeout=timeout
            )
            return result
        finally:
            # Cleanup temp file
            try:
                os.unlink(script_path)
            except:
                pass
    
    async def execute_with_files(
        self,
        command: str,
        files: Dict[str, str],
        timeout: Optional[int] = None
    ) -> SandboxResult:
        """Execute command with temporary files.
        
        Args:
            command: Command to execute
            files: Dictionary of filename -> content
            timeout: Execution timeout
            
        Returns:
            Execution result
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write files
            for filename, content in files.items():
                file_path = Path(tmpdir) / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
            
            # Execute command in temp directory
            result = await self.execute(
                command,
                timeout=timeout,
                working_dir=tmpdir
            )
            
            return result
    
    def cleanup(self):
        """Cleanup sandbox resources."""
        if self._container:
            try:
                self._container.stop()
                self._container.remove()
            except:
                pass
            self._container = None
        
        if self._client:
            try:
                self._client.close()
            except:
                pass
            self._client = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.cleanup()