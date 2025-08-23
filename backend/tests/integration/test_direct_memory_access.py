#!/usr/bin/env python3
"""Direct memory access demonstration for T-Developer v2."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


async def test_direct_memory_access():
    """Test direct memory access operations."""
    
    print("=" * 80)
    print("TESTING DIRECT MEMORY ACCESS")
    print("=" * 80)
    
    # Initialize memory hub
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    try:
        # 1. Direct Write to Memory
        print("\n1. Writing data directly to memory...")
        
        test_data = {
            "requirement": "Build a REST API",
            "components": ["auth", "database", "api"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Write to shared context
        success = await memory_hub.put(
            context_type=ContextType.S_CTX,
            key="test:requirement",
            value=test_data,
            ttl_seconds=3600,
            tags=["test", "requirement", "api"]
        )
        print(f"   ✅ Write to S_CTX: {success}")
        
        # Write to agent context
        agent_data = {
            "agent": "RequirementAnalyzer",
            "analysis": "Complex requirement needing 5 components",
            "confidence": 0.95
        }
        
        success = await memory_hub.put(
            context_type=ContextType.A_CTX,
            key="RequirementAnalyzer:analysis:001",
            value=agent_data,
            tags=["RequirementAnalyzer", "analysis"]
        )
        print(f"   ✅ Write to A_CTX: {success}")
        
        # 2. Direct Read from Memory
        print("\n2. Reading data directly from memory...")
        
        # Read from shared context
        retrieved_data = await memory_hub.get(
            context_type=ContextType.S_CTX,
            key="test:requirement"
        )
        print(f"   ✅ Read from S_CTX: {retrieved_data['requirement']}")
        
        # Read from agent context
        agent_retrieved = await memory_hub.get(
            context_type=ContextType.A_CTX,
            key="RequirementAnalyzer:analysis:001"
        )
        print(f"   ✅ Read from A_CTX: Agent={agent_retrieved['agent']}, Confidence={agent_retrieved['confidence']}")
        
        # 3. Search by Tags
        print("\n3. Searching memory by tags...")
        
        # Search for all requirement-related entries
        search_results = await memory_hub.search(
            context_type=ContextType.S_CTX,
            tags=["requirement"],
            limit=10
        )
        print(f"   ✅ Found {len(search_results)} entries with 'requirement' tag")
        
        # Search in agent context
        agent_results = await memory_hub.search(
            context_type=ContextType.A_CTX,
            tags=["RequirementAnalyzer"],
            limit=10
        )
        print(f"   ✅ Found {len(agent_results)} entries for RequirementAnalyzer")
        
        # 4. Cross-Context Access
        print("\n4. Cross-context memory operations...")
        
        # Write orchestrator data
        orchestrator_data = {
            "plan": "Execute in 3 phases",
            "tasks": ["analyze", "implement", "test"],
            "priority": "high"
        }
        
        await memory_hub.put(
            context_type=ContextType.O_CTX,
            key="execution_plan:latest",
            value=orchestrator_data,
            tags=["plan", "orchestrator"]
        )
        print("   ✅ Wrote to O_CTX (Orchestrator context)")
        
        # Write user data
        user_data = {
            "user": "developer1",
            "preferences": ["python", "fastapi"],
            "history": ["created API", "reviewed code"]
        }
        
        await memory_hub.put(
            context_type=ContextType.U_CTX,
            key="user:developer1",
            value=user_data,
            tags=["user", "preferences"]
        )
        print("   ✅ Wrote to U_CTX (User context)")
        
        # Write observability data
        obs_data = {
            "metrics": {"latency": 120, "success_rate": 0.99},
            "anomalies": [],
            "timestamp": datetime.now().isoformat()
        }
        
        await memory_hub.put(
            context_type=ContextType.OBS_CTX,
            key="metrics:latest",
            value=obs_data,
            tags=["observability", "metrics"]
        )
        print("   ✅ Wrote to OBS_CTX (Observability context)")
        
        # 5. Get All Contexts Summary
        print("\n5. Memory summary across all contexts...")
        
        for context_type in ContextType:
            context = memory_hub.contexts.get(context_type)
            if context:
                entry_count = len(context.entries)
                print(f"   📊 {context_type.value}: {entry_count} entries")
        
        # 6. Direct Context Access (Advanced)
        print("\n6. Advanced: Direct context manipulation...")
        
        # Get raw context object
        shared_context = memory_hub.contexts[ContextType.S_CTX]
        
        # List all keys in shared context
        all_keys = list(shared_context.entries.keys())
        print(f"   🔑 Keys in S_CTX: {all_keys}")
        
        # Get entry with metadata
        if all_keys:
            first_key = all_keys[0]
            entry = shared_context.get_entry(first_key)
            if entry:
                print(f"   📦 Entry details for '{first_key}':")
                print(f"      - Created: {entry.created_at}")
                print(f"      - TTL: {entry.ttl_seconds}s")
                print(f"      - Tags: {entry.tags}")
        
        print("\n" + "=" * 80)
        print("DIRECT MEMORY ACCESS TEST COMPLETE")
        print("=" * 80)
        
        print("\n✅ All memory operations successful!")
        print("\n📝 Key Takeaways:")
        print("   1. Direct read/write using memory_hub.get() and memory_hub.put()")
        print("   2. Tag-based search using memory_hub.search()")
        print("   3. Five context types: S_CTX, A_CTX, O_CTX, U_CTX, OBS_CTX")
        print("   4. Direct context access via memory_hub.contexts[ContextType]")
        print("   5. TTL support for automatic expiration")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await memory_hub.shutdown()


if __name__ == "__main__":
    asyncio.run(test_direct_memory_access())