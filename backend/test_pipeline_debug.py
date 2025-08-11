#!/usr/bin/env python3
"""
Debug script to check actual agent execution flow
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration.production_pipeline import ProductionECSPipeline

async def debug_pipeline():
    """Debug the pipeline execution with detailed logging"""
    
    # Initialize pipeline
    pipeline = ProductionECSPipeline()
    await pipeline.initialize()
    
    print("=" * 60)
    print("🔍 DEBUGGING AGENT PIPELINE")
    print("=" * 60)
    
    # Check loaded agents
    print(f"\n✅ Pipeline initialized")
    print(f"✅ Agents loaded: {len(pipeline.agents)}")
    
    # Very simple test input
    test_input = {
        'name': 'Debug App',
        'description': 'Debug test',
        'framework': 'react',
        'features': ['test'],
        'requirements': ['simple']
    }
    
    print(f"\n📤 Test Input: {json.dumps(test_input, indent=2)}")
    
    # Execute and catch any errors
    try:
        print("\n🚀 Starting pipeline execution...")
        result = await pipeline.execute(test_input, {})
        
        print("\n✅ Pipeline executed without exception")
        print(f"Result type: {type(result)}")
        print(f"Result success: {result.success}")
        print(f"Result project_id: {result.project_id}")
        
        # Check metadata for agent execution info
        if result.metadata:
            agents_executed = result.metadata.get('agents_executed', [])
            print(f"\n📊 Agents executed: {len(agents_executed)}")
            for i, agent in enumerate(agents_executed, 1):
                print(f"  {i}. {agent}")
        
        # Check for errors
        if result.errors:
            print(f"\n⚠️ Errors found: {len(result.errors)}")
            for error in result.errors:
                print(f"  - {error}")
        
        # Check final output
        if result.project_path:
            print(f"\n✅ Project created at: {result.project_path}")
        
        return result.success
        
    except Exception as e:
        print(f"\n❌ Pipeline failed with exception: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_pipeline())
    print(f"\n{'✅' if success else '❌'} Pipeline execution: {'SUCCESS' if success else 'FAILED'}")