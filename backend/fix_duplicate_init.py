#!/usr/bin/env python3
"""
Fix duplicate __init__ methods in Enhanced*Result classes
"""
import re
from pathlib import Path

def fix_enhanced_result_classes():
    """Fix duplicate __init__ methods in all Enhanced*Result classes"""
    
    files = [
        "/home/ec2-user/T-DeveloperMVP/backend/src/agents/unified/assembly/agent.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/agents/unified/generation/agent.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/agents/unified/match_rate/agent.py",
        "/home/ec2-user/T-DeveloperMVP/backend/src/agents/unified/search/agent.py"
    ]
    
    for file_path in files:
        file = Path(file_path)
        if not file.exists():
            continue
            
        print(f"Processing {file.name}...")
        
        with open(file, 'r') as f:
            content = f.read()
        
        # Pattern to find the duplicate __init__ structure
        pattern = r'(class Enhanced\w+Result:)\s+(def __init__.*?)\s+(""".*?""")\s+(def __init__.*?)(?=\n\s+def |\n\nclass |\Z)'
        
        def replace_duplicate_init(match):
            class_def = match.group(1)
            first_init = match.group(2)
            docstring = match.group(3)
            second_init = match.group(4)
            
            # Merge both __init__ contents
            # Extract body of second init (has super() call and more attributes)
            second_body = re.findall(r'def __init__.*?:\n((?:\s+.*\n)+)', second_init, re.DOTALL)
            
            if second_body:
                merged_body = second_body[0]
                # Remove super().__init__ line since we don't have parent
                merged_body = re.sub(r'\s+super\(\).__init__\([^)]*\)\n', '', merged_body)
                
                # Add data and success from first init at the beginning
                merged_init = f"""    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.success = data.get("success", False)
{merged_body}"""
            else:
                merged_init = first_init
            
            return f"{class_def}\n    {docstring}\n    \n{merged_init}"
        
        # Apply the fix
        fixed_content = re.sub(pattern, replace_duplicate_init, content, flags=re.DOTALL)
        
        # Write back
        with open(file, 'w') as f:
            f.write(fixed_content)
        
        print(f"  ✅ Fixed {file.name}")

if __name__ == "__main__":
    fix_enhanced_result_classes()
    print("\n✅ All duplicate __init__ methods fixed!")