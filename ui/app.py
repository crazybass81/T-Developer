#!/usr/bin/env python3
"""T-Developer 테스트 UI - Streamlit 기반

이 UI는 T-Developer의 오케스트레이터들을 테스트하고
실행 과정을 모니터링할 수 있는 웹 인터페이스를 제공합니다.

주요 기능:
1. 프로젝트 경로 선택
2. 요구사항 입력
3. 실시간 진행 상황 표시
4. 생성된 문서 다운로드
"""

import streamlit as st
import asyncio
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import sys
import os
import zipfile
import io

# T-Developer 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator, UpgradeConfig
)
from backend.packages.orchestrator.newbuild_orchestrator import (
    NewBuildOrchestrator, NewBuildConfig
)

# 페이지 설정
st.set_page_config(
    page_title="T-Developer Control Panel",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
    }
    .status-running {
        color: #1f77b4;
        font-weight: bold;
    }
    .status-success {
        color: #2ca02c;
        font-weight: bold;
    }
    .status-failed {
        color: #d62728;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'running' not in st.session_state:
    st.session_state.running = False
if 'result' not in st.session_state:
    st.session_state.result = None
if 'documents' not in st.session_state:
    st.session_state.documents = {}

# 제목과 설명
st.title("🚀 T-Developer Control Panel")
st.markdown("**AI-Driven Autonomous Development System** - 자연어로 시스템을 진화시키세요")

# 사이드바 - 설정
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 오케스트레이터 선택
    orchestrator_type = st.radio(
        "오케스트레이터 선택",
        ["🔧 기존 프로젝트 업그레이드", "🆕 새 프로젝트 생성"],
        help="업그레이드는 기존 프로젝트를 개선하고, 새 프로젝트는 처음부터 생성합니다"
    )
    
    st.divider()
    
    if orchestrator_type == "🔧 기존 프로젝트 업그레이드":
        st.subheader("업그레이드 설정")
        
        # 프로젝트 경로
        project_path = st.text_input(
            "프로젝트 경로",
            value=os.path.expanduser("~/my-project"),
            help="업그레이드할 프로젝트의 절대 경로"
        )
        
        # Evolution Loop 설정
        st.markdown("### 🔄 Evolution Loop")
        enable_evolution = st.checkbox(
            "Evolution Loop 활성화",
            value=True,
            help="갭이 0이 될 때까지 자동으로 개선을 반복합니다"
        )
        
        if enable_evolution:
            max_iterations = st.slider(
                "최대 반복 횟수",
                min_value=1,
                max_value=10,
                value=5,
                help="Evolution Loop의 최대 반복 횟수"
            )
            
            convergence_threshold = st.slider(
                "수렴 임계값 (%)",
                min_value=50,
                max_value=100,
                value=90,
                help="이 수준에 도달하면 루프를 종료합니다"
            )
        
        # AI 드리븐 설정
        st.markdown("### 🤖 AI 설정")
        ai_driven = st.checkbox(
            "AI-Driven Workflow",
            value=True,
            help="AI가 동적으로 에이전트 실행 순서를 결정합니다"
        )
        
        parallel_execution = st.checkbox(
            "병렬 실행 허용",
            value=True,
            help="독립적인 에이전트들을 병렬로 실행합니다"
        )
        
    else:  # 새 프로젝트 생성
        st.subheader("새 프로젝트 설정")
        
        # 프로젝트 정보
        project_name = st.text_input(
            "프로젝트 이름",
            value="my-new-project",
            help="생성할 프로젝트의 이름"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            project_type = st.selectbox(
                "프로젝트 타입",
                ["API", "Web App", "CLI Tool", "Library", "Microservice"],
                help="프로젝트의 유형"
            )
        
        with col2:
            language = st.selectbox(
                "프로그래밍 언어",
                ["Python", "JavaScript", "TypeScript", "Go", "Rust"],
                help="주 개발 언어"
            )
        
        framework = st.text_input(
            "프레임워크",
            value="FastAPI" if language == "Python" else "Express",
            help="사용할 프레임워크 (예: FastAPI, Express, Gin)"
        )
        
        # Evolution Loop 설정
        st.markdown("### 🔄 Evolution Loop")
        enable_evolution = st.checkbox(
            "Evolution Loop 활성화",
            value=True,
            help="초기 생성 후 자동으로 품질을 개선합니다"
        )
        
        if enable_evolution:
            max_iterations = st.slider(
                "최대 개선 횟수",
                min_value=1,
                max_value=5,
                value=3,
                help="초기 생성 후 개선 반복 횟수"
            )
        
        # 포함 옵션
        st.markdown("### 📦 포함 옵션")
        include_tests = st.checkbox("테스트 코드", value=True)
        include_docs = st.checkbox("문서화", value=True)
        include_docker = st.checkbox("Docker 설정", value=True)
        include_ci_cd = st.checkbox("CI/CD 파이프라인", value=True)
    
    # 출력 디렉토리
    st.divider()
    output_dir = st.text_input(
        "출력 디렉토리",
        value="/tmp/t-developer-output",
        help="결과물이 저장될 디렉토리"
    )

# 메인 영역
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 요구사항")
    
    # 예시 템플릿
    template = st.selectbox(
        "템플릿 선택 (선택사항)",
        ["직접 입력", "API 서버", "웹 애플리케이션", "데이터 파이프라인", "마이크로서비스"],
        help="미리 정의된 요구사항 템플릿을 사용할 수 있습니다"
    )
    
    if template == "API 서버":
        default_requirements = """RESTful API 서버 구현:
- 사용자 인증/인가 (JWT)
- CRUD 작업 지원
- 데이터베이스 연동 (PostgreSQL)
- API 문서 자동 생성 (OpenAPI)
- 레이트 리미팅
- 로깅 및 모니터링
- 단위 테스트 및 통합 테스트
- Docker 컨테이너화"""
    elif template == "웹 애플리케이션":
        default_requirements = """웹 애플리케이션 구현:
- 반응형 UI (모바일 지원)
- 사용자 계정 시스템
- 실시간 알림 (WebSocket)
- 파일 업로드/다운로드
- 검색 및 필터링
- 다국어 지원
- SEO 최적화
- 성능 최적화"""
    elif template == "데이터 파이프라인":
        default_requirements = """데이터 처리 파이프라인:
- 실시간 데이터 수집
- 데이터 검증 및 정제
- ETL/ELT 프로세스
- 배치 처리 지원
- 에러 핸들링 및 재시도
- 모니터링 대시보드
- 데이터 품질 체크
- 스케일링 지원"""
    elif template == "마이크로서비스":
        default_requirements = """마이크로서비스 아키텍처:
- 서비스 디스커버리
- API 게이트웨이
- 서비스 간 통신 (gRPC/REST)
- 분산 트레이싱
- 서킷 브레이커
- 컨테이너 오케스트레이션
- 헬스 체크
- 중앙 로깅"""
    else:
        default_requirements = ""
    
    requirements = st.text_area(
        "요구사항을 입력하세요",
        value=default_requirements,
        height=250,
        placeholder="예시:\n- 사용자 인증 기능 추가\n- REST API를 GraphQL로 마이그레이션\n- 성능 최적화 (응답시간 50% 개선)\n- 테스트 커버리지 80% 달성",
        help="자연어로 원하는 기능이나 개선사항을 설명하세요"
    )
    
    # 실행 버튼
    col_run, col_stop, col_clear = st.columns(3)
    with col_run:
        run_button = st.button(
            "🚀 실행",
            type="primary",
            disabled=st.session_state.running,
            help="오케스트레이터를 실행합니다"
        )
    with col_stop:
        stop_button = st.button(
            "🛑 중지",
            type="secondary",
            disabled=not st.session_state.running,
            help="실행 중인 작업을 중지합니다"
        )
    with col_clear:
        clear_button = st.button(
            "🗑️ 초기화",
            help="로그와 결과를 초기화합니다"
        )

with col2:
    st.header("📊 상태")
    
    # 상태 표시
    status_container = st.container()
    with status_container:
        if st.session_state.running:
            st.markdown('<p class="status-running">🔄 실행 중...</p>', unsafe_allow_html=True)
        elif st.session_state.result:
            if st.session_state.result.get('success'):
                st.markdown('<p class="status-success">✅ 완료</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="status-failed">❌ 실패</p>', unsafe_allow_html=True)
        else:
            st.markdown("⏸️ 대기 중")
    
    # 진행률
    if st.session_state.running:
        st.progress(0.5, "처리 중...")
    elif st.session_state.result:
        st.progress(1.0, "완료")
    else:
        st.progress(0.0)
    
    # 메트릭 표시
    st.divider()
    
    if st.session_state.result:
        if orchestrator_type == "🔧 기존 프로젝트 업그레이드":
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric(
                    "반복 횟수",
                    st.session_state.result.get('iterations', 0),
                    delta=None
                )
            with col_m2:
                st.metric(
                    "갭 스코어",
                    f"{st.session_state.result.get('gap_score', 0):.1%}",
                    delta=f"{st.session_state.result.get('gap_reduction', 0):.1%}"
                )
        else:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric(
                    "생성 파일",
                    st.session_state.result.get('files_created', 0)
                )
            with col_m2:
                st.metric(
                    "코드 라인",
                    st.session_state.result.get('lines_of_code', 0)
                )
    
    # 페르소나 정보
    st.divider()
    with st.expander("🎭 활성 페르소나"):
        if orchestrator_type == "🔧 기존 프로젝트 업그레이드":
            st.markdown("**진화 마에스트로**")
            st.caption("\"진화는 혁명보다 강하다\"")
        else:
            st.markdown("**창조 아키텍트**")
            st.caption("\"모든 위대한 시스템은 작은 씨앗에서 시작된다\"")

# 탭 구성
tab_log, tab_docs, tab_plan, tab_code = st.tabs(
    ["📜 실행 로그", "📄 생성 문서", "📋 실행 계획", "💻 생성 코드"]
)

with tab_log:
    # 로그 컨테이너
    log_container = st.container()
    with log_container:
        if st.session_state.logs:
            # 최근 로그를 역순으로 표시
            for log in reversed(st.session_state.logs[-50:]):  # 최근 50개만
                if "ERROR" in log or "실패" in log:
                    st.error(log)
                elif "WARNING" in log or "경고" in log:
                    st.warning(log)
                elif "SUCCESS" in log or "완료" in log:
                    st.success(log)
                else:
                    st.text(log)
        else:
            st.info("실행 로그가 여기에 표시됩니다")

with tab_docs:
    if st.session_state.documents:
        # 문서 테이블
        doc_data = []
        for agent_name, doc in st.session_state.documents.items():
            doc_data.append({
                "에이전트": agent_name,
                "문서 타입": doc.get("type", "unknown"),
                "생성 시간": doc.get("created_at", ""),
                "크기": f"{len(str(doc.get('content', '')))} chars"
            })
        
        if doc_data:
            df = pd.DataFrame(doc_data)
            st.dataframe(df, use_container_width=True)
            
            # 문서 상세 보기
            selected_agent = st.selectbox(
                "문서 상세 보기",
                list(st.session_state.documents.keys())
            )
            
            if selected_agent:
                doc = st.session_state.documents[selected_agent]
                st.json(doc.get("content", {}))
    else:
        st.info("생성된 문서가 여기에 표시됩니다")

with tab_plan:
    if st.session_state.result and 'plan' in st.session_state.result:
        plan = st.session_state.result['plan']
        
        # Phase별 계획 표시
        for phase in plan.get('phases', []):
            with st.expander(f"Phase {phase.get('number', '?')}: {phase.get('name', 'Unknown')}"):
                st.markdown(f"**목표**: {phase.get('goal', 'N/A')}")
                st.markdown(f"**예상 시간**: {phase.get('estimated_time', 'N/A')}")
                
                if 'tasks' in phase:
                    st.markdown("**태스크**:")
                    for task in phase['tasks']:
                        st.checkbox(
                            f"{task.get('name', 'Unknown')} ({task.get('duration', '?')}분)",
                            value=task.get('completed', False),
                            disabled=True
                        )
    else:
        st.info("실행 계획이 여기에 표시됩니다")

with tab_code:
    if st.session_state.result and 'generated_code' in st.session_state.result:
        code_files = st.session_state.result['generated_code']
        
        # 파일 선택
        if code_files:
            selected_file = st.selectbox(
                "파일 선택",
                list(code_files.keys())
            )
            
            if selected_file:
                code = code_files[selected_file]
                # 언어 감지
                if selected_file.endswith('.py'):
                    lang = 'python'
                elif selected_file.endswith(('.js', '.jsx')):
                    lang = 'javascript'
                elif selected_file.endswith(('.ts', '.tsx')):
                    lang = 'typescript'
                else:
                    lang = 'text'
                
                st.code(code, language=lang, line_numbers=True)
    else:
        st.info("생성된 코드가 여기에 표시됩니다")

# 다운로드 섹션
if st.session_state.result and st.session_state.documents:
    st.divider()
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        # 전체 문서 다운로드
        if st.button("📥 모든 문서 다운로드", type="secondary"):
            # ZIP 파일 생성
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # 모든 문서 추가
                for agent_name, doc in st.session_state.documents.items():
                    # JSON 형식으로 저장
                    doc_json = json.dumps(doc, indent=2, ensure_ascii=False)
                    zip_file.writestr(f"documents/{agent_name}.json", doc_json)
                
                # 요약 파일 추가
                summary = {
                    "timestamp": datetime.now().isoformat(),
                    "orchestrator": orchestrator_type,
                    "requirements": requirements,
                    "result": st.session_state.result,
                    "document_count": len(st.session_state.documents)
                }
                zip_file.writestr("summary.json", json.dumps(summary, indent=2, ensure_ascii=False))
            
            # 다운로드 버튼
            st.download_button(
                label="💾 ZIP 다운로드",
                data=zip_buffer.getvalue(),
                file_name=f"t-developer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
            )
    
    with col_dl2:
        # Markdown 보고서 다운로드
        if st.button("📝 Markdown 보고서", type="secondary"):
            # Markdown 생성
            md_content = f"""# T-Developer 실행 보고서

## 실행 정보
- **날짜**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **오케스트레이터**: {orchestrator_type}
- **상태**: {'성공' if st.session_state.result.get('success') else '실패'}

## 요구사항
```
{requirements}
```

## 실행 결과
{json.dumps(st.session_state.result, indent=2, ensure_ascii=False)}

## 생성된 문서
총 {len(st.session_state.documents)}개의 문서가 생성되었습니다.

### 문서 목록
"""
            for agent_name, doc in st.session_state.documents.items():
                md_content += f"- **{agent_name}**: {doc.get('type', 'unknown')} ({doc.get('created_at', '')})\n"
            
            # 다운로드 버튼
            st.download_button(
                label="💾 MD 다운로드",
                data=md_content,
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    
    with col_dl3:
        # 로그 다운로드
        if st.button("📋 실행 로그", type="secondary"):
            log_content = "\n".join(st.session_state.logs)
            
            st.download_button(
                label="💾 LOG 다운로드",
                data=log_content,
                file_name=f"execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                mime="text/plain"
            )

# 실행 함수
async def run_orchestrator():
    """오케스트레이터 실행"""
    st.session_state.running = True
    st.session_state.logs = []
    st.session_state.documents = {}
    
    def log(message):
        """로그 추가"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        st.session_state.logs.append(log_entry)
    
    try:
        if orchestrator_type == "🔧 기존 프로젝트 업그레이드":
            log("UpgradeOrchestrator 초기화 중...")
            
            config = UpgradeConfig(
                project_path=project_path,
                output_dir=output_dir,
                enable_evolution_loop=enable_evolution,
                max_evolution_iterations=max_iterations if enable_evolution else 1,
                ai_driven_workflow=ai_driven,
                allow_parallel_execution=parallel_execution
            )
            
            orchestrator = UpgradeOrchestrator(config)
            await orchestrator.initialize()
            
            log("✅ UpgradeOrchestrator 초기화 완료")
            log(f"📍 프로젝트: {project_path}")
            log(f"🔄 Evolution Loop: {'활성화' if enable_evolution else '비활성화'}")
            
            if enable_evolution:
                log("Evolution Loop 실행 중...")
                result = await orchestrator.execute_evolution_loop(requirements)
                
                st.session_state.result = {
                    'success': result.success,
                    'iterations': result.iterations,
                    'gap_score': result.convergence_rate,
                    'gap_reduction': 1.0 - result.convergence_rate
                }
            else:
                log("단일 분석 실행 중...")
                report = await orchestrator.analyze(requirements)
                
                st.session_state.result = {
                    'success': report.success,
                    'iterations': 1
                }
            
            # 문서 수집
            if orchestrator.document_context:
                st.session_state.documents = orchestrator.document_context.get_all_documents()
                log(f"📄 {len(st.session_state.documents)}개 문서 생성됨")
            
        else:  # 새 프로젝트 생성
            log("NewBuildOrchestrator 초기화 중...")
            
            config = NewBuildConfig(
                project_name=project_name,
                output_dir=output_dir,
                project_type=project_type.lower().replace(" ", "_"),
                language=language.lower(),
                framework=framework,
                enable_evolution_loop=enable_evolution,
                max_evolution_iterations=max_iterations if enable_evolution else 1,
                include_tests=include_tests,
                include_docs=include_docs,
                include_docker=include_docker,
                include_ci_cd=include_ci_cd
            )
            
            orchestrator = NewBuildOrchestrator(config)
            await orchestrator.initialize()
            
            log("✅ NewBuildOrchestrator 초기화 완료")
            log(f"🎯 프로젝트: {project_name}")
            log(f"💻 언어: {language} / 프레임워크: {framework}")
            
            log("프로젝트 생성 중...")
            report = await orchestrator.build(requirements)
            
            st.session_state.result = {
                'success': report.success,
                'files_created': len(report.files_created),
                'lines_of_code': report.code_generated.get('total_lines', 0) if report.code_generated else 0,
                'output_path': report.output_path
            }
            
            # 문서 수집
            if orchestrator.document_context:
                st.session_state.documents = orchestrator.document_context.get_all_documents()
                log(f"📄 {len(st.session_state.documents)}개 문서 생성됨")
            
            if report.success:
                log(f"✅ 프로젝트 생성 완료: {report.output_path}")
        
        log("🎉 실행 완료!")
        
    except Exception as e:
        log(f"❌ 오류 발생: {e}")
        st.session_state.result = {'success': False, 'error': str(e)}
        
    finally:
        st.session_state.running = False

# 버튼 이벤트 처리
if run_button:
    # 비동기 실행
    asyncio.run(run_orchestrator())
    st.rerun()

if stop_button:
    st.session_state.running = False
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 사용자가 실행을 중지했습니다")
    st.rerun()

if clear_button:
    st.session_state.logs = []
    st.session_state.result = None
    st.session_state.documents = {}
    st.rerun()

# 푸터
st.divider()
with st.expander("ℹ️ T-Developer v2.0 정보"):
    st.markdown("""
### 🚀 T-Developer - AI-Driven Autonomous Development System
    
**핵심 기능**
- 🤖 100% Real AI (AWS Bedrock Claude 3) - Mock/Fake 없음
- 🔄 Evolution Loop - 갭이 0이 될 때까지 자동 개선
- 📚 SharedDocumentContext - 모든 에이전트가 모든 문서 참조
- 🎯 Gap-driven Development - 목표 달성까지 지속적 진화
- 🎭 페르소나 시스템 - 각 에이전트의 일관된 전문성
    
**오케스트레이터**
1. **UpgradeOrchestrator** - 기존 프로젝트 업그레이드/디버깅/리팩토링
2. **NewBuildOrchestrator** - 새 프로젝트 생성 (SeedProduct)
    
**에이전트 (15개)**
- RequirementAnalyzer - 요구사항 분석
- StaticAnalyzer - 정적 코드 분석
- CodeAnalysisAgent - AI 기반 코드 분석
- BehaviorAnalyzer - 런타임 행동 분석
- ImpactAnalyzer - 변경 영향도 분석
- QualityGate - 품질 검증
- ExternalResearcher - 외부 지식 조사
- GapAnalyzer - 현재-목표 갭 분석
- SystemArchitect - 시스템 아키텍처 설계
- OrchestratorDesigner - 오케스트레이션 설계
- PlannerAgent - 실행 계획 수립
- TaskCreatorAgent - 세부 작업 생성
- CodeGenerator - 코드 자동 생성
- TestAgent - 테스트 실행 및 분석
- AgnoManager - 에이전트 자동 생성
    
**특징**
- AI-Driven Dynamic Workflow - AI가 실행 순서 결정
- 병렬 실행 지원 - 독립적 에이전트 동시 실행
- 자동 테스트 - 코드 생성 후 자동 검증
- 완벽한 문서화 - 모든 과정 문서화
    
---
Version: 2.0.0 | AWS Agent Squad Framework | Bedrock Runtime
    """)

# 자동 새로고침 (실행 중일 때)
if st.session_state.running:
    import time
    time.sleep(2)
    st.rerun()