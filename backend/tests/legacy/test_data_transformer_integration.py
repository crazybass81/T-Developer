#!/usr/bin/env python3
"""
Data Transformer와 파이프라인 통합 테스트
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

async def test():
    print("=" * 50)
    print("Data Transformer Integration Test")
    print("=" * 50)
    
    # 1. Data Transformer import 테스트
    try:
        from src.agents.data_transformer.agent import data_transformer
        print("✅ Data Transformer imported successfully")
    except ImportError as e:
        print(f"❌ Data Transformer import failed: {e}")
        return
    
    # 2. Pipeline import 테스트 
    try:
        from src.orchestration.production_pipeline import ProductionECSPipeline
        print("✅ Pipeline imported successfully")
    except ImportError as e:
        print(f"❌ Pipeline import failed: {e}")
        return
    
    # 3. 실제 에이전트와 Data Transformer 통합 테스트
    print("\n--- Testing Data Transformer with Real Agents ---")
    
    # Test data
    test_data = {
        'data': {
            'name': 'Todo App',
            'description': 'A todo application', 
            'framework': 'react',
            'features': ['todo', 'priority']
        },
        'context': {
            'pipeline_id': 'test_123'
        }
    }
    
    # Component Decision Agent 테스트
    try:
        from src.agents.unified.component_decision.agent import ComponentDecisionAgent
        agent = ComponentDecisionAgent()
        
        # 변환 없이 직접 실행 (실패 예상)
        print("\n1. Direct execution (should fail):")
        try:
            result = await agent.process(test_data)
            print(f"   Unexpected success: {result}")
        except AttributeError as e:
            print(f"   Expected failure: {e}")
            
            # Data Transformer로 수정
            print("\n2. With Data Transformer auto-fix:")
            fixed_data = await data_transformer.auto_fix(e, test_data, 'component_decision')
            if fixed_data:
                print(f"   ✅ Data fixed! Has name attr: {hasattr(fixed_data, 'name')}")
                try:
                    result = await agent.process(fixed_data)
                    print(f"   ✅ Agent executed successfully!")
                except Exception as e2:
                    print(f"   ❌ Still failed: {e2}")
            else:
                print("   ❌ Auto-fix failed")
                
    except ImportError as e:
        print(f"ComponentDecisionAgent import failed: {e}")
    
    # 4. 전체 파이프라인 테스트
    print("\n--- Testing Full Pipeline with Data Transformer ---")
    
    pipeline = ProductionECSPipeline()
    await pipeline.initialize()
    
    result = await pipeline.execute(
        user_input="Create a Todo App with tasks and priorities",
        project_name="Test Todo App",
        project_type="react",
        features=["todo", "priority", "filter"]
    )
    
    print(f"\n✅ Pipeline completed: {result.success}")
    print(f"   Project ID: {result.project_id}")
    print(f"   Errors: {len(result.errors)}")
    if result.errors:
        for err in result.errors[:3]:  # 처음 3개 에러만
            print(f"   - {err[:100]}")

if __name__ == "__main__":
    asyncio.run(test())