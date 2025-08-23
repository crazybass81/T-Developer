"""실제 파일 개선 테스트 - T-Developer-TEST의 파일을 직접 수정"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


async def add_docstring_to_file():
    """간단한 docstring 추가"""
    
    print("🚀 Adding docstrings to actual file")
    
    # 대상 파일
    target_file = Path("/home/ec2-user/T-Developer-TEST/backend/packages/agents/base.py")
    
    if not target_file.exists():
        print(f"❌ File not found: {target_file}")
        return False
    
    # 파일 읽기
    with open(target_file, 'r') as f:
        lines = f.readlines()
    
    # 첫 번째 함수 찾아서 docstring 추가
    modified = False
    new_lines = []
    in_class = False
    method_indent = ""
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # 클래스 찾기
        if line.strip().startswith("class BaseAgent"):
            in_class = True
            print(f"Found class at line {i+1}")
        
        # __init__ 메서드 찾기
        if in_class and "def __init__" in line and not modified:
            method_indent = line[:len(line) - len(line.lstrip())]
            
            # 다음 줄 확인 (이미 docstring이 있는지)
            if i+1 < len(lines) and '"""' not in lines[i+1]:
                # docstring 추가
                docstring = f'{method_indent}    """Initialize BaseAgent.\n'
                docstring += f'{method_indent}    \n'
                docstring += f'{method_indent}    Auto-generated docstring by T-Developer Evolution.\n'
                docstring += f'{method_indent}    \n'
                docstring += f'{method_indent}    Args:\n'
                docstring += f'{method_indent}        name: Agent name\n'
                docstring += f'{method_indent}        role: Agent role\n'
                docstring += f'{method_indent}        capabilities: List of capabilities\n'
                docstring += f'{method_indent}        memory_hub: Memory hub instance\n'
                docstring += f'{method_indent}    """\n'
                
                new_lines.append(docstring)
                modified = True
                print(f"✅ Added docstring after line {i+1}")
                break
    
    if modified:
        # 파일 쓰기
        with open(target_file, 'w') as f:
            f.writelines(new_lines)
        
        print(f"✅ File modified: {target_file}")
        print(f"📝 Added docstring to __init__ method")
        
        # 변경 내용 미리보기
        print("\n--- Preview of changes ---")
        for i, line in enumerate(new_lines[70:85], start=71):
            print(f"{i:3}: {line.rstrip()}")
        
        return True
    else:
        print("ℹ️ No modifications needed (docstring might already exist)")
        return False


async def add_type_hints():
    """타입 힌트 추가"""
    
    print("\n🔧 Adding type hints to methods")
    
    target_file = Path("/home/ec2-user/T-Developer-TEST/backend/packages/agents/base.py")
    
    with open(target_file, 'r') as f:
        content = f.read()
    
    # 간단한 타입 힌트 추가 (execute 메서드)
    old_signature = "async def execute(self, inputs):"
    new_signature = "async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:"
    
    if old_signature in content:
        content = content.replace(old_signature, new_signature)
        
        # Dict, Any import 추가
        if "from typing import" not in content:
            content = "from typing import Dict, Any, List, Optional\n" + content
        
        with open(target_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Added type hints to execute method")
        return True
    else:
        print("ℹ️ Type hints might already exist")
        return False


async def main():
    """메인 실행"""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║           T-Developer Code Evolution - Direct Test           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 1. Docstring 추가
    result1 = await add_docstring_to_file()
    
    # 2. Type hints 추가
    result2 = await add_type_hints()
    
    if result1 or result2:
        print("\n✨ Code improvements applied successfully!")
        print("Check /home/ec2-user/T-Developer-TEST/backend/packages/agents/base.py")
    else:
        print("\n📝 No changes were needed.")


if __name__ == "__main__":
    asyncio.run(main())