"""T-Developer v2 Web Interface.

Streamlit UI for comprehensive project analysis and upgrade planning.
Features:
- Project path selection
- Requirements input
- Dependency-based analysis execution
- Results viewing and download
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import traceback

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator,
    UpgradeConfig,
    UpgradeReport
)
from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


# Page configuration
st.set_page_config(
    page_title="T-Developer v2",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "analysis_running" not in st.session_state:
    st.session_state.analysis_running = False
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []


async def run_upgrade_analysis(project_path: str, requirements: str, config_options: Dict[str, Any]) -> UpgradeReport:
    """Run comprehensive upgrade analysis."""
    config = UpgradeConfig(
        project_path=project_path,
        output_dir=config_options.get('output_dir', '/tmp/t-developer/reports'),
        enable_dynamic_analysis=config_options.get('enable_dynamic', False),
        include_behavior_analysis=config_options.get('include_behavior', True),
        generate_impact_matrix=config_options.get('generate_impact', True),
        generate_recommendations=config_options.get('generate_recommendations', True),
        safe_mode=config_options.get('safe_mode', True),
        parallel_analysis=config_options.get('parallel', True)
    )
    
    orchestrator = UpgradeOrchestrator(config)
    await orchestrator.initialize()
    
    # Run analysis with research
    report = await orchestrator.analyze(
        requirements=requirements,
        include_research=config_options.get('include_research', True)
    )
    
    return report


def format_task_status(tasks: list) -> str:
    """Format task breakdown for display."""
    
    if not tasks:
        return "No tasks defined"
    
    output = []
    for task in tasks:
        status_icon = "✅" if task.get('status') == 'completed' else "⏳"
        output.append(f"{status_icon} {task.get('name', 'Unknown')} ({task.get('duration', '?')}min)")
    return "\n".join(output)


# Main UI
def main():
    """Main Streamlit application."""
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🚀 T-Developer v2")
        st.markdown("**AI-Driven Software Upgrade Orchestrator**")
        st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Documentation")
        st.markdown("""
        ### How to use:
        1. Select your project directory
        2. Enter requirements
        3. Configure analysis options
        4. Click 'Run Analysis'
        5. View and download results
        
        ### Features:
        - 🔍 Comprehensive code analysis
        - 🤖 AI-driven recommendations
        - 📊 Dependency-based execution
        - 🎯 Gap analysis
        - 📈 Impact assessment
        - 🚀 Migration planning
        """)
        
        st.markdown("---")
        st.markdown("**Version:** 2.0.0")
        st.markdown("**Status:** Production Ready")
    
    # Project Selection Section
    st.header("📁 Project Selection")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Project path input - T-Developer-TEST로 고정
        default_project_path = "/home/ec2-user/T-Developer-TEST"
        if not Path(default_project_path).exists():
            # T-Developer-TEST가 없으면 현재 디렉토리 사용
            default_project_path = os.getcwd()
        
        project_path = st.text_input(
            "Project Path",
            value=st.session_state.selected_project or default_project_path,
            help="Enter the absolute path to your project directory (Default: T-Developer-TEST)"
        )
        
        # Validate path
        if project_path:
            path = Path(project_path)
            if path.exists() and path.is_dir():
                st.success(f"✅ Valid project path: {path.name}")
                st.session_state.selected_project = str(path)
                
                # Show project info
                try:
                    py_files = list(path.glob("**/*.py"))[:100]
                    st.info(f"📊 Found {len(py_files)} Python files")
                except:
                    pass
            else:
                st.error("❌ Invalid path or directory does not exist")
    
    with col2:
        # Quick select buttons
        st.markdown("**Quick Select:**")
        if st.button("Current Directory"):
            st.session_state.selected_project = os.getcwd()
            st.rerun()
        if st.button("Backend Directory"):
            backend_path = Path(__file__).parent.parent / "backend"
            if backend_path.exists():
                st.session_state.selected_project = str(backend_path)
                st.rerun()
        
    # Requirements Section
    if st.session_state.selected_project:
        st.header("📝 Requirements Input")
        
        # Templates
        templates = {
            "테스트 커버리지 개선": """현재 시스템의 테스트 커버리지를 분석하고 80% 이상으로 개선해주세요.
특히 다음 사항에 집중해주세요:
1. 단위 테스트 추가
2. 통합 테스트 구현
3. 엣지 케이스 처리""",
            
            "성능 최적화": """시스템 성능을 분석하고 최적화해주세요.
목표:
- 응답 시간 50% 감소
- 메모리 사용량 30% 감소
- 동시 처리량 2배 향상""",
            
            "보안 강화": """보안 취약점을 분석하고 개선해주세요.
- OWASP Top 10 체크
- 의존성 취약점 패치
- 보안 베스트 프랙티스 적용""",
            
            "코드 품질 개선": """코드 품질을 분석하고 개선해주세요.
- 복잡도 감소 (Cyclomatic Complexity < 10)
- 코드 중복 제거
- SOLID 원칙 적용
- 디자인 패턴 적용""",
            
            "UpgradeOrchestrator 완성": """T-Developer의 여러가지 오케스트레이터 중 UpgradeOrchestrator를 중점적으로 완성한다.

## UpgradeOrchestrator의 세부사항
1. 개발중인 대상프로젝트를 요청에 따라 업그레이드/디버깅/리팩터링을 수행하는 UpgradeOrchestrator를 완성한다.
2. 정해진 기본 호출 순서에 따라 작업수행 하는 것을 원칙으로 하지만 요청사항에 따라 호출하는 에이전트의 종류나 순서를 변경할 수 있는 AI드리븐 오케스트레이터이다.
3. 기본 호출순서는 요청사항 분석에이전트(요청사항을 파싱,분석해서 문서화) - 대상프로젝트의 현재상태를 분석하는 에이전트 (행동, 임팩트, 정적, 품질, ai동적, 각각의 문서를 작성하고 하나의 통합문서로 종합) - 외부리서치 에이전트(현재상태를 베이스로 요청사항을 달성하는데에 도움이 될 수 있는 최신기술, 코드레퍼런스등 각종 외부자료 조사 후 문서화) - 갭분석 에이전트(현재상태를 베이스로 요청사항을 달성하기 위해 필요한 변경사항을 분석하고, 그 차이를 수치화) - 아키택트 에이전트 (오케스트레이터와 에이전트등 생성되는 에이전트 전체의 아키텍쳐를 설계하고 업그레이드시에는 기존 아키텍처의 수정/진화를 설계하고 문서화 하는 역할을 한다.) - 오케스트레이터 디자이너(아키택트 에이전트가 생성한 문서를 바탕으로 오케스트레이터와 필요한 에이전트를 디자인하고 문서화 한다.) - 계획수립 에이전트(아키텍처 문서와, 오케스트레이터, 에이전트 디자인 문서를 바탕으로 아그노와 코드제너레이터가 생성,수정해야하는 작업을 Phase 단위로 계획하고 문서화) - 세부임무계획 에이전트 (Phase 단위의 계획을 5-20분 작업시간 단위의 task로 구체화 하여 계획) - 아그노 & 코드제너레이터 에이전트 - 테스트 에이전트 - 현재상태를 분석하는 에이전트들로 돌아가 갭 에이전트가 현재의 상태가 목적의 상태와 일치하면 루프가 종료
4. ai가 방해가 되는 경우를 제외하고 ai드리븐 에이전트/오케스트레이터로 만든다.
5. 문서생성에이전트 : requirement_analyzer.py, behavior_analyzer.py, code_analysis.py, external_researcher.py, gap_analyzer.py, impact_analyzer.py, planner_agent.py, static_analyzer.py, task_creator_agent.py, quality_gate.py, 아키텍트에이전트, 오케스트레이터디자이너 에이전트
6. requirement레포트는 external_researcher.py, gap_analyzer.py가 참조한다.
7. behavior, code, impact, static, quality등 현재상태 분석레포트는 external_researcher.py, gap_analyzer.py가 참조한다.
8. external_research레포트는 gap_analyzer.py가 참조한다.
9. gap 분석레포트는 아키텍트 에이전트가 참조한다.
10. 아키텍처 디자인 문서는 오케스트레이터 디자인 에이전트가 참조한다.
11. 오케스트레이터 디자인 문서는 planner_agent.py, task_creator_agent.py가 참조한다.
12. planner, task_creator 레포트는 code_generator.py가 참조한다.
13. 참조원칙은 기본값이고, AI가 판단 후 필요에 의해 다른 문서를 참조할 수 있다.
14. 실행버튼을 눌러 생성된 모든 보고서와 계획을 MD파일도 다운받을 수 있도록 한다.
15. UI에서 프로젝트 경로는 T-Developer-TEST폴더로 하고 요청사항도 위 내용이 미리 입력되어 있도록 픽스하여 둔다 (추후변경)""",
            "Custom": ""
        }
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            template_choice = st.selectbox(
                "Choose Template",
                options=list(templates.keys()),
                index=0  # UpgradeOrchestrator 완성을 기본으로 선택
            )
        
        with col1:
            requirements = st.text_area(
                "Enter your requirements",
                value=templates[template_choice],
                height=200,
                help="Describe what you want to analyze and improve"
            )
    
        # Configuration Section
        st.header("⚙️ Analysis Configuration")
        
        col1, col2, col3 = st.columns(3)
        
        config = {}
        
        with col1:
            st.markdown("**Analysis Options**")
            config['parallel'] = st.checkbox("Parallel Analysis", value=True)
            config['include_research'] = st.checkbox("Include External Research", value=True)
            config['generate_recommendations'] = st.checkbox("Generate Recommendations", value=True)
        
        with col2:
            st.markdown("**Safety & Performance**")
            config['safe_mode'] = st.checkbox("Safe Mode", value=True)
            config['enable_dynamic'] = st.checkbox("Enable Dynamic Analysis", value=False)
            config['include_behavior'] = st.checkbox("Include Behavior Analysis", value=True)
        
        with col3:
            st.markdown("**Output Options**")
            config['generate_impact'] = st.checkbox("Generate Impact Matrix", value=True)
            config['output_dir'] = st.text_input(
                "Output Directory",
                value="/tmp/t-developer/reports"
            )
        
        # Run Analysis Button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
                if requirements and requirements.strip():
                    st.session_state.analysis_running = True
                    
                    # Progress indicators
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    try:
                        # Run analysis
                        with st.spinner("Running comprehensive analysis..."):
                            # Create async task
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            report = loop.run_until_complete(
                                run_upgrade_analysis(
                                    st.session_state.selected_project,
                                    requirements,
                                    config
                                )
                            )
                            
                            st.session_state.analysis_results = report
                            st.session_state.analysis_running = False
                
                            # Clear progress
                            progress_placeholder.empty()
                            status_placeholder.success("✅ Analysis completed successfully!")
                            
                            # Add to history
                            st.session_state.analysis_history.append({
                                "timestamp": datetime.now().isoformat(),
                                "path": st.session_state.selected_project,
                                "requirements": requirements,
                                "report": report
                            })
                            
                    except Exception as e:
                        st.session_state.analysis_running = False
                        status_placeholder.error(f"❌ Analysis failed: {str(e)}")
                        import traceback
                        st.error("Full error:")
                        st.code(traceback.format_exc())
                else:
                    st.warning("⚠️ Please enter requirements before running analysis")
    
    # Results Section
    if st.session_state.analysis_results and not st.session_state.analysis_running:
        display_results(st.session_state.analysis_results)
    
    # History section
    if st.session_state.analysis_history:
        st.divider()
        st.header("📜 Analysis History")
        
        for i, item in enumerate(reversed(st.session_state.analysis_history[-3:]), 1):
            with st.expander(f"Analysis {i} - {item['timestamp'][:19]}"):
                st.markdown(f"**Path:** `{item['path']}`")
                st.markdown(f"**Requirements:** {item['requirements'][:100]}...")
                if 'report' in item and item['report']:
                    report = item['report']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("System Health", f"{report.system_health_score:.1f}/100")
                    with col2:
                        st.metric("Upgrade Risk", f"{report.upgrade_risk_score:.1f}/100")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 1rem;'>
        <small>
        T-Developer v2.0.0 | Powered by AWS Bedrock & Claude AI<br>
        Build autonomous, self-evolving services with AI
        </small>
    </div>
    """, unsafe_allow_html=True)


def display_results(report: UpgradeReport):
    """Display analysis results."""
    st.header("📊 Analysis Results")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="System Health",
            value=f"{report.system_health_score:.1f}/100",
            delta=f"{report.system_health_score - 50:.1f}"
        )
    
    with col2:
        st.metric(
            label="Upgrade Risk",
            value=f"{report.upgrade_risk_score:.1f}/100",
            delta=f"{50 - report.upgrade_risk_score:.1f}"
        )
    
    with col3:
        st.metric(
            label="Total Issues",
            value=report.total_issues_found,
            delta=None
        )
    
    with col4:
        st.metric(
            label="Critical Issues",
            value=len(report.critical_issues),
            delta=None
        )
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Overview",
        "🎯 Current State",
        "🔍 Research",
        "📈 Gap Analysis"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📌 Immediate Actions")
            if report.immediate_actions:
                for action in report.immediate_actions:
                    st.markdown(f"• {action}")
            else:
                st.info("No immediate actions required")
        
        with col2:
            st.subheader("🎯 Short-term Goals")
            if report.short_term_goals:
                for goal in report.short_term_goals:
                    st.markdown(f"• {goal}")
            else:
                st.info("No short-term goals identified")
    
    with tab2:
        if report.current_state:
            display_current_state(report.current_state)
    
    with tab3:
        if report.research_pack:
            display_research(report.research_pack)
    
    with tab4:
        if report.gap_report:
            display_gap_analysis(report.gap_report)
    
    # Download section
    download_section(report)

def display_current_state(state):
    """현재 상태 표시."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Static Analysis")
        if state.static_analysis:
            static = state.static_analysis
            st.info(f"Total Files: {static.get('total_files', 0)}")
            st.info(f"Complexity Hotspots: {static.get('complexity_hotspots', 0)}")
    
    with col2:
        st.subheader("🔄 Dynamic Analysis")
        if state.dynamic_analysis:
            dynamic = state.dynamic_analysis
            if dynamic.get('execution_metrics'):
                metrics = dynamic['execution_metrics']
                st.info(f"Execution Groups: {metrics.get('execution_groups', 0)}")
                st.info(f"Analysis Time: {metrics.get('analysis_time', 0):.2f}s")

def display_research(research):
    """리서치 결과 표시."""
    st.info(research.one_line_conclusion)
    
    if research.recommended_approach:
        st.success(f"✅ {research.recommended_approach.get('name', 'N/A')}")

def display_gap_analysis(gap):
    """갭 분석 표시."""
    if gap.gaps:
        st.subheader("📊 Identified Gaps")
        for g in gap.gaps[:5]:
            priority = g.get('priority', 'medium')
            priority_color = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(priority, '⚪')
            st.markdown(f"{priority_color} **{g.get('description', 'N/A')}**")

def download_section(report):
    """다운로드 섹션."""
    st.markdown("---")
    st.subheader("💾 Download Reports")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # JSON export
        json_str = json.dumps(report.__dict__, default=str, indent=2)
        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"t_developer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Markdown export
        if st.button("📝 Download All MD Files", use_container_width=True):
            st.info("📦 MD files have been saved to: " + report.__dict__.get('output_dir', '/tmp/t-developer/reports'))
            # Show individual MD files available
            project_name = Path(report.project_path).name
            timestamp = report.timestamp.replace(':', '-').replace('.', '-')
            output_dir = Path("/tmp/t-developer/reports") / project_name / timestamp
            
            if output_dir.exists():
                md_files = list(output_dir.glob("*.md"))
                if md_files:
                    st.success(f"✅ Found {len(md_files)} MD files")
                    for md_file in sorted(md_files):
                        st.text(f"  • {md_file.name}")
                else:
                    st.warning("⚠️ No MD files found")
    
    with col3:
        # HTML export (if needed)
        st.button("🌐 Export as HTML", use_container_width=True, disabled=True, help="Coming soon")
    
    with col4:
        # PDF export (if needed)
        st.button("📕 Export as PDF", use_container_width=True, disabled=True, help="Coming soon")

if __name__ == "__main__":
    main()