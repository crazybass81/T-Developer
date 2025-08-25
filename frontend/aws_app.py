"""T-Developer AWS Agent Squad 기반 테스트 UI.

AWS Agent Squad 프레임워크와 Bedrock AgentCore를 사용하는
T-Developer v2.0의 테스트 인터페이스입니다.

주요 기능:
1. 대상 프로젝트 폴더 경로 선택
2. 요구사항 입력 (템플릿 지원)
3. 오케스트레이터 선택 (Upgrade/NewBuilder)
4. 실시간 진행 상황 표시
5. Evolution Loop 모니터링
6. 생성된 문서 다운로드 (ZIP, Markdown, Log)
7. 페르소나 정보 표시
8. 메트릭 대시보드
"""

import streamlit as st
import asyncio
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
import sys
import os

# T-Developer 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

# AWS Agent Squad 오케스트레이터
from backend.packages.orchestrator.aws_upgrade_orchestrator import (
    AWSUpgradeOrchestrator,
    AWSUpgradeConfig
)
from backend.packages.orchestrator.aws_newbuilder_orchestrator import (
    AWSNewBuilderOrchestrator,
    AWSNewBuilderConfig,
    SeedProductConfig
)

# 페르소나
from backend.packages.agents.personas import get_all_personas

# Streamlit 페이지 설정
st.set_page_config(
    page_title="T-Developer v2.0 AWS Agent Squad",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF9900;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #232F3E 0%, #37475A 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .evolution-box {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF9900;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .persona-card {
        background: #f8f9fa;
        padding: 0.8rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    .aws-badge {
        background: #FF9900;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<h1 class="main-header">🚀 T-Developer v2.0 - AWS Agent Squad</h1>', unsafe_allow_html=True)

# 세션 상태 초기화
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []

# 사이드바 - 설정
with st.sidebar:
    st.markdown("## ⚙️ 설정")
    st.markdown('<span class="aws-badge">AWS Bedrock Powered</span>', unsafe_allow_html=True)
    
    # 오케스트레이터 선택
    st.markdown("### 🎯 오케스트레이터 선택")
    orchestrator_type = st.radio(
        "실행할 오케스트레이터",
        ["UpgradeOrchestrator", "NewBuilderOrchestrator"],
        help="UpgradeOrchestrator: 기존 프로젝트 업그레이드\nNewBuilderOrchestrator: 새 프로젝트 생성"
    )
    
    # 프로젝트 설정
    st.markdown("### 📁 프로젝트 설정")
    
    if orchestrator_type == "UpgradeOrchestrator":
        project_path = st.text_input(
            "대상 프로젝트 경로",
            value="/home/ec2-user/T-Developer",
            help="업그레이드할 프로젝트의 절대 경로"
        )
    else:
        project_name = st.text_input(
            "프로젝트 이름",
            value="my-seed-project",
            help="생성할 프로젝트 이름"
        )
        
        # SeedProduct 설정
        st.markdown("#### 🌱 SeedProduct 설정")
        project_type = st.selectbox(
            "프로젝트 타입",
            ["api", "web", "cli", "library", "microservice"]
        )
        
        language = st.selectbox(
            "프로그래밍 언어",
            ["python", "javascript", "go", "rust", "java"]
        )
        
        framework = st.text_input(
            "프레임워크 (선택사항)",
            value="fastapi" if language == "python" else "",
            help="예: fastapi, express, gin, actix, spring"
        )
        
        architecture_pattern = st.selectbox(
            "아키텍처 패턴",
            ["clean", "hexagonal", "layered", "mvc"]
        )
    
    output_dir = st.text_input(
        "출력 디렉토리",
        value="/tmp/t-developer-output",
        help="결과물이 저장될 디렉토리"
    )
    
    # Evolution Loop 설정
    st.markdown("### 🔄 Evolution Loop")
    enable_evolution = st.checkbox("Evolution Loop 활성화", value=True)
    
    if enable_evolution:
        max_iterations = st.slider(
            "최대 반복 횟수",
            min_value=1,
            max_value=20,
            value=10
        )
        
        convergence_threshold = st.slider(
            "수렴 임계값",
            min_value=0.5,
            max_value=1.0,
            value=0.95,
            step=0.05,
            help="갭이 이 값 이하가 되면 수렴으로 판단"
        )
    
    # AI 설정
    st.markdown("### 🤖 AI 설정")
    ai_driven = st.checkbox("AI-Driven 워크플로우", value=True)
    
    temperature = st.slider(
        "창의성 (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.7 if orchestrator_type == "UpgradeOrchestrator" else 0.8,
        step=0.1
    )
    
    # 페르소나 설정
    st.markdown("### 🎭 페르소나")
    enable_personas = st.checkbox("페르소나 시스템 활성화", value=True)
    
    if enable_personas:
        if st.button("페르소나 목록 보기"):
            st.session_state.show_personas = True

# 메인 영역
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 📝 요구사항 입력")
    
    # 템플릿 선택
    template = st.selectbox(
        "템플릿 선택",
        [
            "직접 입력",
            "GraphQL API 마이그레이션",
            "마이크로서비스 아키텍처 전환",
            "성능 최적화",
            "보안 강화",
            "테스트 커버리지 개선",
            "E-commerce API 생성",
            "실시간 채팅 시스템",
            "데이터 파이프라인"
        ]
    )
    
    # 템플릿별 기본 요구사항
    templates = {
        "GraphQL API 마이그레이션": "기존 REST API를 GraphQL로 마이그레이션하고 성능을 50% 개선하세요.",
        "마이크로서비스 아키텍처 전환": "모놀리식 애플리케이션을 마이크로서비스 아키텍처로 전환하세요.",
        "성능 최적화": "응답 시간을 30% 단축하고 처리량을 2배 증가시키세요.",
        "보안 강화": "OWASP Top 10 취약점을 모두 해결하고 보안 모니터링을 구현하세요.",
        "테스트 커버리지 개선": "테스트 커버리지를 90% 이상으로 높이고 CI/CD 파이프라인을 구축하세요.",
        "E-commerce API 생성": "상품 관리, 주문 처리, 결제 통합을 포함한 E-commerce API를 생성하세요.",
        "실시간 채팅 시스템": "WebSocket 기반 실시간 채팅 시스템을 구현하세요.",
        "데이터 파이프라인": "실시간 데이터 수집, 처리, 분석 파이프라인을 구축하세요."
    }
    
    default_req = templates.get(template, "")
    
    requirements = st.text_area(
        "요구사항 설명",
        value=default_req,
        height=150,
        help="프로젝트에 대한 요구사항을 자세히 입력하세요"
    )
    
    # 실행 버튼
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        start_button = st.button(
            "🚀 실행",
            disabled=st.session_state.is_running,
            type="primary",
            use_container_width=True
        )
    
    with col_btn2:
        stop_button = st.button(
            "⏹️ 중지",
            disabled=not st.session_state.is_running,
            use_container_width=True
        )
    
    with col_btn3:
        clear_button = st.button(
            "🗑️ 초기화",
            use_container_width=True
        )

with col2:
    st.markdown("## 📊 실시간 메트릭")
    
    if st.session_state.orchestrator:
        # 메트릭 카드
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if hasattr(st.session_state.orchestrator, 'get_iteration_count'):
                iteration = st.session_state.orchestrator.get_iteration_count()
            else:
                iteration = 0
            st.metric("반복 횟수", iteration)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with metric_col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if hasattr(st.session_state.orchestrator, 'get_gap_score'):
                gap = st.session_state.orchestrator.get_gap_score()
            else:
                gap = 1.0
            st.metric("갭 스코어", f"{gap:.2%}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Evolution Loop 상태
        if enable_evolution:
            st.markdown("### 🔄 Evolution Loop")
            progress = 1.0 - gap if gap < 1.0 else 0.0
            st.progress(progress)
            
            if gap <= (1 - convergence_threshold):
                st.success("✅ 수렴 달성!")
            else:
                st.info(f"목표: 갭 ≤ {(1-convergence_threshold):.2%}")
    
    # 실행 상태
    st.markdown("### 📡 실행 상태")
    if st.session_state.is_running:
        st.warning("🔄 실행 중...")
    elif st.session_state.results:
        if st.session_state.results.get('success') or st.session_state.results.get('converged'):
            st.success("✅ 완료!")
        else:
            st.info("⏸️ 실행 완료 (미수렴)")
    else:
        st.info("⏸️ 대기 중")

# 진행 상황 표시
st.markdown("## 📜 실행 로그")

log_container = st.container()
with log_container:
    if st.session_state.logs:
        log_text = "\n".join(st.session_state.logs[-50:])  # 최근 50개 로그
        st.code(log_text, language="text")
    else:
        st.info("실행 버튼을 눌러 시작하세요")

# 실행 함수
async def run_orchestrator():
    """오케스트레이터 실행."""
    st.session_state.is_running = True
    st.session_state.logs = []
    st.session_state.results = None
    
    try:
        if orchestrator_type == "UpgradeOrchestrator":
            # UpgradeOrchestrator 설정
            config = AWSUpgradeConfig(
                project_path=project_path,
                output_dir=output_dir,
                enable_evolution_loop=enable_evolution,
                max_evolution_iterations=max_iterations if enable_evolution else 1,
                convergence_threshold=convergence_threshold if enable_evolution else 0.95,
                ai_driven_workflow=ai_driven,
                temperature=temperature,
                enable_personas=enable_personas
            )
            
            # 오케스트레이터 생성
            orchestrator = AWSUpgradeOrchestrator(config)
            st.session_state.orchestrator = orchestrator
            
            # Evolution Loop 실행
            if enable_evolution:
                result = await orchestrator.execute_evolution_loop(requirements)
            else:
                result = await orchestrator.execute_ai_driven(requirements)
            
        else:
            # NewBuilderOrchestrator 설정
            seed_config = SeedProductConfig(
                name=project_name,
                type=project_type,
                language=language,
                framework=framework if framework else None,
                architecture_pattern=architecture_pattern
            )
            
            config = AWSNewBuilderConfig(
                project_name=project_name,
                output_dir=output_dir,
                seed_config=seed_config,
                enable_evolution_loop=enable_evolution,
                max_evolution_iterations=max_iterations if enable_evolution else 1,
                convergence_threshold=convergence_threshold if enable_evolution else 0.95,
                ai_driven_workflow=ai_driven,
                temperature=temperature,
                enable_personas=enable_personas
            )
            
            # 오케스트레이터 생성
            orchestrator = AWSNewBuilderOrchestrator(config)
            st.session_state.orchestrator = orchestrator
            
            # SeedProduct 생성
            result = await orchestrator.create_seed_product(requirements)
        
        st.session_state.results = result
        st.session_state.logs.append(f"✅ 실행 완료: {datetime.now().isoformat()}")
        
    except Exception as e:
        st.session_state.logs.append(f"❌ 오류 발생: {str(e)}")
        st.error(f"실행 중 오류 발생: {str(e)}")
    
    finally:
        st.session_state.is_running = False

# 버튼 이벤트 처리
if start_button and not st.session_state.is_running:
    if requirements:
        st.session_state.logs.append(f"🚀 실행 시작: {datetime.now().isoformat()}")
        st.session_state.logs.append(f"📋 오케스트레이터: {orchestrator_type}")
        st.session_state.logs.append(f"📝 요구사항: {requirements[:100]}...")
        
        # 비동기 실행
        asyncio.run(run_orchestrator())
    else:
        st.error("요구사항을 입력하세요")

if stop_button and st.session_state.is_running:
    st.session_state.is_running = False
    st.session_state.logs.append(f"⏹️ 사용자에 의해 중지됨: {datetime.now().isoformat()}")

if clear_button:
    st.session_state.orchestrator = None
    st.session_state.results = None
    st.session_state.is_running = False
    st.session_state.logs = []
    st.rerun()

# 결과 표시
if st.session_state.results:
    st.markdown("## 📊 실행 결과")
    
    # 결과 요약
    col_res1, col_res2, col_res3 = st.columns(3)
    
    with col_res1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if 'iterations' in st.session_state.results:
            st.metric("총 반복 횟수", st.session_state.results.get('iterations', 0))
        elif 'total_iterations' in st.session_state.results:
            st.metric("총 반복 횟수", st.session_state.results.get('total_iterations', 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_res2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        final_gap = st.session_state.results.get('final_gap_score', 1.0)
        st.metric("최종 갭 스코어", f"{final_gap:.2%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_res3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        converged = st.session_state.results.get('converged', False)
        st.metric("수렴 여부", "✅ 성공" if converged else "⏸️ 미수렴")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 문서 다운로드
    st.markdown("### 📥 문서 다운로드")
    
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        # JSON 다운로드
        json_str = json.dumps(st.session_state.results, indent=2, ensure_ascii=False, default=str)
        st.download_button(
            label="📄 JSON 다운로드",
            data=json_str,
            file_name=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col_dl2:
        # Markdown 보고서 생성
        md_report = f"""# T-Developer 실행 보고서

## 실행 정보
- 오케스트레이터: {orchestrator_type}
- 실행 시간: {datetime.now().isoformat()}
- Evolution Loop: {'활성화' if enable_evolution else '비활성화'}

## 요구사항
{requirements}

## 결과 요약
- 총 반복 횟수: {st.session_state.results.get('iterations', st.session_state.results.get('total_iterations', 0))}
- 최종 갭 스코어: {st.session_state.results.get('final_gap_score', 1.0):.2%}
- 수렴 여부: {'성공' if st.session_state.results.get('converged', False) else '미수렴'}

## 상세 결과
```json
{json.dumps(st.session_state.results, indent=2, ensure_ascii=False, default=str)}
```
"""
        st.download_button(
            label="📝 Markdown 다운로드",
            data=md_report,
            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col_dl3:
        # 로그 다운로드
        log_text = "\n".join(st.session_state.logs)
        st.download_button(
            label="📜 로그 다운로드",
            data=log_text,
            file_name=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# 페르소나 정보 표시
if st.session_state.get('show_personas', False):
    with st.expander("🎭 페르소나 목록", expanded=True):
        personas = get_all_personas()
        
        for name, persona in personas.items():
            st.markdown(f'<div class="persona-card">', unsafe_allow_html=True)
            st.markdown(f"**{name}**")
            st.markdown(f"- 이름: {persona.name}")
            st.markdown(f"- 역할: {persona.role}")
            st.markdown(f"- 캐치프레이즈: *\"{persona.catchphrase}\"*")
            st.markdown('</div>', unsafe_allow_html=True)

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    🤖 T-Developer v2.0 - AWS Agent Squad Framework<br>
    Powered by AWS Bedrock & Claude 3 Sonnet<br>
    © 2025 T-Developer Team
</div>
""", unsafe_allow_html=True)