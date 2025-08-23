#!/usr/bin/env python3
"""ReportGenerator 단독 테스트 - 보고서 생성 검증."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

# from backend.packages.agents.report_generator import ReportGenerator  # Module not yet implemented
from backend.packages.agents.base import AgentTask
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


async def test_report_generator():
    """ReportGenerator 상세 테스트."""
    print("="*80)
    print("📝 ReportGenerator 검증 테스트")
    print("="*80)
    
    # 메모리 허브 초기화
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    # ReportGenerator 생성
    report_gen = ReportGenerator(memory_hub=memory_hub)
    
    # 테스트 1: 프로젝트 분석 보고서
    analysis_data = {
        "project_name": "User Management API",
        "requirement": "Build REST API with FastAPI",
        "analysis": {
            "functional_requirements": [
                "CRUD operations for users",
                "JWT authentication",
                "Input validation"
            ],
            "non_functional_requirements": [
                "80% test coverage",
                "Rate limiting",
                "OpenAPI documentation"
            ],
            "components": [
                {"name": "API Endpoints", "type": "REST API"},
                {"name": "Auth Service", "type": "Service"},
                {"name": "Database", "type": "PostgreSQL"}
            ],
            "complexity": "medium",
            "estimated_effort": "3-4 weeks"
        },
        "feasibility": {
            "overall_score": 0.85,
            "technical_feasibility": True,
            "risks": ["Security vulnerabilities", "Performance issues"]
        }
    }
    
    print("\n📋 테스트 1: 프로젝트 분석 보고서")
    print("-"*50)
    print(f"프로젝트: {analysis_data['project_name']}")
    
    # 보고서 생성 실행
    task1 = AgentTask(
        intent="generate_report",
        inputs={
            "report_type": "analysis",
            "data": analysis_data,
            "format": "markdown"
        }
    )
    
    print("\n🔄 보고서 생성 중...")
    result1 = await report_gen.execute(task1)
    
    print(f"\n✅ 보고서 생성 결과:")
    print(f"   - 성공 여부: {result1.success}")
    print(f"   - 상태: {result1.status}")
    
    if result1.success and result1.data:
        data = result1.data
        
        # 보고서 내용 출력
        print(f"\n📊 생성된 보고서:")
        
        if 'report_path' in data:
            print(f"   - 파일 경로: {data['report_path']}")
        
        if 'summary' in data:
            print(f"\n   [요약]")
            summary = data['summary']
            if isinstance(summary, str):
                print(f"   {summary[:200]}...")
            else:
                print(f"   {summary}")
        
        if 'sections' in data:
            sections = data['sections']
            print(f"\n   [섹션] {len(sections)}개")
            for section in sections[:5]:
                if isinstance(section, dict):
                    print(f"   • {section.get('title', 'N/A')}")
                else:
                    print(f"   • {section}")
        
        if 'metadata' in data:
            meta = data['metadata']
            print(f"\n   [메타데이터]")
            print(f"   • 생성일: {meta.get('created_at', 'N/A')}")
            print(f"   • 포맷: {meta.get('format', 'N/A')}")
            print(f"   • 버전: {meta.get('version', 'N/A')}")
    
    # 결과를 파일로 저장
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"report_test_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "input_data": analysis_data,
            "result": {
                "success": result1.success,
                "status": str(result1.status),
                "data": result1.data,
                "metadata": result1.metadata
            }
        }, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n💾 테스트 결과 저장: {output_file.absolute()}")
    
    # 테스트 2: 진행 상황 보고서
    print("\n" + "="*80)
    progress_data = {
        "project_name": "Microservices Migration",
        "total_tasks": 25,
        "completed_tasks": 15,
        "in_progress_tasks": 5,
        "pending_tasks": 5,
        "milestones": [
            {"name": "Service Extraction", "status": "completed", "date": "2025-08-20"},
            {"name": "Infrastructure Setup", "status": "in_progress", "date": "2025-08-22"},
            {"name": "Data Migration", "status": "pending", "date": "2025-08-25"}
        ],
        "issues": [
            {"severity": "high", "description": "Database sync delay"},
            {"severity": "medium", "description": "Service discovery configuration"}
        ],
        "next_steps": [
            "Complete infrastructure setup",
            "Begin data migration testing",
            "Prepare rollback plan"
        ]
    }
    
    print("📋 테스트 2: 진행 상황 보고서")
    print("-"*50)
    print(f"프로젝트: {progress_data['project_name']}")
    print(f"진행률: {progress_data['completed_tasks']}/{progress_data['total_tasks']} 완료")
    
    task2 = AgentTask(
        intent="generate_report",
        inputs={
            "report_type": "progress",
            "data": progress_data,
            "format": "markdown"
        }
    )
    
    print("\n🔄 보고서 생성 중...")
    result2 = await report_gen.execute(task2)
    
    if result2.success and result2.data:
        print(f"\n✅ 진행 상황 보고서 생성 완료:")
        if 'report_path' in result2.data:
            print(f"   • 파일 경로: {result2.data['report_path']}")
        print(f"   • 섹션 수: {len(result2.data.get('sections', []))}")
    
    # 메모리에서 저장된 보고서 확인
    print("\n" + "="*80)
    print("📦 메모리 허브 확인")
    print("-"*50)
    
    # 저장된 보고서 검색
    stored_reports = await memory_hub.search(
        context_type=ContextType.S_CTX,  # Reports might be in S_CTX
        limit=5
    )
    
    print(f"저장된 항목: {len(stored_reports)}개")
    for report in stored_reports:
        print(f"  - Key: {report.get('key', 'N/A')}")
        print(f"    Created: {report.get('created_at', 'N/A')}")
    
    # 정리
    await memory_hub.shutdown()
    print("\n✅ ReportGenerator 테스트 완료!")


if __name__ == "__main__":
    import os
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("🔧 환경 설정:")
    print(f"   - AWS Region: {os.environ.get('AWS_DEFAULT_REGION')}")
    print(f"   - Python: {sys.version.split()[0]}")
    print()
    
    asyncio.run(test_report_generator())