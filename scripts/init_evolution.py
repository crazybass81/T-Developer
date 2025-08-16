#!/usr/bin/env python3
"""Initialize the T-Developer self-evolution system."""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

def check_environment() -> Dict[str, bool]:
    """Check if all required environment variables and tools are configured."""
    checks = {
        "aws_configured": bool(os.environ.get("AWS_REGION")),
        "claude_api_key": bool(os.environ.get("CLAUDE_API_KEY")),
        "mcp_enabled": os.environ.get("MCP_FILESYSTEM_ENABLED") == "true",
        "evolution_mode": os.environ.get("EVOLUTION_MODE") == "enabled",
    }
    return checks

def setup_mcp_servers() -> None:
    """Initialize MCP server configurations."""
    mcp_dir = Path("packages/mcp/servers")
    mcp_dir.mkdir(parents=True, exist_ok=True)
    
    # Filesystem MCP server config
    fs_config = {
        "name": "filesystem",
        "command": "mcp-server-filesystem",
        "args": ["--workspace", str(Path.cwd())],
        "env": {"MCP_WRITE_SCOPE": "packages/**,tests/**"}
    }
    
    # Git MCP server config
    git_config = {
        "name": "git",
        "command": "mcp-server-git",
        "args": ["--repo", str(Path.cwd())]
    }
    
    # GitHub MCP server config
    github_config = {
        "name": "github",
        "command": "mcp-server-github",
        "args": [],
        "env": {"GITHUB_TOKEN": os.environ.get("MCP_GITHUB_TOKEN", "")}
    }
    
    # Write configurations
    for name, config in [("filesystem", fs_config), ("git", git_config), ("github", github_config)]:
        config_path = mcp_dir / f"{name}.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print(f"✓ Created MCP server config: {config_path}")

def initialize_agents() -> None:
    """Create skeleton files for core agents."""
    agents_dir = Path("packages/agents")
    agents_dir.mkdir(parents=True, exist_ok=True)
    
    # Base agent template
    base_agent = '''"""Base agent interface for T-Developer agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAgent(ABC):
    """Base class for all T-Developer agents."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary task."""
        pass
    
    @abstractmethod
    async def validate(self, result: Dict[str, Any]) -> bool:
        """Validate the agent's output."""
        pass
'''
    
    with open(agents_dir / "base.py", "w") as f:
        f.write(base_agent)
    print("✓ Created base agent interface")
    
    # Create skeleton agents
    agents = ["research_agent", "planner_agent", "refactor_agent", "evaluator_agent"]
    for agent in agents:
        agent_file = agents_dir / f"{agent}.py"
        with open(agent_file, "w") as f:
            f.write(f'''"""Implementation of {agent.replace('_', ' ').title()}."""

from .base import BaseAgent
from typing import Dict, Any

class {agent.replace('_', ' ').title().replace(' ', '')}(BaseAgent):
    """Agent responsible for {agent.replace('_', ' ')} tasks."""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute {agent.replace('_', ' ')} task."""
        # TODO: Implement agent logic
        return {{"status": "pending", "agent": self.name}}
    
    async def validate(self, result: Dict[str, Any]) -> bool:
        """Validate {agent.replace('_', ' ')} output."""
        return result.get("status") == "success"
''')
        print(f"✓ Created {agent}")

def main():
    """Main initialization routine."""
    print("🚀 Initializing T-Developer Self-Evolution System\n")
    
    # Check environment
    print("Checking environment...")
    checks = check_environment()
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
    
    if not all(checks.values()):
        print("\n⚠️  Some checks failed. Please configure your environment.")
        print("   Copy .env.example to .env and fill in the values.")
        sys.exit(1)
    
    print("\nSetting up components...")
    
    # Setup MCP servers
    setup_mcp_servers()
    
    # Initialize agents
    initialize_agents()
    
    print("\n✅ T-Developer initialization complete!")
    print("   Run 'python scripts/run_evolution.py' to start self-evolution.")

if __name__ == "__main__":
    main()