#!/usr/bin/env python3
"""
Fix all import paths to use absolute imports
"""
import os
from pathlib import Path

def fix_all_imports():
    """Fix all import paths to absolute imports"""
    
    agents_dir = Path("/home/ec2-user/T-DeveloperMVP/backend/src/agents/unified")
    
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
                lines = f.readlines()
            
            # Fix imports line by line
            new_lines = []
            changed = False
            
            for line in lines:
                original_line = line
                
                # Fix relative base imports
                if "from ..base import" in line:
                    line = line.replace("from ..base import", "from src.agents.unified.base import")
                    changed = True
                    print(f"  Fixed: relative base import")
                
                # Fix wrong base_agent imports  
                elif "from ..base.unified_base_agent import" in line:
                    line = line.replace("from ..base.unified_base_agent import", "from src.agents.unified.base import")
                    changed = True
                    print(f"  Fixed: base_agent import")
                    
                # Remove try/except blocks for imports
                elif line.strip() == "try:":
                    # Check if this is an import try block
                    next_idx = lines.index(original_line) + 1
                    if next_idx < len(lines) and "from ..base import" in lines[next_idx]:
                        continue  # Skip the try line
                elif line.strip() == "except ImportError:":
                    # Check if previous was an import
                    prev_idx = lines.index(original_line) - 1
                    if prev_idx >= 0 and "from src.agents.unified.base import" in new_lines[-1]:
                        continue  # Skip the except line
                elif line.strip().startswith("from src.agents.unified.base import") and lines[lines.index(original_line)-1].strip() == "except ImportError:":
                    continue  # Skip duplicate import after except
                    
                new_lines.append(line)
            
            # Write back if changed
            if changed:
                with open(agent_file, 'w') as f:
                    f.writelines(new_lines)
                print(f"  ✅ Updated {agent_name}/agent.py")
            else:
                print(f"  ⚠️ No changes needed for {agent_name}/agent.py")

if __name__ == "__main__":
    fix_all_imports()
    print("\n✅ Import fixes completed!")