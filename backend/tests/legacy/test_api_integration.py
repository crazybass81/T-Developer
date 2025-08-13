#!/usr/bin/env python3
"""
API 통합 테스트
"""

import asyncio
from src.orchestration.production_pipeline import ProductionECSPipeline

async def test_pipeline():
    print("Testing Pipeline with Todo Request...")
    
    pipeline = ProductionECSPipeline()
    await pipeline.initialize()
    
    # Todo 앱 요청
    result = await pipeline.execute(
        user_input="Create a Todo App with tasks and priorities",
        project_name="Test Todo App",
        project_type="react",
        features=["todo", "priority", "filter"]
    )
    
    print(f"\nResult: {result.success}")
    if result.success:
        print(f"Project ID: {result.project_id}")
        print(f"Metadata keys: {list(result.metadata.keys())}")
        
        # pipeline_data 확인
        if 'pipeline_data' in result.metadata:
            pd = result.metadata['pipeline_data']
            print(f"\nPipeline Data Keys: {list(pd.keys())}")
            
            # generation 결과 확인
            if 'generation' in pd:
                gen = pd['generation']
                print(f"\nGeneration Keys: {list(gen.keys())}")
                if 'is_todo_app' in gen:
                    print(f"Is Todo App: {gen['is_todo_app']}")
                if 'agents_created' in gen:
                    print(f"Agents Created: {gen['agents_created']}")
                if 'agent_names' in gen:
                    print(f"Agent Names: {gen['agent_names']}")
    else:
        print(f"Errors: {result.errors}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())