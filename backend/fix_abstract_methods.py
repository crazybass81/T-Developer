#!/usr/bin/env python3
"""
Fix abstract methods in unified agents
"""

import os
import re
from pathlib import Path

# Agents that need fixing
agents_to_fix = [
    'component_decision',
    'match_rate', 
    'search',
    'generation',
    'assembly'
]

# Method implementations to add
methods_to_add = '''
    async def _custom_initialize(self):
        """Custom initialization"""
        pass
    
    async def _process_internal(self, input_data, context):
        """Internal processing method - delegates to main process"""
        result = await self.process(input_data)
        return result.data if hasattr(result, 'data') else result
'''

def fix_agent(agent_name):
    """Fix abstract methods in agent file"""
    agent_path = Path(f'/home/ec2-user/T-DeveloperMVP/backend/src/agents/unified/{agent_name}/agent.py')
    
    if not agent_path.exists():
        print(f"❌ Agent file not found: {agent_path}")
        return False
    
    with open(agent_path, 'r') as f:
        content = f.read()
    
    # Check if methods already exist
    if '_custom_initialize' in content and '_process_internal' in content:
        print(f"✅ {agent_name}: Methods already exist")
        return True
    
    # Find the class definition
    class_patterns = [
        rf'class \w*{agent_name.replace("_", "").title()}Agent\([^)]+\):',
        rf'class {agent_name.replace("_", "").title()}Agent\([^)]+\):',
        rf'class \w+Agent\([^)]+\):'
    ]
    
    for pattern in class_patterns:
        match = re.search(pattern, content)
        if match:
            break
    
    if not match:
        print(f"❌ {agent_name}: Could not find class definition")
        return False
    
    # Find the __init__ method
    init_match = re.search(r'(\s+)def __init__\(self[^)]*\):', content[match.end():])
    if not init_match:
        print(f"❌ {agent_name}: Could not find __init__ method")
        return False
    
    # Insert methods right after class definition, before __init__
    indent = '    '  # Standard 4-space indent for class methods
    insertion_point = match.end()
    
    # Add docstring if not present
    docstring_check = content[match.end():match.end()+100]
    if '"""' in docstring_check:
        # Find end of docstring
        docstring_end = content.find('"""', match.end() + docstring_check.index('"""') + 3)
        insertion_point = docstring_end + 3
    
    # Add newline and methods
    new_content = (
        content[:insertion_point] + 
        '\n' + methods_to_add + '\n' +
        content[insertion_point:]
    )
    
    # Write back
    with open(agent_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ {agent_name}: Methods added successfully")
    return True

def main():
    print("Fixing abstract methods in unified agents...")
    
    success_count = 0
    for agent in agents_to_fix:
        if fix_agent(agent):
            success_count += 1
    
    print(f"\n✅ Fixed {success_count}/{len(agents_to_fix)} agents")

if __name__ == '__main__':
    main()