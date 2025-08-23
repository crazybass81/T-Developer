#!/usr/bin/env python3
"""분석 파트 및 보고서 생성 통합 테스트."""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

# 프로젝트 경로 설정
import sys
sys.path.append(str(Path(__file__).parent))

from backend.packages.agents.requirement_analyzer import RequirementAnalyzer
from backend.packages.agents.code_analysis import CodeAnalysisAgent
# from backend.packages.agents.report_generator import ReportGenerator  # Module not yet implemented
from backend.packages.agents.external_researcher import ExternalResearcher
from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


async def test_full_analysis_and_report():
    """전체 분석 및 보고서 생성 테스트."""
    print("="*60)
    print("🚀 T-Developer v2 분석 파트 및 보고서 생성 테스트")
    print("="*60)
    
    # 메모리 허브 초기화
    memory = MemoryHub()
    await memory.initialize()
    
    # 테스트 요구사항
    test_requirement = """
    사용자 인증 시스템 구현:
    - 회원가입 기능 (이메일, 비밀번호)
    - 로그인/로그아웃
    - JWT 토큰 기반 인증
    - 비밀번호 암호화 (bcrypt)
    - 세션 관리
    """
    
    print("\n📋 테스트 요구사항:")
    print(test_requirement)
    
    # 1. RequirementAnalyzer 테스트
    print("\n" + "="*60)
    print("1️⃣ RequirementAnalyzer 테스트")
    print("="*60)
    
    requirement_analyzer = RequirementAnalyzer()
    req_task = AgentTask(
        intent="analyze_requirement",
        inputs={"requirement": test_requirement}
    )
    req_response = await requirement_analyzer.execute(req_task)
    req_result = req_response.data
    
    print(f"✅ 분석 완료:")
    print(f"   - 기능 요구사항: {len(req_result.get('functional_requirements', []))}개")
    print(f"   - 비기능 요구사항: {len(req_result.get('non_functional_requirements', []))}개")
    print(f"   - 기술 스택: {', '.join(req_result.get('tech_stack', []))}")
    
    # 메모리에 저장
    await memory.put(
        key="requirement_analysis",
        value=req_result,
        context_type=ContextType.S_CTX
    )
    
    # 2. ExternalResearcher 테스트
    print("\n" + "="*60)
    print("2️⃣ ExternalResearcher 테스트")
    print("="*60)
    
    researcher = ExternalResearcher()
    research_topics = [
        "JWT authentication best practices",
        "bcrypt password hashing security",
        "session management patterns"
    ]
    
    research_results = []
    for topic in research_topics:
        print(f"   🔍 연구 중: {topic}")
        research_task = AgentTask(
            intent="research_topic",
            inputs={"topic": topic}
        )
        research_response = await researcher.execute(research_task)
        result = research_response.data
        research_results.append(result)
        print(f"      ✓ 완료: {len(result.get('findings', []))}개 발견")
    
    print(f"✅ 외부 연구 완료:")
    print(f"   - 연구 주제: {len(research_topics)}개")
    print(f"   - 총 발견사항: {sum(len(r.get('findings', [])) for r in research_results)}개")
    
    # 메모리에 저장
    await memory.put(
        key="research_results",
        value={"topics": research_topics, "results": research_results},
        context_type=ContextType.S_CTX
    )
    
    # 3. CodeAnalysisAgent 테스트
    print("\n" + "="*60)
    print("3️⃣ CodeAnalysisAgent 테스트")
    print("="*60)
    
    code_analyzer = CodeAnalysisAgent()
    
    # 현재 프로젝트 코드 분석 - 간단한 파일로 테스트
    test_file = Path(__file__)
    code_task = AgentTask(
        intent="analyze_code",
        inputs={
            "file_path": str(test_file),
            "analysis_type": "general",
            "language": "python"
        }
    )
    code_response = await code_analyzer.execute(code_task)
    code_result = code_response.data
    
    print(f"✅ 코드 분석 완료:")
    print(f"   - 분석된 파일: {code_result.get('total_files', 0)}개")
    print(f"   - 총 라인 수: {code_result.get('total_lines', 0)}")
    print(f"   - 평균 복잡도: {code_result.get('average_complexity', 0):.2f}")
    print(f"   - 품질 점수: {code_result.get('quality_score', 0):.2f}/100")
    
    # 메모리에 저장
    await memory.put(
        key="code_analysis",
        value=code_result,
        context_type=ContextType.S_CTX
    )
    
    # 4. ReportGenerator 테스트
    print("\n" + "="*60)
    print("4️⃣ ReportGenerator 테스트")
    print("="*60)
    
    report_generator = ReportGenerator()
    
    # 종합 분석 데이터 준비
    analysis_data = {
        "requirement_analysis": req_result,
        "research_results": research_results,
        "code_analysis": code_result,
        "timestamp": datetime.now().isoformat(),
        "project_name": "T-Developer v2",
        "analyzed_by": "T-Developer Analysis System"
    }
    
    # 보고서 생성
    report_task = AgentTask(
        intent="generate_report",
        inputs={
            "analysis_data": analysis_data,
            "report_type": "comprehensive",
            "format": "markdown"
        }
    )
    report_response = await report_generator.execute(report_task)
    report = report_response.data
    
    # 보고서 저장
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"analysis_report_{timestamp}.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report['content'])
    
    print(f"✅ 보고서 생성 완료:")
    print(f"   - 보고서 유형: {report.get('type', 'N/A')}")
    print(f"   - 포맷: {report.get('format', 'N/A')}")
    print(f"   - 크기: {len(report.get('content', ''))} 문자")
    print(f"   - 저장 경로: {report_path.absolute()}")
    
    # JSON 형식 보고서도 생성
    json_task = AgentTask(
        intent="generate_report",
        inputs={
            "analysis_data": analysis_data,
            "report_type": "comprehensive",
            "format": "json"
        }
    )
    json_response = await report_generator.execute(json_task)
    json_report = json_response.data
    
    json_path = reports_dir / f"analysis_report_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_report['content'], f, indent=2, ensure_ascii=False)
    
    print(f"   - JSON 보고서: {json_path.absolute()}")
    
    # 5. 메모리 허브 확인
    print("\n" + "="*60)
    print("5️⃣ 메모리 허브 상태")
    print("="*60)
    
    # 메모리 검색
    memories = await memory.search("", context_type=ContextType.S_CTX, limit=5)
    print(f"✅ 저장된 메모리: {len(memories)}개")
    for mem in memories:
        print(f"   - {mem.get('key', 'N/A')}: 저장됨")
    
    print("\n" + "="*60)
    print("✅ 모든 테스트 완료!")
    print("="*60)
    print(f"\n📁 생성된 보고서 위치:")
    print(f"   - Markdown: {report_path.absolute()}")
    print(f"   - JSON: {json_path.absolute()}")
    
    return {
        "markdown_report": str(report_path.absolute()),
        "json_report": str(json_path.absolute()),
        "test_status": "SUCCESS"
    }


if __name__ == "__main__":
    # 이벤트 루프 실행
    result = asyncio.run(test_full_analysis_and_report())
    
    print("\n" + "="*60)
    print("🎉 테스트 완료 요약")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))