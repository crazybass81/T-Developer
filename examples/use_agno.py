#!/usr/bin/env python3
"""Example: Create a new agent using Agno Manager.

This example demonstrates how Agno:
1. Analyzes requirements
2. Checks for duplicates (DD-Gate)
3. Creates agent specifications
4. Generates implementation code using Claude
5. Registers the new agent
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.memory import MemoryHub
from backend.packages.agents.registry import AgentRegistry
from backend.packages.agno import AgnoManager


async def main():
    """Run the Agno example."""
    
    print("🚀 T-Developer v2 - Agno Manager Example")
    print("=" * 60)
    print("This example will create a new agent from requirements.")
    print()
    
    # 1. Initialize components
    print("1. Initializing Agno components...")
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    registry = AgentRegistry()
    
    agno = AgnoManager(
        memory_hub=memory_hub,
        registry=registry
    )
    print("   ✅ Agno Manager ready")
    
    # 2. Define requirements for a new agent
    print("\n2. Defining agent requirements...")
    
    # Example 1: Data Validation Agent
    validation_agent_requirements = {
        "name": "DataValidator",
        "version": "1.0.0",
        "purpose": "Validate and clean incoming data according to specified rules",
        "capability": "validate",
        "inputs": [
            {
                "name": "data",
                "type": "dict",
                "required": True,
                "description": "Raw data to validate"
            },
            {
                "name": "schema",
                "type": "dict",
                "required": True,
                "description": "Validation schema defining rules"
            },
            {
                "name": "strict_mode",
                "type": "bool",
                "required": False,
                "description": "Whether to fail on any validation error"
            }
        ],
        "outputs": [
            {
                "name": "valid",
                "type": "bool",
                "description": "Whether the data is valid"
            },
            {
                "name": "cleaned_data",
                "type": "dict",
                "description": "Cleaned and validated data"
            },
            {
                "name": "errors",
                "type": "list",
                "description": "List of validation errors"
            }
        ],
        "policies": {
            "ai_first": False,  # This is a deterministic operation
            "dedup_required": True,
            "timeout_seconds": 60
        },
        "memory": {
            "read": ["S_CTX"],
            "write": ["A_CTX", "S_CTX"]
        },
        "tags": ["validation", "data-quality", "preprocessing"]
    }
    
    print("   Agent: DataValidator")
    print(f"   Purpose: {validation_agent_requirements['purpose']}")
    print(f"   Inputs: {len(validation_agent_requirements['inputs'])} parameters")
    print(f"   Outputs: {len(validation_agent_requirements['outputs'])} fields")
    
    # 3. Create the agent using Agno
    print("\n3. Creating agent with Agno...")
    print("   ⏳ This will:")
    print("      - Check for duplicates (DD-Gate)")
    print("      - Create agent specification")
    print("      - Generate implementation with Claude")
    print("      - Register the agent")
    print()
    
    try:
        result = await agno.create_agent(
            requirements=validation_agent_requirements,
            auto_implement=True,  # Generate code automatically
            force_create=False     # Check for duplicates
        )
        
        # 4. Display results
        print("\n4. Agent Creation Results:")
        print("=" * 60)
        
        # Status
        status = result.get("status", "unknown")
        print(f"\n📊 Status: {status.upper()}")
        
        # Duplicate check
        dup_check = result.get("duplicate_check", {})
        if dup_check.get("is_duplicate"):
            print("\n⚠️  DUPLICATE DETECTED!")
            similar = dup_check.get("similar_agents", [])
            if similar:
                print("   Similar existing agents:")
                for agent in similar[:3]:
                    print(f"   - {agent['name']} (similarity: {agent['similarity']:.2%})")
                    print(f"     Suggestion: {agent['suggestion']}")
        else:
            print("\n✅ No duplicates found (DD-Gate passed)")
        
        # Reusable components
        reusable = result.get("reusable_components", [])
        if reusable:
            print(f"\n♻️  Found {len(reusable)} reusable components:")
            for comp in reusable[:3]:
                print(f"   - {comp['name']} ({comp['type']})")
        
        # Specification
        if "spec" in result:
            print("\n📄 Agent Specification Created:")
            spec_lines = result["spec"].split("\n")[:15]  # First 15 lines
            for line in spec_lines:
                print(f"   {line}")
            if len(result["spec"].split("\n")) > 15:
                print("   ...")
        
        # Implementation
        if "implementation" in result:
            impl = result["implementation"]
            print(f"\n💻 Code Generated:")
            print(f"   Files created: {len(impl)}")
            for filename in impl.keys():
                print(f"   - {filename}")
            
            # Show a snippet of the generated agent code
            agent_file = f"{validation_agent_requirements['name'].lower()}_agent.py"
            if agent_file in impl:
                code_lines = impl[agent_file].split("\n")[:20]
                print(f"\n   Preview of {agent_file}:")
                for line in code_lines:
                    print(f"   {line}")
                print("   ...")
        
        # Validation
        if "validation" in result:
            val = result["validation"]
            if val["valid"]:
                print("\n✅ Generated code validation: PASSED")
            else:
                print("\n❌ Generated code validation: FAILED")
                for error in val["errors"][:3]:
                    print(f"   - {error}")
        
        # Registration
        if "registration" in result:
            reg = result["registration"]
            if reg.get("registered"):
                print(f"\n✅ Agent registered: {reg['registry_name']} v{reg['version']}")
            else:
                print(f"\n❌ Registration failed: {reg.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"\n❌ Error creating agent: {str(e)}")
        print("\n⚠️  Note: This example requires:")
        print("   1. AWS credentials configured")
        print("   2. AWS Bedrock access")
        print("   3. Claude model access in Bedrock")
    
    # 5. Try creating another agent to test duplicate detection
    print("\n" + "=" * 60)
    print("5. Testing Duplicate Detection...")
    print("   Creating similar agent to test DD-Gate...")
    
    similar_requirements = validation_agent_requirements.copy()
    similar_requirements["name"] = "DataChecker"  # Different name
    similar_requirements["purpose"] = "Check and validate data using rules"  # Similar purpose
    
    try:
        dup_result = await agno.create_agent(
            requirements=similar_requirements,
            auto_implement=False,  # Skip implementation for speed
            force_create=False
        )
        
        if dup_result.get("duplicate_check", {}).get("is_duplicate"):
            print("   ✅ DD-Gate working: Duplicate detected!")
            print(f"   Suggestion: {dup_result.get('suggestion', 'Use existing agent')}")
        else:
            print("   ℹ️  No duplicate detected (might be different enough)")
            
    except Exception as e:
        print(f"   ❌ Error in duplicate test: {str(e)}")
    
    # 6. List all specifications
    print("\n6. Listing all agent specifications...")
    specs = await agno.list_specifications()
    if specs:
        print(f"   Found {len(specs)} specifications:")
        for spec in specs:
            print(f"   - {spec['name']} v{spec['version']}: {spec['capability']}")
    else:
        print("   No specifications found")
    
    # 7. Cleanup
    print("\n7. Shutting down...")
    await memory_hub.shutdown()
    print("   ✅ Cleanup complete")
    
    print("\n" + "=" * 60)
    print("Agno Example completed! 🎉")
    print("\nKey Takeaways:")
    print("- Agno automates agent creation from requirements")
    print("- DD-Gate prevents duplicate development")
    print("- Claude generates actual implementation code")
    print("- Agents are automatically registered and tracked")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())