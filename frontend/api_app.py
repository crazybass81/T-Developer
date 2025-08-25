"""T-Developer API 기반 UI - FastAPI 백엔드와 연동

백엔드 API 서버와 통신하는 Streamlit UI입니다.
API 서버가 먼저 실행되어 있어야 합니다.
"""

import streamlit as st
import requests
import json
import time
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
import pandas as pd

# API 서버 URL
API_URL = "http://localhost:8000"

# 페이지 설정
st.set_page_config(
    page_title="T-Developer API Client",
    page_icon="🚀",
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
    .status-box {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF9900;
        margin: 1rem 0;
    }
    .api-status {
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .api-online {
        background: #d4edda;
        color: #155724;
    }
    .api-offline {
        background: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<h1 class="main-header">🚀 T-Developer v2.0 - API Client</h1>', unsafe_allow_html=True)

# API 연결 상태 확인
def check_api_status():
    """API 서버 상태 확인"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# 업그레이드 요청
def request_upgrade(requirements, project_path, config):
    """업그레이드 요청 전송"""
    try:
        payload = {
            "requirements": requirements,
            "project_path": project_path,
            "orchestrator_type": config.get("orchestrator_type", "upgrade"),
            "enable_dynamic_analysis": config.get("enable_dynamic_analysis", False),
            "include_behavior_analysis": config.get("include_behavior_analysis", True),
            "generate_impact_matrix": config.get("generate_impact_matrix", True)
        }
        
        response = requests.post(
            f"{API_URL}/upgrade",
            json=payload,
            timeout=60  # 60초로 증가
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API 오류: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
        return None
    except Exception as e:
        st.error(f"요청 실패: {str(e)}")
        return None

# 작업 상태 확인
def get_task_status(task_id):
    """작업 상태 조회"""
    try:
        response = requests.get(
            f"{API_URL}/status/{task_id}",
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# 결과 다운로드
def download_result(task_id):
    """작업 결과 다운로드"""
    try:
        response = requests.get(
            f"{API_URL}/result/{task_id}",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# 사이드바
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API 상태
    api_online = check_api_status()
    if api_online:
        st.markdown('<div class="api-status api-online">✅ API 서버 연결됨</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-status api-offline">❌ API 서버 오프라인</div>', unsafe_allow_html=True)
        st.info("백엔드 서버를 먼저 실행해주세요:")
        st.code("python3 -m uvicorn backend.api.upgrade_api:app --reload", language="bash")
    
    st.divider()
    
    # 오케스트레이터 선택
    st.subheader("🎯 오케스트레이터 선택")
    orchestrator_type = st.radio(
        "작업 유형",
        ["upgrade", "newbuild"],
        format_func=lambda x: "🔧 기존 프로젝트 업그레이드" if x == "upgrade" else "🆕 새 프로젝트 생성",
        help="**Upgrade**: 기존 프로젝트 개선\n**NewBuild**: 빈 폴더에 새 프로젝트 생성"
    )
    
    # 프로젝트 경로
    if orchestrator_type == "newbuild":
        project_path = st.text_input(
            "📁 새 프로젝트 경로",
            value="/home/ec2-user/new-project",
            help="⚠️ 빈 폴더 경로 입력 (없으면 자동 생성)"
        )
        st.info("💡 빈 폴더에 SeedProduct를 생성합니다")
    else:
        project_path = st.text_input(
            "📁 기존 프로젝트 경로",
            value="/home/ec2-user/my-project",
            help="업그레이드할 기존 프로젝트의 경로"
        )
    
    # 설정 옵션 (Upgrade만)
    if orchestrator_type == "upgrade":
        st.subheader("🔧 분석 옵션")
        enable_dynamic = st.checkbox("동적 분석 활성화", value=False)
        include_behavior = st.checkbox("행동 분석 포함", value=True)
        generate_impact = st.checkbox("영향도 매트릭스 생성", value=True)
    else:
        enable_dynamic = False
        include_behavior = False
        generate_impact = False
    
    config = {
        "orchestrator_type": orchestrator_type,
        "enable_dynamic_analysis": enable_dynamic,
        "include_behavior_analysis": include_behavior,
        "generate_impact_matrix": generate_impact
    }

# 메인 컨텐츠
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 요구사항 입력")
    
    # 템플릿 선택
    template = st.selectbox(
        "템플릿 선택 (선택사항)",
        ["직접 입력", "성능 개선", "보안 강화", "리팩터링", "버그 수정", "기능 추가"]
    )
    
    # 템플릿별 기본 텍스트
    templates = {
        "성능 개선": "이 프로젝트의 성능을 분석하고 병목 지점을 찾아 최적화하세요. 응답 시간을 50% 개선하는 것이 목표입니다.",
        "보안 강화": "보안 취약점을 스캔하고 OWASP Top 10에 대한 방어를 구현하세요. 모든 입력 검증과 인증/인가를 강화하세요.",
        "리팩터링": "코드 품질을 개선하고 SOLID 원칙을 적용하세요. 중복 코드를 제거하고 테스트 커버리지를 80% 이상으로 높이세요.",
        "버그 수정": "알려진 버그들을 수정하고 엣지 케이스를 처리하세요. 에러 핸들링을 개선하고 로깅을 강화하세요.",
        "기능 추가": "새로운 기능을 추가하세요: "
    }
    
    default_text = templates.get(template, "")
    
    # 요구사항 입력
    requirements = st.text_area(
        "자연어 요구사항",
        value=default_text,
        height=200,
        placeholder="예: GraphQL API로 마이그레이션하고 성능을 50% 개선하세요"
    )

with col2:
    st.header("🎯 실행 제어")
    
    # 실행 버튼
    button_text = "🚀 업그레이드 시작" if orchestrator_type == "upgrade" else "🆕 프로젝트 생성"
    if st.button(button_text, type="primary", disabled=not api_online):
        if not requirements:
            st.error("요구사항을 입력해주세요")
        elif orchestrator_type == "upgrade" and (not project_path or not Path(project_path).exists()):
            st.error("유효한 프로젝트 경로를 입력해주세요")
        elif not project_path:
            st.error("프로젝트 경로를 입력해주세요")
        else:
            # 업그레이드 요청
            with st.spinner("🔄 업그레이드 요청 중..."):
                result = request_upgrade(requirements, project_path, config)
                
                if result:
                    task_id = result.get("task_id")
                    st.success(f"✅ 작업 시작됨 - Task ID: {task_id}")
                    
                    # 진행 상황 모니터링
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    while True:
                        status = get_task_status(task_id)
                        if status:
                            progress = status.get("progress", 0)
                            progress_bar.progress(progress)
                            
                            current_phase = status.get("current_phase", "준비 중")
                            status_text.text(f"현재 단계: {current_phase}")
                            
                            if status.get("status") == "completed":
                                st.balloons()
                                st.success("🎉 업그레이드 완료!")
                                
                                # 결과 다운로드
                                result_data = download_result(task_id)
                                if result_data:
                                    st.json(result_data)
                                break
                            elif status.get("status") == "failed":
                                st.error(f"❌ 작업 실패: {status.get('message')}")
                                break
                        
                        time.sleep(2)
    
    # API 문서 링크
    if api_online:
        st.markdown("---")
        st.markdown("📚 [API 문서 보기](http://localhost:8000/docs)")

# 결과 표시 영역
st.header("📊 실행 결과")

result_tabs = st.tabs(["요약", "상세 로그", "생성된 문서", "메트릭"])

with result_tabs[0]:
    st.info("업그레이드를 실행하면 여기에 요약이 표시됩니다")

with result_tabs[1]:
    st.text_area("실행 로그", value="", height=400, disabled=True)

with result_tabs[2]:
    st.info("생성된 문서들이 여기에 표시됩니다")

with result_tabs[3]:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("분석된 파일", "0")
    with col2:
        st.metric("발견된 이슈", "0")
    with col3:
        st.metric("개선 제안", "0")
    with col4:
        st.metric("예상 영향도", "0%")

# 푸터
st.markdown("---")
st.markdown("🤖 **T-Developer v2.0** - AWS Agent Squad Framework | Evolution Loop Enabled")