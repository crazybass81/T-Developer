#!/usr/bin/env python3
"""T-Developer UNIFIED Evolution Loop 실행 스크립트.

이 스크립트는 갭이 0이 될 때까지 진화 루프를 실행합니다.
Agno와 CodeGenerator를 사용하여 자동으로 에이전트를 생성하고 코드를 구현합니다.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator,
    UpgradeConfig,
    EvolutionResult
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 고정된 요구사항
EVOLUTION_REQUIREMENTS = """# 테스트 대상 프로젝트 : T-Developer-UNIFIED

## 요청사항
1. 개발중인 대상프로젝트를 요청에 따라 업그레이드/디버깅/리팩터링을 수행하는 UpgradeOrchestrator를 완성한다.
2. 정해진 기본 호출 순서에 따라 작업수행 하는 것을 원칙으로 하지만 요청사항에 따라 호출하는 에이전트의 종류나 순서를 변경할 수 있는 AI드리븐 오케스트레이터이다.
3. 기본 호출순서는 요청사항 분석에이전트(요청사항을 파싱,분석해서 문서화) - 대상프로젝트의 현재상태를 분석하는 에이전트 (행동, 임팩트, 정적, 품질, ai동적, 각각의 문서를 작성하고 하나의 통합문서로 종합) - 외부리서치 에이전트(현재상태를 베이스로 요청사항을 달성하는데에 도움이 될 수 있는 최신기술, 코드레퍼런스등 각종 외부자료 조사 후 문서화) - 갭분석 에이전트(현재상태를 베이스로 요청사항을 달성하기 위해 필요한 변경사항을 분석하고, ai가 외부 리서치를 참고하여 큰단위의 계획 수립 후 문서화) - 계획수립 에이전트(큰단위의 계획을 바탕으로 아그노와 코드제너레이터가 생성,수정해야하는 에이전트 계획후 문서화) - 세부임무계획 에이전트 (각 에이전트 구현을 위해 코드제너레이터와 아그노가 수행해야하는 임무를 에이전트 단위로 수립 후 문서화) - 아그노 & 코드제너레이터 에이전트 - 테스트 에이전트 - 현재상태를 분석하는 에이전트들로 돌아가 갭 에이전트가 현재의 상태가 목적의 상태와 일치하면 루프가 종료
4. ai가 방해가 되는 경우를 제외하고 ai드리븐 에이전트/오케스트레이터로 만든다.
5. 문서생성에이전트 : requirement_analyzer.py, behavior_analyzer.py, code_analysis.py, external_researcher.py, gap_analyzer.py, impact_analyzer.py, planner_agent.py, static_analyzer.py, task_creator_agent.py, quality_gate.py
6. requirement레포트는 external_researcher.py, gap_analyzer.py가 참조한다.
7. behavior, code, impact, static, quality등 현재상태 분석레포트는 external_researcher.py, gap_analyzer.py가 참조한다.
8. external_research레포트는 gap_analyzer.py가 참조한다.
9. gap 분석레포트는 planner_agent.py, task_creator_agent.py가 참조한다.
10. planner, task_creator 레포트는 code_generator.py가 참조한다.
11. 참조원칙은 기본값이고, AI가 판단 후 필요에 의해 다른 문서를 참조할 수 있다.
12. 실행버튼을 눌러 생성된 모든 보고서와 계획을 MD파일도 다운받을 수 있도록 한다.
13. 모든 에이전트의 주석에 해당 에이전트의 기능과 목적에 대한 자세한 서술을 기록해놓는다."""


async def main():
    """메인 진화 루프 실행."""
    
    logger.info("=" * 80)
    logger.info("🧬 T-Developer UNIFIED Evolution Loop")
    logger.info("=" * 80)
    logger.info("This will iterate until all gaps are resolved...")
    logger.info("Using Agno and CodeGenerator for automatic implementation")
    logger.info("-" * 80)
    
    # Create configuration with evolution enabled
    config = UpgradeConfig(
        project_path="/home/ec2-user/T-Developer-UNIFIED",
        output_dir="/tmp/t-developer/evolution",
        enable_evolution_loop=True,
        max_evolution_iterations=10,
        auto_generate_agents=True,
        auto_implement_code=True,
        enable_dynamic_analysis=False,  # Safety
        include_behavior_analysis=True,
        generate_impact_matrix=True,
        generate_recommendations=True,
        safe_mode=True,
        parallel_analysis=True,
        max_execution_time=3600  # 1 hour max
    )
    
    # Create and initialize orchestrator
    logger.info("\n🔧 Initializing UpgradeOrchestrator...")
    orchestrator = UpgradeOrchestrator(config)
    await orchestrator.initialize()
    logger.info("✅ Orchestrator initialized successfully")
    
    # Run evolution loop
    logger.info("\n🚀 Starting Evolution Loop...")
    logger.info("This may take considerable time depending on the gaps found...")
    
    try:
        result = await orchestrator.execute_evolution_loop(
            requirements=EVOLUTION_REQUIREMENTS,
            max_iterations=config.max_evolution_iterations
        )
        
        # Display detailed results
        logger.info("\n" + "=" * 80)
        logger.info("🎉 EVOLUTION LOOP COMPLETE")
        logger.info("=" * 80)
        
        if result.success:
            logger.info("\n✨ SUCCESS! All gaps have been resolved!")
            logger.info(f"   Completed in {result.iterations} iterations")
        else:
            logger.info("\n⚠️ INCOMPLETE: Some gaps remain unresolved")
            logger.info(f"   Stopped after {result.iterations} iterations")
            logger.info(f"   Remaining gaps: {len(result.final_gaps)}")
            
            if result.final_gaps:
                logger.info("\n📋 Remaining Gaps:")
                for i, gap in enumerate(result.final_gaps[:10], 1):
                    logger.info(f"   {i}. {gap.get('description', 'Unknown gap')}")
        
        # Statistics
        logger.info("\n📊 Evolution Statistics:")
        logger.info(f"   • Iterations: {result.iterations}")
        logger.info(f"   • Agents created: {len(result.agents_created)}")
        logger.info(f"   • Code generated: {result.code_generated} lines")
        logger.info(f"   • Tests passed: {result.tests_passed}")
        logger.info(f"   • Tests failed: {result.tests_failed}")
        logger.info(f"   • Convergence rate: {result.convergence_rate:.2%}")
        logger.info(f"   • Total time: {result.total_time:.2f}s")
        
        # Created agents
        if result.agents_created:
            logger.info("\n🤖 Agents Created:")
            for agent_path in result.agents_created:
                logger.info(f"   • {agent_path}")
        
        # Evolution history
        if result.evolution_history:
            logger.info("\n📜 Evolution History:")
            for entry in result.evolution_history:
                iteration = entry.get("iteration", 0)
                gaps_before = len(entry.get("gaps_before", []))
                gaps_after = len(entry.get("gaps_after", []))
                duration = entry.get("duration", 0)
                
                logger.info(f"\n   Iteration {iteration}:")
                logger.info(f"     • Gaps: {gaps_before} → {gaps_after}")
                logger.info(f"     • Duration: {duration:.2f}s")
                
                for action in entry.get("actions_taken", []):
                    if isinstance(action, dict):
                        logger.info(f"     • {action.get('gap', 'Action taken')}")
                    else:
                        logger.info(f"     • {action}")
        
        # Save evolution report
        report_path = Path(config.output_dir) / f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                "success": result.success,
                "iterations": result.iterations,
                "final_gaps": result.final_gaps,
                "agents_created": result.agents_created,
                "code_generated": result.code_generated,
                "tests_passed": result.tests_passed,
                "tests_failed": result.tests_failed,
                "convergence_rate": result.convergence_rate,
                "total_time": result.total_time,
                "evolution_history": result.evolution_history
            }, f, indent=2, default=str)
        
        logger.info(f"\n💾 Evolution report saved to: {report_path}")
        
        # Recommendations
        if not result.success and result.final_gaps:
            logger.info("\n💡 Recommendations:")
            logger.info("   1. Review the remaining gaps manually")
            logger.info("   2. Consider adjusting the requirements")
            logger.info("   3. Increase max_iterations if more time is available")
            logger.info("   4. Check logs for any errors during evolution")
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️ Evolution interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Evolution failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        await orchestrator.shutdown()
        logger.info("\n👋 Orchestrator shutdown complete")
    
    logger.info("\n" + "=" * 80)
    logger.info("Evolution loop execution finished")
    logger.info("=" * 80)


if __name__ == "__main__":
    print("\n🧬 T-Developer UNIFIED Evolution Loop Runner")
    print("=" * 50)
    print("This will automatically evolve the system until all gaps are resolved.")
    print("Press Ctrl+C to interrupt at any time.\n")
    
    asyncio.run(main())