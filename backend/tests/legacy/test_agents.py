#!/usr/bin/env python3
"""
Test script to verify agent pipeline execution
"""
import asyncio
import json
from src.orchestration.production_pipeline import ProductionECSPipeline

async def test_pipeline():
    """Test the complete agent pipeline"""
    
    # Initialize pipeline
    pipeline = ProductionECSPipeline()
    await pipeline.initialize()
    
    print("=" * 60)
    print("🔍 AGENT PIPELINE STATUS CHECK")
    print("=" * 60)
    
    # Check loaded agents (use correct attribute name)
    agents_attr = 'agents' if hasattr(pipeline, 'agents') else 'agent_instances'
    agents = getattr(pipeline, agents_attr, {})
    
    print(f"\n✅ Loaded {len(agents)} agents:")
    for name, agent in agents.items():
        print(f"  [{name}]: {type(agent).__name__}")
    
    # Test input
    test_input = {
        'name': 'Test Todo App',
        'description': 'A simple todo application for testing',
        'framework': 'react',
        'features': ['Add tasks', 'Delete tasks', 'Mark complete'],
        'requirements': ['User-friendly', 'Responsive']
    }
    
    print("\n" + "=" * 60)
    print("🧪 TESTING AGENT EXECUTION FLOW")
    print("=" * 60)
    
    # Track agent execution using proper method override
    executed_agents = []
    
    # Check which execute method exists
    if hasattr(pipeline, '_execute_agent_with_retry'):
        original_execute = pipeline._execute_agent_with_retry
        
        async def tracked_execute(agent_name, agent, input_data, context):
            print(f"\n➡️  Executing: {agent_name}")
            print(f"   Input type: {type(input_data).__name__}")
            print(f"   Input keys: {list(input_data.keys()) if isinstance(input_data, dict) else 'N/A'}")
            
            result = await original_execute(agent_name, agent, input_data, context)
            
            executed_agents.append(agent_name)
            print(f"   ✅ {agent_name} completed")
            print(f"   Output type: {type(result).__name__}")
            if isinstance(result, dict):
                print(f"   Output keys: {list(result.keys())[:5]}...")
            
            return result
        
        pipeline._execute_agent_with_retry = tracked_execute
    elif hasattr(pipeline, '_execute_real_agent'):
        original_execute = pipeline._execute_real_agent
        
        async def tracked_execute(agent_name, agent, input_data, context):
            print(f"\n➡️  Executing: {agent_name}")
            print(f"   Input type: {type(input_data).__name__}")
            print(f"   Input keys: {list(input_data.keys()) if isinstance(input_data, dict) else 'N/A'}")
            
            result = await original_execute(agent_name, agent, input_data, context)
            
            executed_agents.append(agent_name)
            print(f"   ✅ {agent_name} completed")
            print(f"   Output type: {type(result).__name__}")
            if isinstance(result, dict):
                print(f"   Output keys: {list(result.keys())[:5]}...")
            
            return result
        
        pipeline._execute_real_agent = tracked_execute
    else:
        print("⚠️  Warning: Could not hook into agent execution method")
    
    # Execute pipeline
    try:
        print(f"\n📤 Input: {json.dumps(test_input, indent=2)}")
        
        result = await pipeline.execute(test_input, {})
        
        print("\n" + "=" * 60)
        print("📊 EXECUTION RESULTS")
        print("=" * 60)
        
        print(f"\n✅ Pipeline Success: {result.success}")
        print(f"✅ Agents Executed: {len(executed_agents)}/{len(agents)}")
        print(f"✅ Execution Order: {' → '.join(executed_agents)}")
        
        # Use correct ProductionPipelineResult attributes
        if result.project_id:
            print(f"\n📦 Output Data:")
            print(f"  - Project ID: {result.project_id}")
            print(f"  - Project Path: {result.project_path}")
            print(f"  - Execution Time: {result.execution_time:.2f}s")
        
        if result.metadata:
            print(f"\n📊 Metadata:")
            print(f"  - Download URL: {result.metadata.get('download_url', 'N/A')}")
            print(f"  - Files Generated: {result.metadata.get('total_files', 0)}")
            print(f"  - Agents Executed: {result.metadata.get('agents_executed', [])}")
        
        if result.errors:
            print(f"\n⚠️  Errors: {result.errors}")
        
    except Exception as e:
        print(f"\n❌ Pipeline execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
    
    return len(executed_agents) == 9

if __name__ == "__main__":
    success = asyncio.run(test_pipeline())
    print(f"\n{'✅' if success else '❌'} All 9 agents executed: {success}")