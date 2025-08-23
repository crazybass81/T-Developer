"""간단한 진화 테스트 - docstring 추가만"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator,
    UpgradeConfig
)


async def simple_evolution():
    """간단한 진화 실행 - docstring 추가"""
    
    print("🚀 Starting Simple Evolution Test...")
    
    config = UpgradeConfig(
        project_path="/home/ec2-user/T-Developer-TEST",
        output_dir="/tmp/t-developer/simple_evolution",
        safe_mode=True,
        max_execution_time=300,  # 5분
        parallel_analysis=False,
        
        # Evolution 설정
        enable_evolution_loop=False,  # 단일 실행
        auto_generate_agents=False,
        auto_implement_code=True,  # 코드 생성만 활성화
    )
    
    # 매우 간단한 요구사항
    requirements = """
    Add missing docstrings to the following file:
    /home/ec2-user/T-Developer-TEST/backend/packages/agents/base.py
    
    Specifically:
    1. Add a docstring to the __init__ method if missing
    2. Add a docstring to the execute method if missing
    3. Follow Google style docstring format
    """
    
    try:
        orchestrator = UpgradeOrchestrator(config)
        await orchestrator.initialize()
        
        # CodeGenerator 직접 호출
        code_generator = orchestrator.agents.get("CodeGenerator")
        if code_generator:
            print("📝 Generating improved code with docstrings...")
            
            # base.py 파일 읽기
            base_path = Path("/home/ec2-user/T-Developer-TEST/backend/packages/agents/base.py")
            if base_path.exists():
                with open(base_path, 'r') as f:
                    original_code = f.read()
                
                # 개선된 코드 생성
                result = await code_generator.execute({
                    "task": "Add comprehensive docstrings",
                    "code": original_code[:1000],  # 처음 1000자만
                    "requirements": requirements
                })
                
                if result and "generated_code" in result:
                    print("✅ Code generated successfully!")
                    
                    # 생성된 코드 일부 출력
                    generated = result["generated_code"]
                    print("\n--- Generated Code Preview ---")
                    print(generated[:500])
                    print("...")
                    
                    # 파일에 쓰기 (테스트용)
                    test_file = Path("/tmp/t-developer/simple_evolution/improved_base.py")
                    test_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(test_file, 'w') as f:
                        f.write(generated)
                    print(f"\n💾 Saved to: {test_file}")
                    
                    return True
        
        print("❌ Code generation failed")
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(simple_evolution())
    if result:
        print("\n✨ Evolution test completed successfully!")
    else:
        print("\n⚠️ Evolution test failed")