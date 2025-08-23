#!/usr/bin/env python3
"""NewBuildOrchestrator 테스트 스크립트

새 프로젝트를 처음부터 생성하는 NewBuildOrchestrator를 테스트합니다.
UpgradeOrchestrator와 달리 기존 프로젝트 분석 없이 새로운 프로젝트를 생성합니다.
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.orchestrator.newbuild_orchestrator import (
    NewBuildOrchestrator,
    NewBuildConfig
)


async def test_newbuild_orchestrator():
    """NewBuildOrchestrator 테스트"""
    
    print("=" * 80)
    print("🚀 Testing NewBuildOrchestrator - Building New Project from Scratch")
    print("=" * 80)
    
    # 테스트용 프로젝트 설정
    project_name = f"test-project-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # 요구사항 정의
    requirements = """
    T-Developer-TEST 프로젝트를 새로 생성합니다.
    
    ## 프로젝트 요구사항
    1. Python 기반 웹 애플리케이션
    2. Flask 프레임워크 사용
    3. 사용자 인증 기능
    4. 데이터베이스 연동 (SQLite)
    5. RESTful API 엔드포인트
    6. 단위 테스트 포함
    7. Docker 컨테이너화
    8. CI/CD 파이프라인 설정
    
    ## 주요 기능
    - 사용자 등록/로그인
    - 프로필 관리
    - 게시글 CRUD
    - 댓글 기능
    - 검색 기능
    
    ## 기술 스택
    - Backend: Python, Flask
    - Database: SQLite (개발), PostgreSQL (프로덕션)
    - Authentication: JWT
    - Testing: pytest
    - Containerization: Docker
    - CI/CD: GitHub Actions
    """
    
    print(f"📝 Project Name: {project_name}")
    print(f"📋 Requirements Preview: {requirements[:200]}...")
    
    # NewBuildConfig 생성 (Evolution Loop 활성화)
    config = NewBuildConfig(
        project_name=project_name,
        output_dir="/tmp/t-developer/new-projects",
        project_type="web",
        language="python",
        framework="flask",
        include_tests=True,
        include_docs=True,
        include_ci_cd=True,
        include_docker=True,
        include_kubernetes=False,
        # Evolution Loop 설정
        enable_evolution_loop=True,  # Evolution Loop 활성화
        max_evolution_iterations=3,  # 최대 3번 반복
        evolution_convergence_threshold=0.85,  # 85% 수렴 시 종료
        auto_improve_code=True,  # 코드 자동 개선
        ai_driven_design=True,
        auto_generate_all=True,
        use_best_practices=True,
        max_execution_time=900,  # 15분 (Evolution Loop 고려)
        max_files=50,
        max_code_lines=5000
    )
    
    print("\n⚙️ Configuration:")
    print(f"  - Project Type: {config.project_type}")
    print(f"  - Language: {config.language}")
    print(f"  - Framework: {config.framework}")
    print(f"  - Output Dir: {config.output_dir}")
    print(f"  - Include Tests: {config.include_tests}")
    print(f"  - Include Docker: {config.include_docker}")
    print(f"  - AI-Driven Design: {config.ai_driven_design}")
    print(f"  - Evolution Loop: {config.enable_evolution_loop}")
    print(f"  - Max Iterations: {config.max_evolution_iterations}")
    print(f"  - Convergence Threshold: {config.evolution_convergence_threshold:.0%}")
    
    # 오케스트레이터 생성 및 초기화
    print("\n🔧 Initializing NewBuildOrchestrator...")
    orchestrator = NewBuildOrchestrator(config)
    await orchestrator.initialize()
    print("✅ Orchestrator initialized")
    
    # 빌드 실행
    print("\n🏗️ Starting Project Build...")
    print("-" * 40)
    
    start_time = datetime.now()
    
    try:
        # build 메서드 실행
        report = await orchestrator.build(requirements)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print("\n✅ Build Process Completed!")
        print("-" * 40)
        
        # 결과 출력
        print("\n📊 Build Results:")
        print(f"  - Success: {report.success}")
        print(f"  - Execution Time: {execution_time:.2f}s")
        print(f"  - Project Name: {report.project_name}")
        print(f"  - Output Path: {report.output_path}")
        
        # 단계별 결과 확인
        print("\n📋 Phase Execution Results:")
        
        if report.requirement_analysis:
            print("  ✅ RequirementAnalyzer - Completed")
        else:
            print("  ❌ RequirementAnalyzer - Failed or Skipped")
        
        if report.external_research:
            print("  ✅ ExternalResearcher - Completed")
        else:
            print("  ❌ ExternalResearcher - Failed or Skipped")
        
        if report.architecture_design:
            print("  ✅ SystemArchitect - Completed")
            agents = report.architecture_design.get('agents', [])
            print(f"     - Designed Agents: {len(agents)}")
        else:
            print("  ❌ SystemArchitect - Failed or Skipped")
        
        if report.orchestrator_design:
            print("  ✅ OrchestratorDesigner - Completed")
        else:
            print("  ❌ OrchestratorDesigner - Failed or Skipped")
        
        if report.development_plan:
            print("  ✅ PlannerAgent - Completed")
        else:
            print("  ❌ PlannerAgent - Failed or Skipped")
        
        if report.detailed_tasks:
            print("  ✅ TaskCreatorAgent - Completed")
            print(f"     - Total Tasks: {len(report.detailed_tasks)}")
        else:
            print("  ❌ TaskCreatorAgent - Failed or Skipped")
        
        if report.project_structure:
            print("  ✅ Project Structure - Created")
            print(f"     - Root Dir: {report.project_structure.root_dir}")
            print(f"     - Directories: {len(report.project_structure.directories_to_create)}")
        else:
            print("  ❌ Project Structure - Failed")
        
        if report.code_generated:
            print("  ✅ CodeGenerator - Completed")
            print(f"     - Files Generated: {report.code_generated.get('total_files', 0)}")
            print(f"     - Total Lines: {report.code_generated.get('total_lines', 0)}")
        else:
            print("  ❌ CodeGenerator - Failed or Skipped")
        
        if report.tests_generated:
            print("  ✅ Test Generation - Completed")
            print(f"     - Test Files: {report.tests_generated.get('total_tests', 0)}")
        else:
            print("  ❌ Test Generation - Failed or Skipped")
        
        if report.documentation_generated:
            print("  ✅ Documentation - Completed")
            print(f"     - Docs Generated: {len(report.documentation_generated)}")
        else:
            print("  ❌ Documentation - Failed or Skipped")
        
        if report.quality_metrics:
            print("  ✅ Quality Gate - Completed")
            print(f"     - Quality Score: {report.quality_metrics.get('quality_score', 0):.1f}/100")
        else:
            print("  ❌ Quality Gate - Failed or Skipped")
        
        # Evolution Loop 결과
        if report.evolution_iterations > 0:
            print("\n🔄 Evolution Loop Results:")
            print(f"  - Iterations Completed: {report.evolution_iterations}")
            print(f"  - Convergence Rate: {report.convergence_rate:.2%}")
            print(f"  - Gaps Remaining: {len(report.gaps_remaining) if report.gaps_remaining else 0}")
            
            if report.gap_analysis:
                print(f"  - Gap Score: {report.gap_analysis.get('gap_score', 0):.2%}")
            
            if report.current_state_analysis:
                print("  - Current State Analysis: Completed")
        
        # 생성된 파일 목록
        if report.files_created:
            print("\n📁 Files Created:")
            for file_path in report.files_created[:10]:  # 처음 10개만 표시
                print(f"  • {file_path}")
            if len(report.files_created) > 10:
                print(f"  ... and {len(report.files_created) - 10} more files")
        
        # 에러 및 경고
        if report.errors:
            print("\n❌ Errors:")
            for error in report.errors:
                print(f"  • {error}")
        
        if report.warnings:
            print("\n⚠️ Warnings:")
            for warning in report.warnings:
                print(f"  • {warning}")
        
        # 다음 단계
        if report.next_steps:
            print("\n🎯 Next Steps:")
            for step in report.next_steps:
                print(f"  • {step}")
        
        # 배포 지침 미리보기
        if report.deployment_instructions:
            print("\n📦 Deployment Instructions (Preview):")
            preview = report.deployment_instructions[:300]
            print(preview + "..." if len(report.deployment_instructions) > 300 else preview)
        
        # 전체 보고서를 JSON으로 저장
        test_output_path = Path("test_outputs")
        test_output_path.mkdir(exist_ok=True)
        
        output_file = test_output_path / f"newbuild_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 보고서를 딕셔너리로 변환
        report_dict = {
            "timestamp": report.timestamp,
            "project_name": report.project_name,
            "output_path": report.output_path,
            "success": report.success,
            "total_execution_time": report.total_execution_time,
            "files_created": report.files_created,
            "errors": report.errors,
            "warnings": report.warnings,
            "next_steps": report.next_steps,
            "phases_completed": {
                "requirement_analysis": bool(report.requirement_analysis),
                "external_research": bool(report.external_research),
                "architecture_design": bool(report.architecture_design),
                "orchestrator_design": bool(report.orchestrator_design),
                "development_plan": bool(report.development_plan),
                "detailed_tasks": len(report.detailed_tasks) if report.detailed_tasks else 0,
                "code_generated": bool(report.code_generated),
                "tests_generated": bool(report.tests_generated),
                "documentation_generated": bool(report.documentation_generated),
                "quality_metrics": bool(report.quality_metrics)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\n💾 Full report saved to: {output_file}")
        
        # 프로젝트 디렉토리 확인
        if report.success and report.output_path:
            project_path = Path(report.output_path)
            if project_path.exists():
                print(f"\n✅ Project successfully created at: {project_path}")
                print("\nTo explore the project:")
                print(f"  cd {project_path}")
                print("  ls -la")
            else:
                print(f"\n⚠️ Project directory not found: {project_path}")
        
        print("\n" + "=" * 80)
        if report.success:
            print("🎉 NewBuildOrchestrator Test Completed Successfully!")
        else:
            print("⚠️ NewBuildOrchestrator Test Completed with Issues")
        print("=" * 80)
        
        return report.success
        
    except Exception as e:
        print(f"\n❌ Error during build: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    success = asyncio.run(test_newbuild_orchestrator())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()