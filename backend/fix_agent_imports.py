#!/usr/bin/env python3
"""
Fix all import paths in unified agents
"""
import os
from pathlib import Path

def fix_agent_imports():
    """Fix import paths in all agent files"""
    
    agents_dir = Path("/home/ec2-user/T-DeveloperMVP/backend/src/agents/unified")
    
    # Import fixes to apply
    fixes = [
        # Fix base imports - wrong path
        ("from agents.unified.base_agent import UnifiedBaseAgent", 
         "from ..base import UnifiedBaseAgent, AgentConfig, AgentContext, AgentResult"),
        
        # Fix absolute imports that should be relative
        ("from src.agents.unified.base import", 
         "from ..base import"),
         
        # Fix wrong base_agent references
        ("from agents.unified.base_agent", 
         "from ..base.unified_base_agent"),
    ]
    
    # Process each agent directory
    agent_dirs = [
        "nl_input", "ui_selection", "parser", "component_decision",
        "match_rate", "search", "generation", "assembly", "download"
    ]
    
    for agent_name in agent_dirs:
        agent_file = agents_dir / agent_name / "agent.py"
        if agent_file.exists():
            print(f"Processing {agent_name}/agent.py...")
            
            # Read the file
            with open(agent_file, 'r') as f:
                content = f.read()
            
            # Apply fixes
            original_content = content
            for old_import, new_import in fixes:
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    print(f"  Fixed: {old_import}")
            
            # Write back if changed
            if content != original_content:
                with open(agent_file, 'w') as f:
                    f.write(content)
                print(f"  ✅ Updated {agent_name}/agent.py")
            else:
                print(f"  ⚠️ No changes needed for {agent_name}/agent.py")

if __name__ == "__main__":
    fix_agent_imports()
    print("\n✅ Import fixes completed!")