"""Tests for Docker Sandbox implementation."""

import asyncio
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from packages.sandbox.docker_sandbox import (
    DockerSandbox,
    SandboxConfig,
    SandboxResult,
    ResourceLimits,
    SecurityPolicy
)


class TestSandboxConfig:
    """Test sandbox configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SandboxConfig()
        
        assert config.cpu_limit == 1.0
        assert config.memory_limit == "512m"
        assert config.timeout == 300
        assert config.network_mode == "none"
        assert config.readonly_paths == []
        assert config.writable_paths == ["/workspace"]
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = SandboxConfig(
            cpu_limit=2.0,
            memory_limit="1g",
            timeout=600,
            network_mode="bridge"
        )
        
        assert config.cpu_limit == 2.0
        assert config.memory_limit == "1g"
        assert config.timeout == 600
        assert config.network_mode == "bridge"
    
    def test_resource_limits(self):
        """Test resource limits configuration."""
        limits = ResourceLimits(
            cpu=0.5,
            memory="256m",
            disk="1g",
            processes=50
        )
        
        assert limits.cpu == 0.5
        assert limits.memory == "256m"
        assert limits.disk == "1g"
        assert limits.processes == 50
    
    def test_security_policy(self):
        """Test security policy configuration."""
        policy = SecurityPolicy(
            allow_network=False,
            allow_privileged=False,
            allowed_syscalls=["read", "write", "open"],
            blocked_syscalls=["fork", "exec"],
            capabilities=["NET_ADMIN"]
        )
        
        assert policy.allow_network is False
        assert policy.allow_privileged is False
        assert "read" in policy.allowed_syscalls
        assert "fork" in policy.blocked_syscalls
        assert "NET_ADMIN" in policy.capabilities


class TestDockerSandbox:
    """Test Docker sandbox functionality."""
    
    @pytest.fixture
    def sandbox(self):
        """Create sandbox instance."""
        config = SandboxConfig()
        return DockerSandbox(config)
    
    @pytest.mark.asyncio
    async def test_execute_simple_command(self, sandbox):
        """Test executing a simple command."""
        with patch('docker.from_env') as mock_docker:
            # Mock container
            mock_container = Mock()
            mock_container.exec_run.return_value = (0, b"Hello World\n")
            mock_container.status = "running"
            
            # Mock Docker client
            mock_client = Mock()
            mock_client.containers.run.return_value = mock_container
            mock_docker.return_value = mock_client
            
            result = await sandbox.execute(
                command="echo 'Hello World'",
                timeout=10
            )
            
            assert result.exit_code == 0
            assert result.stdout == "Hello World\n"
            assert result.stderr == ""
            assert result.error is None
    
    @pytest.mark.asyncio
    async def test_execute_with_timeout(self, sandbox):
        """Test command timeout."""
        with patch('docker.from_env') as mock_docker:
            # Mock container that times out
            mock_container = Mock()
            mock_container.exec_run.side_effect = TimeoutError("Command timed out")
            mock_container.status = "running"
            
            mock_client = Mock()
            mock_client.containers.run.return_value = mock_container
            mock_docker.return_value = mock_client
            
            result = await sandbox.execute(
                command="sleep 100",
                timeout=1
            )
            
            assert result.exit_code != 0
            assert result.error == "Command timed out"
    
    @pytest.mark.asyncio
    async def test_execute_with_working_dir(self, sandbox):
        """Test execution with working directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            
            with patch('docker.from_env') as mock_docker:
                mock_container = Mock()
                mock_container.exec_run.return_value = (0, b"test content\n")
                
                mock_client = Mock()
                mock_client.containers.run.return_value = mock_container
                mock_docker.return_value = mock_client
                
                result = await sandbox.execute(
                    command="cat test.txt",
                    working_dir=tmpdir,
                    timeout=10
                )
                
                assert result.exit_code == 0
                assert "test content" in result.stdout
    
    @pytest.mark.asyncio
    async def test_execute_python_script(self, sandbox):
        """Test executing Python script."""
        script = """
import sys
print("Python version:", sys.version)
print("Hello from Python!")
"""
        
        with patch('docker.from_env') as mock_docker:
            mock_container = Mock()
            mock_container.exec_run.return_value = (
                0,
                b"Python version: 3.9.0\nHello from Python!\n"
            )
            
            mock_client = Mock()
            mock_client.containers.run.return_value = mock_container
            mock_docker.return_value = mock_client
            
            result = await sandbox.execute_python(
                script=script,
                timeout=10
            )
            
            assert result.exit_code == 0
            assert "Hello from Python!" in result.stdout
            assert "Python version:" in result.stdout
    
    @pytest.mark.asyncio
    async def test_resource_limits_enforcement(self, sandbox):
        """Test resource limits are enforced."""
        sandbox.config.cpu_limit = 0.5
        sandbox.config.memory_limit = "256m"
        
        with patch('docker.from_env') as mock_docker:
            mock_client = Mock()
            mock_docker.return_value = mock_client
            
            await sandbox.execute("echo test", timeout=10)
            
            # Verify container was created with limits
            mock_client.containers.run.assert_called_once()
            call_kwargs = mock_client.containers.run.call_args[1]
            
            assert call_kwargs['cpu_quota'] == 50000  # 0.5 CPU
            assert call_kwargs['mem_limit'] == "256m"
    
    @pytest.mark.asyncio
    async def test_network_isolation(self, sandbox):
        """Test network isolation."""
        sandbox.config.network_mode = "none"
        
        with patch('docker.from_env') as mock_docker:
            mock_client = Mock()
            mock_docker.return_value = mock_client
            
            await sandbox.execute("ping google.com", timeout=5)
            
            # Verify container was created with no network
            call_kwargs = mock_client.containers.run.call_args[1]
            assert call_kwargs['network_mode'] == "none"
    
    @pytest.mark.asyncio
    async def test_filesystem_isolation(self, sandbox):
        """Test filesystem isolation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox.config.readonly_paths = ["/etc"]
            sandbox.config.writable_paths = [tmpdir]
            
            with patch('docker.from_env') as mock_docker:
                mock_client = Mock()
                mock_docker.return_value = mock_client
                
                await sandbox.execute("ls /", timeout=10)
                
                # Verify volumes were mounted correctly
                call_kwargs = mock_client.containers.run.call_args[1]
                assert 'volumes' in call_kwargs
    
    @pytest.mark.asyncio
    async def test_cleanup_on_error(self, sandbox):
        """Test container cleanup on error."""
        with patch('docker.from_env') as mock_docker:
            mock_container = Mock()
            mock_container.exec_run.side_effect = Exception("Test error")
            mock_container.stop = Mock()
            mock_container.remove = Mock()
            
            mock_client = Mock()
            mock_client.containers.run.return_value = mock_container
            mock_docker.return_value = mock_client
            
            result = await sandbox.execute("test command", timeout=10)
            
            # Verify cleanup was called
            mock_container.stop.assert_called_once()
            mock_container.remove.assert_called_once()
            
            assert result.error == "Test error"
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self, sandbox):
        """Test concurrent sandbox execution."""
        with patch('docker.from_env') as mock_docker:
            mock_container = Mock()
            mock_container.exec_run.return_value = (0, b"Success\n")
            
            mock_client = Mock()
            mock_client.containers.run.return_value = mock_container
            mock_docker.return_value = mock_client
            
            # Run multiple commands concurrently
            tasks = [
                sandbox.execute(f"echo 'Task {i}'", timeout=10)
                for i in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 5
            assert all(r.exit_code == 0 for r in results)


class TestSandboxSecurity:
    """Test sandbox security features."""
    
    @pytest.fixture
    def secure_sandbox(self):
        """Create secure sandbox."""
        config = SandboxConfig(
            network_mode="none",
            readonly_paths=["/", "/etc", "/usr"],
            writable_paths=["/tmp", "/workspace"]
        )
        policy = SecurityPolicy(
            allow_network=False,
            allow_privileged=False,
            blocked_syscalls=["fork", "exec", "ptrace"]
        )
        return DockerSandbox(config, policy)
    
    @pytest.mark.asyncio
    async def test_prevent_privilege_escalation(self, secure_sandbox):
        """Test prevention of privilege escalation."""
        with patch('docker.from_env') as mock_docker:
            mock_client = Mock()
            mock_docker.return_value = mock_client
            
            await secure_sandbox.execute("sudo apt-get update", timeout=10)
            
            # Verify container runs without privileges
            call_kwargs = mock_client.containers.run.call_args[1]
            assert call_kwargs.get('privileged') is False
            assert call_kwargs.get('user') != 'root'
    
    @pytest.mark.asyncio
    async def test_prevent_dangerous_commands(self, secure_sandbox):
        """Test blocking of dangerous commands."""
        dangerous_commands = [
            "rm -rf /",
            ":(){ :|:& };:",  # Fork bomb
            "dd if=/dev/zero of=/dev/sda",
            "> /etc/passwd"
        ]
        
        for cmd in dangerous_commands:
            result = await secure_sandbox.validate_command(cmd)
            assert result is False, f"Dangerous command not blocked: {cmd}"
    
    @pytest.mark.asyncio
    async def test_syscall_filtering(self, secure_sandbox):
        """Test syscall filtering."""
        with patch('docker.from_env') as mock_docker:
            mock_client = Mock()
            mock_docker.return_value = mock_client
            
            await secure_sandbox.execute("ls /", timeout=10)
            
            # Verify seccomp profile is applied
            call_kwargs = mock_client.containers.run.call_args[1]
            assert 'security_opt' in call_kwargs
            assert any('seccomp' in opt for opt in call_kwargs['security_opt'])