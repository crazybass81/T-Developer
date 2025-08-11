#!/usr/bin/env python3
"""
Fix all relative module imports to absolute imports in all agents
"""
import os
import re
from pathlib import Path

def fix_module_imports():
    """Fix all relative imports to absolute imports"""
    
    agents_dir = Path("/home/ec2-user/T-DeveloperMVP/backend/src/agents/unified")
    
    # Process each agent directory
    agent_dirs = [
        "nl_input", "ui_selection", "parser", "component_decision",
        "match_rate", "search", "generation", "assembly", "download"
    ]
    
    for agent_name in agent_dirs:
        agent_file = agents_dir / agent_name / "agent.py"
        if not agent_file.exists():
            continue
            
        print(f"Processing {agent_name}/agent.py...")
        
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Store original for comparison
        original_content = content
        
        # Fix relative imports from .modules
        # Pattern: from .modules.xxx import YYY
        pattern = r'from \.modules\.(\w+) import'
        replacement = f'from src.agents.unified.{agent_name}.modules.\\1 import'
        content = re.sub(pattern, replacement, content)
        
        # Fix: from .modules import (...)
        pattern = r'from \.modules import'
        replacement = f'from src.agents.unified.{agent_name}.modules import'
        content = re.sub(pattern, replacement, content)
        
        # Also check for multi-line imports
        # Pattern: from .modules import (\n    xxx,\n    yyy\n)
        pattern = r'from \.modules import \(([\s\S]*?)\)'
        
        def fix_multiline_import(match):
            imports = match.group(1)
            return f'from src.agents.unified.{agent_name}.modules import ({imports})'
        
        content = re.sub(pattern, fix_multiline_import, content)
        
        # Write back if changed
        if content != original_content:
            with open(agent_file, 'w') as f:
                f.write(content)
            print(f"  ✅ Fixed module imports in {agent_name}/agent.py")
        else:
            print(f"  ⚠️ No changes needed for {agent_name}/agent.py")

if __name__ == "__main__":
    fix_module_imports()
    print("\n✅ All module imports fixed!")