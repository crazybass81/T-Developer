"""직접 코드 개선 테스트"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.agents.code_generator import CodeGenerator
from backend.packages.memory.hub import MemoryHub


async def improve_code():
    """직접 코드 개선"""
    
    print("🚀 Direct Code Improvement Test")
    
    # CodeGenerator 초기화
    hub = MemoryHub()
    generator = CodeGenerator(memory_hub=hub)
    
    # 개선할 코드 (간단한 예제)
    original_code = '''
class SimpleClass:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}"
    
    def calculate(self, x, y):
        return x + y
'''
    
    # 개선 요청 (CodeGenerator가 기대하는 형식)
    improvement_spec = {
        "requirements": {
            "task": "improve code quality",
            "description": "Add docstrings, type hints, and validation",
            "code": original_code,
            "improvements": [
                "Add comprehensive docstrings to all methods",
                "Add type hints",
                "Add input validation",
                "Follow Google docstring style"
            ]
        },
        "language": "python",
        "task_type": "refactor"
    }
    
    try:
        print("📝 Generating improved code...")
        result = await generator.execute(improvement_spec)
        
        if result and "generated_code" in result:
            improved_code = result["generated_code"]
            
            print("\n✅ Code improved successfully!")
            print("\n--- Original Code ---")
            print(original_code)
            print("\n--- Improved Code ---")
            print(improved_code)
            
            # 실제 파일에 적용 테스트
            test_file = Path("/home/ec2-user/T-Developer-TEST/backend/packages/test_improved.py")
            with open(test_file, 'w') as f:
                f.write(improved_code)
            
            print(f"\n💾 Saved improved code to: {test_file}")
            return True
        else:
            print(f"❌ Generation failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(improve_code())
    if result:
        print("\n✨ Code improvement successful! Check the file for changes.")
    else:
        print("\n⚠️ Code improvement failed")