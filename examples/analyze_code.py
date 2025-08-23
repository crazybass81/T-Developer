#!/usr/bin/env python3
"""Example: Analyze code using CodeAnalysisAgent with real AI.

This example demonstrates:
1. Initializing Memory Hub
2. Creating a CodeAnalysisAgent with AWS Bedrock
3. Analyzing actual code files
4. Using memory to reference previous analyses
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.memory import MemoryHub, ContextType
from backend.packages.agents import AgentTask, AgentRegistry
from backend.packages.agents.code_analysis import CodeAnalysisAgent
from backend.packages.agents.registry import AgentSpec


async def main():
    """Run the code analysis example."""
    
    print("🚀 T-Developer v2 - Code Analysis Example")
    print("=" * 50)
    
    # 1. Initialize Memory Hub
    print("\n1. Initializing Memory Hub...")
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    print("   ✅ Memory Hub ready")
    
    # 2. Create Agent Registry
    print("\n2. Setting up Agent Registry...")
    registry = AgentRegistry()
    
    # 3. Create CodeAnalysisAgent
    print("\n3. Creating CodeAnalysisAgent...")
    agent = CodeAnalysisAgent(
        memory_hub=memory_hub,
        model="claude-3-haiku",  # Fast and cost-effective
        region="us-east-1"
    )
    
    # Register the agent
    spec = AgentSpec(
        name="CodeAnalysisAgent",
        version="1.0.0",
        purpose="Analyze code for quality, security, and performance using AI",
        inputs={
            "file_path": "string (optional)",
            "code": "string (optional)",
            "analysis_type": "string (general/security/performance/test)",
            "language": "string (default: python)"
        },
        outputs={
            "analysis": "object",
            "code_stats": "object",
            "used_history": "boolean"
        },
        policies={
            "ai_first": True,
            "dedup_required": True
        },
        memory={
            "read": ["A_CTX", "S_CTX"],
            "write": ["A_CTX", "S_CTX"]
        },
        tags=["code", "analysis", "ai"]
    )
    
    registry.register(CodeAnalysisAgent, spec, agent)
    print("   ✅ Agent registered")
    
    # 4. Prepare sample code for analysis
    sample_code = """
def calculate_fibonacci(n):
    '''Calculate fibonacci number at position n'''
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def find_prime_numbers(limit):
    '''Find all prime numbers up to limit'''
    primes = []
    for num in range(2, limit + 1):
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process_data(self, raw_data):
        # TODO: Add error handling
        processed = []
        for item in raw_data:
            if item > 0:
                processed.append(item * 2)
        self.data = processed
        return processed
"""
    
    # 5. Create analysis task
    print("\n4. Creating analysis task...")
    task = AgentTask(
        intent="analyze_code",
        inputs={
            "code": sample_code,
            "analysis_type": "general",
            "language": "python",
            "use_history": False  # First run, no history
        }
    )
    
    # 6. Execute analysis
    print("\n5. Executing code analysis with AI...")
    print("   (This will use AWS Bedrock to analyze the code)")
    
    try:
        result = await agent.execute(task)
        
        if result.success:
            print("\n✅ Analysis completed successfully!")
            print("\n" + "=" * 50)
            print("ANALYSIS RESULTS:")
            print("=" * 50)
            
            analysis_data = result.data.get("analysis", {})
            
            # Print analysis based on type
            if "summary" in analysis_data:
                print(f"\n📝 Summary: {analysis_data.get('summary', 'N/A')}")
            
            if "quality_score" in analysis_data:
                print(f"\n⭐ Quality Score: {analysis_data.get('quality_score', 'N/A')}/10")
            
            if "issues" in analysis_data:
                issues = analysis_data.get("issues", [])
                print(f"\n⚠️  Issues Found ({len(issues)}):")
                for i, issue in enumerate(issues[:5], 1):  # Show first 5 issues
                    if isinstance(issue, str):
                        print(f"   {i}. {issue}")
                    elif isinstance(issue, dict):
                        print(f"   {i}. {issue.get('description', issue)}")
            
            if "suggestions" in analysis_data:
                suggestions = analysis_data.get("suggestions", [])
                print(f"\n💡 Suggestions ({len(suggestions)}):")
                for i, suggestion in enumerate(suggestions[:5], 1):  # Show first 5
                    if isinstance(suggestion, str):
                        print(f"   {i}. {suggestion}")
                    elif isinstance(suggestion, dict):
                        print(f"   {i}. {suggestion.get('description', suggestion)}")
            
            # Print metadata
            print(f"\n📊 Code Statistics:")
            code_stats = result.data.get("code_stats", {})
            print(f"   - Lines: {code_stats.get('lines', 'N/A')}")
            print(f"   - Size: {code_stats.get('size_bytes', 'N/A')} bytes")
            
            print(f"\n⏱️  Execution Time: {result.execution_time_ms}ms")
            
            # 7. Run second analysis to test memory
            print("\n" + "=" * 50)
            print("6. Running second analysis (with history)...")
            
            task2 = AgentTask(
                intent="analyze_code",
                inputs={
                    "code": sample_code,
                    "analysis_type": "performance",  # Different type
                    "language": "python",
                    "use_history": True  # Use previous analysis
                }
            )
            
            result2 = await agent.execute(task2)
            
            if result2.success:
                print("✅ Second analysis completed!")
                print(f"   Used history: {result2.data.get('used_history', False)}")
                print(f"   History count: {result2.data.get('history_count', 0)}")
                
                perf_analysis = result2.data.get("analysis", {})
                if "bottlenecks" in perf_analysis:
                    print(f"\n🔍 Performance Bottlenecks:")
                    bottlenecks = perf_analysis.get("bottlenecks", [])
                    for bottleneck in bottlenecks[:3]:
                        if isinstance(bottleneck, str):
                            print(f"   - {bottleneck}")
                        elif isinstance(bottleneck, dict):
                            print(f"   - {bottleneck.get('description', bottleneck)}")
            
            # 8. Check memory contents
            print("\n" + "=" * 50)
            print("7. Checking Memory Hub contents...")
            
            # Check shared context
            shared_summary = await memory_hub.get(
                ContextType.S_CTX,
                f"latest_execution_{agent.agent_id}"
            )
            if shared_summary:
                print(f"\n📚 Latest execution in shared memory:")
                print(f"   - Intent: {shared_summary.get('task_intent', 'N/A')}")
                print(f"   - Success: {shared_summary.get('success', 'N/A')}")
            
            # Get context stats
            for ctx_type in [ContextType.S_CTX, ContextType.A_CTX]:
                stats = await memory_hub.get_context_stats(ctx_type)
                print(f"\n📊 {ctx_type.value} context stats:")
                print(f"   - Total entries: {stats.get('total_entries', 0)}")
            
        else:
            print(f"\n❌ Analysis failed: {result.error}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n⚠️  Note: This example requires:")
        print("   1. AWS credentials configured (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        print("   2. AWS Bedrock access in us-east-1 region")
        print("   3. Claude model access in Bedrock")
    
    finally:
        # Cleanup
        print("\n8. Shutting down...")
        await memory_hub.shutdown()
        print("   ✅ Cleanup complete")
    
    print("\n" + "=" * 50)
    print("Example completed! 🎉")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())