#!/usr/bin/env python3
"""T-Developer v2 전체 분석 및 보고서 생성 테스트 - 실제 프로젝트 분석."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from backend.packages.orchestrator.upgrade_orchestrator import UpgradeOrchestrator as AIOrchestrator
from backend.packages.memory.hub import MemoryHub


async def test_full_project_analysis():
    """현재 T-Developer v2 프로젝트 전체 분석."""
    print("="*80)
    print("🚀 T-Developer v2 프로젝트 완전 분석")
    print("="*80)
    
    # 메모리 허브 초기화
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    # AI Orchestrator 생성
    orchestrator = AIOrchestrator(memory_hub)
    
    # 현재 프로젝트를 개선하는 요구사항
    requirement = """
    Analyze the T-Developer v2 project and generate:
    1. Complete code analysis report
    2. Architecture documentation
    3. Quality metrics assessment
    4. Security vulnerability scan
    5. Performance optimization recommendations
    6. Test coverage report
    7. Dependency analysis
    8. Technical debt assessment
    9. Best practices compliance check
    10. Comprehensive improvement roadmap
    
    Focus on:
    - All Python files in backend/packages/
    - Safety mechanisms (CircuitBreaker, ResourceLimiter)
    - Agent implementations
    - AI Provider integrations
    - Memory management system
    
    Generate actionable recommendations for each area.
    """
    
    print("\n📋 분석 요구사항:")
    print(requirement[:200] + "...")
    
    print("\n" + "="*80)
    print("🔄 프로젝트 분석 시작...")
    print("="*80)
    
    start_time = datetime.now()
    
    try:
        # 오케스트레이션 실행
        result = await orchestrator.orchestrate(requirement)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "="*80)
        print("✅ 분석 완료!")
        print("="*80)
        
        # 결과 요약
        print(f"\n📊 분석 결과 요약:")
        print(f"   - 성공 여부: {'✅' if result['success'] else '❌'}")
        print(f"   - 실행 시간: {execution_time:.2f}초")
        print(f"   - 완료된 에이전트: {len(result.get('completed_agents', []))}개")
        
        # 각 에이전트 결과 요약
        if result.get('results'):
            print(f"\n📍 에이전트별 결과:")
            
            # RequirementAnalyzer
            if 'requirement_analyzer' in result['results']:
                req_data = result['results']['requirement_analyzer']
                if isinstance(req_data, dict):
                    spec = req_data.get('specification', {})
                    print(f"\n   [RequirementAnalyzer]")
                    print(f"   - 기능 요구사항: {len(spec.get('functional_requirements', []))}개")
                    print(f"   - 비기능 요구사항: {len(spec.get('non_functional_requirements', []))}개")
                    print(f"   - 복잡도: {spec.get('complexity', 'N/A')}")
            
            # CodeAnalysisAgent
            if 'code_analyzer' in result['results']:
                code_data = result['results']['code_analyzer']
                if isinstance(code_data, dict):
                    print(f"\n   [CodeAnalysisAgent]")
                    analysis = code_data.get('analysis', {})
                    if analysis:
                        print(f"   - 분석된 파일: {code_data.get('file_path', 'N/A')}")
                        print(f"   - 코드 라인: {code_data.get('code_stats', {}).get('lines', 0)}")
            
            # ExternalResearcher
            if 'external_researcher' in result['results']:
                research_data = result['results']['external_researcher']
                if isinstance(research_data, dict):
                    print(f"\n   [ExternalResearcher]")
                    print(f"   - 연구 영역: {len(research_data.get('research_areas', []))}개")
                    print(f"   - 주요 발견: {len(research_data.get('key_findings', []))}개")
                    print(f"   - 권장사항: {len(research_data.get('recommendations', []))}개")
            
            # CodeGenerator
            if 'code_generator' in result['results']:
                gen_data = result['results']['code_generator']
                if isinstance(gen_data, dict):
                    print(f"\n   [CodeGenerator]")
                    if 'files' in gen_data:
                        print(f"   - 생성된 파일: {len(gen_data['files'])}개")
                    if 'code' in gen_data:
                        print(f"   - 코드 크기: {len(gen_data['code'])} 문자")
            
            # QualityGate
            if 'quality_gate' in result['results']:
                quality_data = result['results']['quality_gate']
                if isinstance(quality_data, dict):
                    print(f"\n   [QualityGate]")
                    print(f"   - 품질 통과: {'✅' if quality_data.get('passed', False) else '❌'}")
                    if 'metrics' in quality_data:
                        metrics = quality_data['metrics']
                        print(f"   - 테스트 커버리지: {metrics.get('test_coverage', 0)}%")
                        print(f"   - 코드 복잡도: {metrics.get('complexity', 0)}")
        
        # 개선 제안
        if result.get('improvements'):
            print(f"\n💡 주요 개선 제안:")
            for i, improvement in enumerate(result['improvements'][:5], 1):
                print(f"   {i}. {improvement[:100]}...")
        
        # 보고서 정보
        if result.get('report'):
            report = result['report']
            if isinstance(report, dict) and 'report_path' in report:
                print(f"\n📄 생성된 보고서:")
                print(f"   - 경로: {report['report_path']}")
                print(f"   - 형식: {report.get('format', 'N/A')}")
                
                # 보고서 내용 미리보기
                report_path = Path(report['report_path'])
                if report_path.exists():
                    with open(report_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"   - 크기: {len(content)} 문자")
                        print(f"\n   [보고서 미리보기]")
                        print("   " + "-"*50)
                        preview = content[:500].replace('\n', '\n   ')
                        print(f"   {preview}...")
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"full_analysis_result_{timestamp}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\n💾 전체 결과 저장: {output_file.absolute()}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        await memory_hub.shutdown()


if __name__ == "__main__":
    import os
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    print(f"   - 프로젝트 경로: {Path.cwd()}")
    
    # 테스트 실행
    asyncio.run(test_full_project_analysis())