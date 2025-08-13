#!/usr/bin/env python3
"""
T-Developer Complete Service
완벽한 오케스트레이터와 9개 에이전트의 실제 통합
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 실제 Python 에이전트들 import (unified 경로에서)
from agents.unified.nl_input.agent import NLInputAgent
from agents.unified.ui_selection.agent import UISelectionAgent
from agents.unified.parser.agent import ParserAgent
from agents.unified.component_decision.agent import ComponentDecisionAgent
from agents.unified.match_rate.agent import MatchRateAgent
from agents.unified.search.agent import SearchAgent
from agents.unified.generation.agent import GenerationAgent
from agents.unified.assembly.agent import AssemblyAgent
from agents.unified.download.agent import DownloadAgent


class CompleteOrchestrator:
    """
    실제 작동하는 완전한 오케스트레이터
    9개의 프로덕션 에이전트를 지휘
    """

    def __init__(self):
        """오케스트레이터 초기화 - 실제 에이전트 인스턴스 생성"""
        logger.info("🎭 Master Orchestrator 초기화 시작...")

        # 실제 프로덕션 에이전트 인스턴스 생성
        self.agents = {
            "nl_input": NLInputAgent(),
            "ui_selection": UISelectionAgent(),
            "parser": ParserAgent(),
            "component_decision": ComponentDecisionAgent(),
            "match_rate": MatchRateAgent(),
            "search": SearchAgent(),
            "generation": GenerationAgent(),
            "assembly": AssemblyAgent(),
            "download": DownloadAgent(),
        }

        # 실행 순서 정의
        self.execution_order = [
            "nl_input",
            "ui_selection",
            "parser",
            "component_decision",
            "match_rate",
            "search",
            "generation",
            "assembly",
            "download",
        ]

        logger.info(f"✅ {len(self.agents)}개 프로덕션 에이전트 로드 완료")

    async def execute_pipeline(self, user_input: str) -> Dict[str, Any]:
        """
        완전한 9-에이전트 파이프라인 실행
        각 에이전트가 실제 작업을 수행하고 결과를 다음 에이전트로 전달
        """

        logger.info("=" * 60)
        logger.info("🚀 T-DEVELOPER COMPLETE PIPELINE 시작")
        logger.info(f"📝 User Input: {user_input}")
        logger.info("=" * 60)

        start_time = time.time()
        pipeline_data = {"user_input": user_input}
        results = {}

        try:
            for i, agent_name in enumerate(self.execution_order, 1):
                logger.info(f"\n🔄 Stage {i}/9: {agent_name.upper()}")
                stage_start = time.time()

                agent = self.agents[agent_name]

                # 에이전트 실행
                if agent_name == "nl_input":
                    result = await self._execute_nl_input(agent, pipeline_data)
                elif agent_name == "ui_selection":
                    result = await self._execute_ui_selection(agent, pipeline_data)
                elif agent_name == "parser":
                    result = await self._execute_parser(agent, pipeline_data)
                elif agent_name == "component_decision":
                    result = await self._execute_component_decision(
                        agent, pipeline_data
                    )
                elif agent_name == "match_rate":
                    result = await self._execute_match_rate(agent, pipeline_data)
                elif agent_name == "search":
                    result = await self._execute_search(agent, pipeline_data)
                elif agent_name == "generation":
                    result = await self._execute_generation(agent, pipeline_data)
                elif agent_name == "assembly":
                    result = await self._execute_assembly(agent, pipeline_data)
                elif agent_name == "download":
                    result = await self._execute_download(agent, pipeline_data)

                # 결과 저장 및 파이프라인 데이터 업데이트
                results[agent_name] = result
                pipeline_data.update(result)

                stage_time = time.time() - stage_start
                logger.info(f"   ✅ {agent_name} 완료 ({stage_time:.2f}초)")

                # 주요 결과 출력
                self._log_stage_results(agent_name, result)

        except Exception as e:
            logger.error(f"❌ Pipeline 실행 중 오류: {str(e)}")
            raise

        total_time = time.time() - start_time

        logger.info("\n" + "=" * 60)
        logger.info("📊 PIPELINE 실행 완료")
        logger.info(f"⏱️  총 실행 시간: {total_time:.2f}초")
        logger.info(f"✅ 성공한 스테이지: {len(results)}/9")
        logger.info("=" * 60)

        return {
            "success": True,
            "execution_time": total_time,
            "stages_completed": len(results),
            "results": results,
            "final_output": {
                "generated_files": pipeline_data.get("generated_files", 0),
                "lines_of_code": pipeline_data.get("lines_of_code", 0),
                "download_url": pipeline_data.get("download_url", ""),
                "project_path": pipeline_data.get("project_path", ""),
            },
        }

    async def _execute_nl_input(self, agent, data: Dict) -> Dict[str, Any]:
        """NL Input Agent 실행"""
        query = data.get("user_input", "")

        # 실제 NLP 처리
        requirements = agent.extract_requirements(query)
        intent = agent.identify_intent(query)
        entities = agent.extract_entities(query)

        return {
            "requirements": requirements,
            "intent": intent,
            "entities": entities,
            "complexity": agent.assess_complexity(requirements),
        }

    async def _execute_ui_selection(self, agent, data: Dict) -> Dict[str, Any]:
        """UI Selection Agent 실행"""
        requirements = data.get("requirements", [])

        # 실제 프레임워크 선택 로직
        framework = agent.select_framework(requirements)
        components = agent.identify_components(requirements, framework)

        return {
            "framework": framework,
            "components": components,
            "ui_library": agent.select_ui_library(framework),
            "styling": agent.select_styling_approach(framework),
        }

    async def _execute_parser(self, agent, data: Dict) -> Dict[str, Any]:
        """Parser Agent 실행"""
        framework = data.get("framework", "react")
        components = data.get("components", [])

        # 실제 프로젝트 구조 파싱
        structure = agent.generate_structure(framework, components)
        dependencies = agent.extract_dependencies(
            framework, data.get("requirements", [])
        )

        return {
            "project_structure": structure,
            "dependencies": dependencies,
            "file_count": agent.count_files(structure),
            "config_files": agent.generate_configs(framework),
        }

    async def _execute_component_decision(self, agent, data: Dict) -> Dict[str, Any]:
        """Component Decision Agent 실행"""
        structure = data.get("project_structure", {})
        framework = data.get("framework", "react")

        # 실제 아키텍처 결정
        architecture = agent.decide_architecture(structure, framework)
        patterns = agent.select_patterns(framework, data.get("requirements", []))

        return {
            "architecture": architecture,
            "design_patterns": patterns,
            "state_management": agent.select_state_management(framework),
            "routing_strategy": agent.decide_routing(framework),
        }

    async def _execute_match_rate(self, agent, data: Dict) -> Dict[str, Any]:
        """Match Rate Agent 실행"""
        requirements = data.get("requirements", [])
        architecture = data.get("architecture", "")

        # 실제 매칭 점수 계산
        score = agent.calculate_match_score(requirements, architecture)
        confidence = agent.assess_confidence(score)

        return {
            "match_score": score,
            "confidence": confidence,
            "recommendations": agent.generate_recommendations(score, requirements),
            "risk_assessment": agent.assess_risks(score),
        }

    async def _execute_search(self, agent, data: Dict) -> Dict[str, Any]:
        """Search Agent 실행"""
        framework = data.get("framework", "react")
        requirements = data.get("requirements", [])

        # 실제 템플릿 검색
        templates = agent.search_templates(framework, requirements)
        best_match = agent.find_best_match(templates, requirements)

        return {
            "search_results": templates,
            "best_template": best_match,
            "relevance_score": agent.calculate_relevance(best_match, requirements),
            "alternatives": agent.suggest_alternatives(templates),
        }

    async def _execute_generation(self, agent, data: Dict) -> Dict[str, Any]:
        """Generation Agent 실행"""
        framework = data.get("framework", "react")
        components = data.get("components", [])
        structure = data.get("project_structure", {})

        # 실제 코드 생성
        generated_files = await agent.generate_code(framework, components, structure)

        return {
            "generated_files": len(generated_files),
            "lines_of_code": agent.count_lines(generated_files),
            "file_list": list(generated_files.keys()),
            "code_quality_score": agent.assess_quality(generated_files),
        }

    async def _execute_assembly(self, agent, data: Dict) -> Dict[str, Any]:
        """Assembly Agent 실행"""
        file_list = data.get("file_list", [])
        structure = data.get("project_structure", {})

        # 실제 프로젝트 조립
        project_path = await agent.assemble_project(file_list, structure)

        return {
            "project_path": project_path,
            "total_size": agent.calculate_size(project_path),
            "build_ready": agent.verify_build_ready(project_path),
            "test_coverage": agent.calculate_test_coverage(project_path),
        }

    async def _execute_download(self, agent, data: Dict) -> Dict[str, Any]:
        """Download Agent 실행"""
        project_path = data.get("project_path", "")

        # 실제 다운로드 준비
        zip_path = await agent.create_archive(project_path)
        download_url = agent.generate_download_url(zip_path)

        return {
            "download_url": download_url,
            "file_size": agent.get_file_size(zip_path),
            "checksum": agent.calculate_checksum(zip_path),
            "expires_at": agent.set_expiration(),
        }

    def _log_stage_results(self, stage: str, result: Dict):
        """스테이지 결과 로깅"""
        if stage == "nl_input":
            logger.info(
                f"   📋 Requirements: {len(result.get('requirements', []))} extracted"
            )
        elif stage == "ui_selection":
            logger.info(f"   🎨 Framework: {result.get('framework', 'N/A')}")
        elif stage == "generation":
            logger.info(f"   📁 Files: {result.get('generated_files', 0)}")
            logger.info(f"   📝 Lines: {result.get('lines_of_code', 0)}")
        elif stage == "download":
            logger.info(f"   📦 Download URL: {result.get('download_url', 'N/A')}")


# FastAPI 통합
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="T-Developer Complete Service")

# 전역 오케스트레이터 인스턴스
orchestrator = CompleteOrchestrator()


class GenerateRequest(BaseModel):
    query: str


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>T-Developer Complete Service</title>
            <style>
                body {
                    font-family: Arial;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }
                h1 { color: #333; }
                textarea {
                    width: 100%;
                    height: 100px;
                    padding: 10px;
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    font-size: 16px;
                }
                button {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 30px;
                    border: none;
                    border-radius: 5px;
                    font-size: 18px;
                    cursor: pointer;
                    margin-top: 10px;
                }
                button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }
                #result {
                    margin-top: 20px;
                    padding: 20px;
                    background: #f5f5f5;
                    border-radius: 5px;
                    display: none;
                }
                .loading {
                    display: none;
                    margin-top: 20px;
                    text-align: center;
                }
                .spinner {
                    border: 3px solid #f3f3f3;
                    border-top: 3px solid #667eea;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 T-Developer Complete Service</h1>
                <p>9개의 프로덕션 에이전트가 완벽하게 작동하는 서비스</p>

                <textarea id="query" placeholder="무엇을 만들어드릴까요? 예: React로 할일 관리 앱을 만들어주세요"></textarea>
                <br>
                <button onclick="generate()">코드 생성 시작</button>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>9개 에이전트가 작업 중입니다...</p>
                </div>

                <div id="result"></div>
            </div>

            <script>
                async function generate() {
                    const query = document.getElementById('query').value;
                    if (!query) {
                        alert('프로젝트 설명을 입력해주세요!');
                        return;
                    }

                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('result').style.display = 'none';

                    try {
                        const response = await fetch('/api/generate', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({query: query})
                        });

                        const data = await response.json();

                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('result').style.display = 'block';
                        document.getElementById('result').innerHTML = `
                            <h3>✅ 생성 완료!</h3>
                            <p>실행 시간: ${data.execution_time?.toFixed(2)}초</p>
                            <p>완료된 스테이지: ${data.stages_completed}/9</p>
                            <p>생성된 파일: ${data.final_output?.generated_files}개</p>
                            <p>코드 라인: ${data.final_output?.lines_of_code}줄</p>
                            ${data.final_output?.download_url ?
                                `<p><a href="${data.final_output.download_url}">📥 다운로드</a></p>` : ''}
                        `;
                    } catch (error) {
                        document.getElementById('loading').style.display = 'none';
                        alert('오류가 발생했습니다: ' + error.message);
                    }
                }
            </script>
        </body>
    </html>
    """


@app.post("/api/generate")
async def generate(request: GenerateRequest):
    """실제 9-에이전트 파이프라인 실행"""
    try:
        result = await orchestrator.execute_pipeline(request.query)
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """헬스체크"""
    return {
        "status": "healthy",
        "service": "T-Developer Complete Service",
        "agents_loaded": len(orchestrator.agents),
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 T-Developer Complete Service Starting...")
    print("=" * 60)
    print("✅ Master Orchestrator: READY")
    print("✅ 9 Production Agents: LOADED")
    print("✅ Pipeline: OPERATIONAL")
    print("=" * 60)
    print("\n📍 Access at: http://localhost:8000")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
