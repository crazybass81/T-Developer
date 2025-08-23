#!/usr/bin/env python3
"""Update all agent constructors to accept document_context parameter"""

import os
import re
from pathlib import Path

# Agent files to update
agent_files = [
    "external_researcher.py",
    "gap_analyzer.py",
    "system_architect.py",
    "orchestrator_designer.py",
    "planner_agent.py",
    "task_creator_agent.py",
    "code_generator.py",
    "quality_gate.py",
    "static_analyzer.py",
    "code_analysis_agent.py",
    "behavior_analyzer.py",
    "impact_analyzer.py"
]

agents_dir = Path("/home/ec2-user/T-Developer/backend/packages/agents")

def update_agent_init(file_path):
    """Update agent __init__ method to accept document_context"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match __init__ method
    pattern = r'(def __init__\(self[^)]*)(memory_hub[^)]*)\):'
    
    # Check if document_context already exists
    if 'document_context' in content:
        print(f"  ⏭️ {file_path.name} already has document_context")
        return False
    
    # Find the __init__ method
    match = re.search(pattern, content)
    if not match:
        print(f"  ⚠️ Could not find __init__ pattern in {file_path.name}")
        return False
    
    # Add document_context parameter
    new_init = match.group(0).replace('):', ', document_context=None):')
    content = content.replace(match.group(0), new_init)
    
    # Find super().__init__ call and add document_context
    super_pattern = r'(super\(\).__init__\([^)]*)(memory_hub=[^)]*)\)'
    super_match = re.search(super_pattern, content)
    
    if super_match:
        # Add document_context to super().__init__
        old_super = super_match.group(0)
        new_super = old_super.replace(')', ',\n            document_context=document_context\n        )')
        content = content.replace(old_super, new_super)
    
    # Update docstring
    docstring_pattern = r'("""[^"]*Args:[^"]*memory_hub[^"]*)(""")'
    docstring_match = re.search(docstring_pattern, content, re.DOTALL)
    
    if docstring_match:
        old_docstring = docstring_match.group(0)
        new_docstring = old_docstring.replace('"""', '\n            document_context: SharedDocumentContext 인스턴스\n        """')
        content = content.replace(old_docstring, new_docstring)
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"  ✅ Updated {file_path.name}")
    return True

def main():
    print("Updating agent constructors to accept document_context...")
    print("=" * 60)
    
    updated_count = 0
    for agent_file in agent_files:
        file_path = agents_dir / agent_file
        if file_path.exists():
            if update_agent_init(file_path):
                updated_count += 1
        else:
            print(f"  ❌ {agent_file} not found")
    
    print("=" * 60)
    print(f"✅ Updated {updated_count} agents")

if __name__ == "__main__":
    main()