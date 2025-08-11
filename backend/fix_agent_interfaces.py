#!/usr/bin/env python3
"""
Fix agent interfaces - add logging methods and data wrapper
"""

import os
from pathlib import Path

# All unified agents
agents = [
    'nl_input', 'ui_selection', 'parser', 'component_decision',
    'match_rate', 'search', 'generation', 'assembly', 'download'
]

# Logging methods to add
logging_methods = '''
    def log_info(self, message: str):
        """Log info message"""
        if hasattr(self, 'logger'):
            self.logger.info(message)
        else:
            print(f"INFO: {message}")
    
    def log_error(self, message: str):
        """Log error message"""
        if hasattr(self, 'logger'):
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")
    
    def log_warning(self, message: str):
        """Log warning message"""
        if hasattr(self, 'logger'):
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")
'''

# Import statement to add
wrapper_import = "from src.agents.unified.data_wrapper import AgentInput, AgentContext, wrap_input, unwrap_result\n"

def fix_agent(agent_name):
    """Fix agent interface issues"""
    agent_path = Path(f'/home/ec2-user/T-DeveloperMVP/backend/src/agents/unified/{agent_name}/agent.py')
    
    if not agent_path.exists():
        print(f"❌ {agent_name}: File not found")
        return False
    
    with open(agent_path, 'r') as f:
        content = f.read()
    
    modified = False
    
    # Add wrapper import if not present
    if 'data_wrapper' not in content:
        # Find the imports section
        import_lines = content.split('\n')
        for i, line in enumerate(import_lines):
            if line.startswith('from src.agents.unified.base import'):
                # Add wrapper import after base import
                import_lines.insert(i + 1, wrapper_import)
                content = '\n'.join(import_lines)
                modified = True
                print(f"  ✓ Added data_wrapper import")
                break
    
    # Add logging methods if not present
    if 'def log_info' not in content:
        # Find a good place to insert - after __init__ or after _custom_initialize
        lines = content.split('\n')
        insert_index = -1
        
        # Try to find __init__ method
        for i, line in enumerate(lines):
            if 'def __init__' in line:
                # Find the end of __init__
                indent_count = len(line) - len(line.lstrip())
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(' ' * (indent_count + 4)):
                        insert_index = j
                        break
                break
        
        if insert_index > 0:
            # Insert logging methods
            lines.insert(insert_index, logging_methods)
            content = '\n'.join(lines)
            modified = True
            print(f"  ✓ Added logging methods")
    
    # Fix process method to handle both dict and AgentInput
    if 'async def process(self' in content:
        # Add input wrapper at the beginning of process method
        process_fix = '''async def process(self, input_data: Any) -> Any:
        """Process input through the agent"""
        # Ensure input is wrapped properly
        if not isinstance(input_data, AgentInput):
            from src.agents.unified.data_wrapper import wrap_input
            input_data = wrap_input(input_data if isinstance(input_data, dict) else {'data': input_data})
'''
        
        # Only apply if not already fixed
        if 'wrap_input' not in content:
            content = content.replace('async def process(self, input_data:', process_fix)
            modified = True
            print(f"  ✓ Added input wrapper to process method")
    
    if modified:
        with open(agent_path, 'w') as f:
            f.write(content)
        print(f"✅ {agent_name}: Fixed successfully")
        return True
    else:
        print(f"✓ {agent_name}: Already fixed")
        return True

def main():
    print("Fixing agent interfaces...")
    print("-" * 40)
    
    success_count = 0
    for agent in agents:
        if fix_agent(agent):
            success_count += 1
    
    print("-" * 40)
    print(f"✅ Fixed {success_count}/{len(agents)} agents")

if __name__ == '__main__':
    main()