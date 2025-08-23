#!/usr/bin/env python3
"""Run UpgradeOrchestrator to analyze T-Developer V2 itself."""

import asyncio
import sys
from pathlib import Path
import logging

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator,
    UpgradeConfig
)
from backend.packages.memory.hub import MemoryHub
from backend.packages.agents.ai_providers import BedrockAIProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_analysis():
    """Run comprehensive analysis on T-Developer V2."""
    
    print("=" * 80)
    print("  T-DEVELOPER V2 SELF-EVOLUTION ANALYSIS")
    print("=" * 80)
    print()
    
    # Initialize components
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    ai_provider = BedrockAIProvider(
        model="claude-3-sonnet",
        region="us-east-1"
    )
    
    # Configure analysis
    config = UpgradeConfig(
        project_path="/home/ec2-user/T-Developer-v2",
        output_dir="/home/ec2-user/T-Developer-v2/docs/reports",
        enable_dynamic_analysis=False,  # Don't execute code
        include_behavior_analysis=True,
        generate_impact_matrix=True,
        generate_recommendations=True,
        safe_mode=True,
        max_execution_time=1200,  # 20 minutes
        parallel_analysis=True
    )
    
    # Create orchestrator (it initializes its own memory hub)
    orchestrator = UpgradeOrchestrator(config=config)
    
    # Initialize the orchestrator
    await orchestrator.initialize()
    
    # Define evolution requirements
    requirements = """
    Analyze T-Developer V2 system for self-evolution capabilities:
    
    1. Current Architecture Analysis
       - Agent ecosystem completeness
       - Memory system effectiveness
       - Report generation and consumption flow
       - Safety mechanisms implementation
    
    2. Evolution Capabilities
       - Self-improvement mechanisms
       - Learning from execution history
       - Automatic optimization paths
       - Code generation quality improvement
    
    3. Gap Analysis
       - Missing components for full autonomy
       - Bottlenecks in current workflow
       - Areas requiring human intervention
       - Test coverage gaps
    
    4. Evolution Recommendations
       - Priority improvements for next version
       - New agents or components needed
       - Architecture optimizations
       - Performance enhancements
    
    5. Success Metrics
       - Code quality metrics
       - Execution efficiency
       - Memory utilization
       - Agent collaboration effectiveness
    
    Goal: Identify concrete steps for T-Developer V2 to evolve into a more autonomous,
    efficient, and capable system that can improve itself with minimal human intervention.
    """
    
    try:
        print("Starting comprehensive analysis...")
        print(f"Target: {config.project_path}")
        print(f"Output: {config.output_dir}")
        print()
        
        # Run analysis
        report = await orchestrator.analyze(
            requirements=requirements,
            include_research=True  # Include external research
        )
        
        print("\n" + "=" * 80)
        print("  ANALYSIS COMPLETE")
        print("=" * 80)
        
        # Summary
        print(f"\n📊 Analysis Summary:")
        print(f"  • Phases completed: {report.phases_completed}")
        print(f"  • Phases failed: {report.phases_failed}")
        print(f"  • Execution time: {report.total_execution_time:.2f} seconds")
        
        if report.evolution_goal:
            print(f"\n🎯 Evolution Goal:")
            print(f"  • Background: {report.evolution_goal.background[:100]}...")
            print(f"  • Stakeholders: {', '.join(report.evolution_goal.stakeholders[:3])}")
        
        if report.current_state:
            print(f"\n📈 Current State:")
            if hasattr(report.current_state, 'ai_summary'):
                print(f"  • AI Summary available")
            if hasattr(report.current_state, 'test_gaps'):
                print(f"  • Test gaps identified: {len(report.current_state.test_gaps)}")
        
        if report.gap_report:
            print(f"\n🔍 Gap Analysis:")
            print(f"  • Gap report generated")
        
        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(report.recommendations[:3], 1):
                print(f"  {i}. {rec.get('title', rec)[:80]}...")
        
        print(f"\n✅ Analysis complete. Reports saved in memory and filesystem.")
        print(f"   Run extract_reports.py to copy all reports to /docs/reports/")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await memory_hub.shutdown()
        print("\n✨ Memory hub shutdown complete")


if __name__ == "__main__":
    print("\n🚀 Starting T-Developer V2 Self-Evolution Analysis...")
    print("   This will analyze the system to identify evolution opportunities.")
    print("   Please ensure AWS credentials are configured.\n")
    
    asyncio.run(run_analysis())