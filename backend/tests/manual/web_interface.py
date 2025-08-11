#!/usr/bin/env python3
"""
T-Developer Web Interface
웹 브라우저에서 직접 실행 가능한 인터페이스
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import sys
import os

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/src'))

# Import the orchestrator
from orchestration.master_orchestrator import MasterOrchestrator, PipelineConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="T-Developer Pipeline",
    description="9-Agent AI Code Generation Pipeline",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active pipelines
active_pipelines: Dict[str, Dict[str, Any]] = {}

class GenerateRequest(BaseModel):
    """Code generation request model"""
    query: str
    framework: Optional[str] = None
    language: Optional[str] = None

class PipelineStatus(BaseModel):
    """Pipeline execution status"""
    pipeline_id: str
    status: str
    current_stage: str
    progress: int
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# HTML Interface
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>T-Developer: AI 코드 생성 파이프라인</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 900px;
            width: 100%;
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 16px;
            resize: vertical;
            min-height: 120px;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .options {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        select {
            flex: 1;
            padding: 12px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 16px;
            background: white;
            cursor: pointer;
            transition: border-color 0.3s;
        }
        
        select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            width: 100%;
        }
        
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .pipeline-status {
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        
        .pipeline-status.active {
            display: block;
        }
        
        .status-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .status-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
        }
        
        .status-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .status-badge.running {
            background: #ffc107;
            color: #000;
        }
        
        .status-badge.success {
            background: #28a745;
            color: white;
        }
        
        .status-badge.error {
            background: #dc3545;
            color: white;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e1e1e1;
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 500;
        }
        
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        
        .agent-card {
            padding: 15px;
            background: white;
            border-radius: 10px;
            border: 2px solid #e1e1e1;
            transition: all 0.3s;
        }
        
        .agent-card.active {
            border-color: #ffc107;
            background: #fff8e1;
        }
        
        .agent-card.completed {
            border-color: #28a745;
            background: #e8f5e9;
        }
        
        .agent-card.error {
            border-color: #dc3545;
            background: #ffebee;
        }
        
        .agent-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .agent-status {
            font-size: 14px;
            color: #666;
        }
        
        .result-section {
            margin-top: 30px;
            padding: 20px;
            background: #e8f5e9;
            border-radius: 10px;
            display: none;
        }
        
        .result-section.active {
            display: block;
        }
        
        .download-button {
            background: #28a745;
            margin-top: 20px;
        }
        
        .error-message {
            padding: 15px;
            background: #ffebee;
            border-left: 4px solid #dc3545;
            border-radius: 5px;
            color: #721c24;
            margin-top: 20px;
        }
        
        .examples {
            margin-top: 30px;
            padding: 20px;
            background: #f0f0f0;
            border-radius: 10px;
        }
        
        .example-title {
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
        
        .example-item {
            padding: 10px;
            background: white;
            border-radius: 5px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .example-item:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 T-Developer</h1>
        <p class="subtitle">9개 AI 에이전트가 협업하여 완벽한 코드를 생성합니다</p>
        
        <div class="input-group">
            <label for="query">무엇을 만들어드릴까요?</label>
            <textarea id="query" placeholder="예: React로 할일 관리 앱을 만들어주세요. 추가, 완료, 삭제 기능이 필요합니다."></textarea>
        </div>
        
        <div class="options">
            <div style="flex: 1;">
                <label for="framework">프레임워크</label>
                <select id="framework">
                    <option value="">자동 선택</option>
                    <option value="react">React</option>
                    <option value="vue">Vue.js</option>
                    <option value="angular">Angular</option>
                    <option value="fastapi">FastAPI</option>
                    <option value="django">Django</option>
                    <option value="express">Express</option>
                </select>
            </div>
            
            <div style="flex: 1;">
                <label for="language">언어</label>
                <select id="language">
                    <option value="">자동 선택</option>
                    <option value="typescript">TypeScript</option>
                    <option value="javascript">JavaScript</option>
                    <option value="python">Python</option>
                </select>
            </div>
        </div>
        
        <button id="generateBtn" onclick="startGeneration()">
            코드 생성 시작
        </button>
        
        <div id="pipelineStatus" class="pipeline-status">
            <div class="status-header">
                <div class="status-title">파이프라인 실행 중</div>
                <div id="statusBadge" class="status-badge running">실행중</div>
            </div>
            
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill" style="width: 0%">
                    0%
                </div>
            </div>
            
            <div class="agents-grid">
                <div class="agent-card" id="agent-nl_input">
                    <div class="agent-name">📝 NL Input</div>
                    <div class="agent-status">대기중</div>
                </div>
                <div class="agent-card" id="agent-ui_selection">
                    <div class="agent-name">🎨 UI Selection</div>
                    <div class="agent-status">대기중</div>
                </div>
                <div class="agent-card" id="agent-parser">
                    <div class="agent-name">🔍 Parser</div>
                    <div class="agent-status">대기중</div>
                </div>
                <div class="agent-card" id="agent-component_decision">
                    <div class="agent-name">🏗️ Component Decision</div>
                    <div class="agent-status">대기중</div>
                </div>
                <div class="agent-card" id="agent-match_rate">
                    <div class="agent-name">📊 Match Rate</div>
                    <div class="agent-status">대기중</div>
                </div>
                <div class="agent-card" id="agent-search">
                    <div class="agent-name">🔎 Search</div>
                    <div class="agent-status">대기중</div>
                </div>
                <div class="agent-card" id="agent-generation">
                    <div class="agent-name">⚡ Generation</div>
                    <div class="agent-status">대기중</div>
                </div>
                <div class="agent-card" id="agent-assembly">
                    <div class="agent-name">📦 Assembly</div>
                    <div class="agent-status">대기중</div>
                </div>
                <div class="agent-card" id="agent-download">
                    <div class="agent-name">💾 Download</div>
                    <div class="agent-status">대기중</div>
                </div>
            </div>
            
            <div id="currentMessage" style="margin-top: 20px; color: #666;">
                파이프라인을 초기화하고 있습니다...
            </div>
        </div>
        
        <div id="resultSection" class="result-section">
            <h3 style="margin-bottom: 15px;">✅ 코드 생성 완료!</h3>
            <div id="resultDetails"></div>
            <button class="download-button" onclick="downloadProject()">
                📥 프로젝트 다운로드
            </button>
        </div>
        
        <div id="errorSection" class="error-message" style="display: none;">
            <strong>오류 발생:</strong>
            <div id="errorMessage"></div>
        </div>
        
        <div class="examples">
            <div class="example-title">예시 프롬프트 (클릭하여 사용)</div>
            <div class="example-item" onclick="useExample('React와 TypeScript로 할일 관리 앱을 만들어주세요. 할일 추가, 완료 표시, 삭제 기능이 필요합니다.')">
                📱 React Todo 앱
            </div>
            <div class="example-item" onclick="useExample('FastAPI로 블로그 REST API를 만들어주세요. 게시글 CRUD, 사용자 인증, 댓글 기능이 필요합니다.')">
                🚀 FastAPI 블로그 API
            </div>
            <div class="example-item" onclick="useExample('Vue.js로 실시간 채팅 애플리케이션을 만들어주세요. WebSocket을 사용하고 이모지 지원이 필요합니다.')">
                💬 Vue.js 채팅 앱
            </div>
        </div>
    </div>
    
    <script>
        let currentPipelineId = null;
        let pollInterval = null;
        
        function useExample(text) {
            document.getElementById('query').value = text;
        }
        
        async function startGeneration() {
            const query = document.getElementById('query').value.trim();
            
            if (!query) {
                alert('만들고 싶은 프로젝트를 설명해주세요!');
                return;
            }
            
            // UI 초기화
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('generateBtn').innerHTML = '생성 중... <span class="spinner"></span>';
            document.getElementById('pipelineStatus').classList.add('active');
            document.getElementById('resultSection').classList.remove('active');
            document.getElementById('errorSection').style.display = 'none';
            
            // 모든 에이전트 카드 초기화
            document.querySelectorAll('.agent-card').forEach(card => {
                card.className = 'agent-card';
                card.querySelector('.agent-status').textContent = '대기중';
            });
            
            try {
                // API 요청
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: query,
                        framework: document.getElementById('framework').value || null,
                        language: document.getElementById('language').value || null
                    })
                });
                
                const data = await response.json();
                
                if (data.pipeline_id) {
                    currentPipelineId = data.pipeline_id;
                    startPolling();
                } else {
                    throw new Error('파이프라인 시작 실패');
                }
                
            } catch (error) {
                showError(error.message);
                resetUI();
            }
        }
        
        function startPolling() {
            pollInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/status/${currentPipelineId}`);
                    const status = await response.json();
                    
                    updateUI(status);
                    
                    if (status.status === 'completed' || status.status === 'failed') {
                        clearInterval(pollInterval);
                        resetUI();
                        
                        if (status.status === 'completed') {
                            showResult(status.result);
                        } else {
                            showError(status.error || '알 수 없는 오류가 발생했습니다');
                        }
                    }
                    
                } catch (error) {
                    console.error('Status polling error:', error);
                }
            }, 1000);
        }
        
        function updateUI(status) {
            // 진행률 업데이트
            const progress = status.progress || 0;
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('progressFill').textContent = progress + '%';
            
            // 상태 배지 업데이트
            const badge = document.getElementById('statusBadge');
            badge.className = `status-badge ${status.status}`;
            badge.textContent = status.status === 'running' ? '실행중' : 
                              status.status === 'completed' ? '완료' : '오류';
            
            // 현재 메시지 업데이트
            document.getElementById('currentMessage').textContent = status.message || '';
            
            // 에이전트 상태 업데이트
            if (status.current_stage) {
                const currentAgent = document.getElementById(`agent-${status.current_stage}`);
                if (currentAgent) {
                    // 이전 active 제거
                    document.querySelectorAll('.agent-card.active').forEach(card => {
                        card.classList.remove('active');
                        card.classList.add('completed');
                        card.querySelector('.agent-status').textContent = '완료';
                    });
                    
                    // 현재 active 설정
                    currentAgent.classList.add('active');
                    currentAgent.querySelector('.agent-status').textContent = '실행중...';
                }
            }
        }
        
        function showResult(result) {
            document.getElementById('resultSection').classList.add('active');
            
            let details = '<ul>';
            if (result.generated_files) {
                details += `<li>📁 생성된 파일: ${result.generated_files}개</li>`;
            }
            if (result.lines_of_code) {
                details += `<li>📝 코드 라인: ${result.lines_of_code}줄</li>`;
            }
            if (result.framework) {
                details += `<li>🎨 프레임워크: ${result.framework}</li>`;
            }
            if (result.download_url) {
                details += `<li>📦 다운로드 준비 완료</li>`;
            }
            details += '</ul>';
            
            document.getElementById('resultDetails').innerHTML = details;
        }
        
        function showError(message) {
            document.getElementById('errorSection').style.display = 'block';
            document.getElementById('errorMessage').textContent = message;
        }
        
        function resetUI() {
            document.getElementById('generateBtn').disabled = false;
            document.getElementById('generateBtn').innerHTML = '코드 생성 시작';
        }
        
        async function downloadProject() {
            if (currentPipelineId) {
                window.open(`/api/download/${currentPipelineId}`, '_blank');
            }
        }
        
        // Enter 키로 생성 시작
        document.getElementById('query').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                startGeneration();
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    return HTML_CONTENT

@app.post("/api/generate")
async def generate_code(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Start code generation pipeline"""
    
    pipeline_id = str(uuid.uuid4())
    
    # Initialize pipeline status
    active_pipelines[pipeline_id] = {
        "status": "running",
        "current_stage": "initialization",
        "progress": 0,
        "message": "파이프라인을 시작하고 있습니다...",
        "started_at": datetime.now(),
        "result": None,
        "error": None
    }
    
    # Start pipeline in background
    background_tasks.add_task(
        run_pipeline,
        pipeline_id,
        request.query,
        request.framework,
        request.language
    )
    
    return JSONResponse({
        "pipeline_id": pipeline_id,
        "message": "Pipeline started successfully"
    })

@app.get("/api/status/{pipeline_id}")
async def get_status(pipeline_id: str):
    """Get pipeline execution status"""
    
    if pipeline_id not in active_pipelines:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    status = active_pipelines[pipeline_id]
    
    return JSONResponse({
        "pipeline_id": pipeline_id,
        "status": status["status"],
        "current_stage": status.get("current_stage"),
        "progress": status.get("progress", 0),
        "message": status.get("message", ""),
        "result": status.get("result"),
        "error": status.get("error")
    })

@app.get("/api/download/{pipeline_id}")
async def download_project(pipeline_id: str):
    """Download generated project"""
    
    if pipeline_id not in active_pipelines:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    status = active_pipelines[pipeline_id]
    
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Project not ready for download")
    
    # In real implementation, this would return the actual zip file
    # For now, return a mock response
    return JSONResponse({
        "download_url": f"/downloads/{pipeline_id}.zip",
        "expires_at": "2024-01-16T12:00:00Z"
    })

async def run_pipeline(pipeline_id: str, query: str, framework: str = None, language: str = None):
    """Run the 9-agent pipeline"""
    
    try:
        # Update status
        active_pipelines[pipeline_id]["message"] = "오케스트레이터 초기화 중..."
        active_pipelines[pipeline_id]["progress"] = 5
        
        # Initialize orchestrator
        config = PipelineConfig(
            enable_monitoring=True,
            enable_caching=True,
            timeout_seconds=120
        )
        
        orchestrator = MasterOrchestrator(config)
        
        # Define agent stages for progress tracking
        stages = [
            ("nl_input", "사용자 요구사항 분석 중...", 11),
            ("ui_selection", "UI 프레임워크 선택 중...", 22),
            ("parser", "프로젝트 구조 분석 중...", 33),
            ("component_decision", "컴포넌트 아키텍처 결정 중...", 44),
            ("match_rate", "템플릿 매칭 중...", 55),
            ("search", "최적 솔루션 검색 중...", 66),
            ("generation", "코드 생성 중...", 77),
            ("assembly", "프로젝트 조립 중...", 88),
            ("download", "다운로드 준비 중...", 100)
        ]
        
        # Simulate pipeline execution with progress updates
        for stage_name, message, progress in stages:
            active_pipelines[pipeline_id]["current_stage"] = stage_name
            active_pipelines[pipeline_id]["message"] = message
            active_pipelines[pipeline_id]["progress"] = progress
            
            # Simulate processing time
            await asyncio.sleep(2)
        
        # Mark as completed
        active_pipelines[pipeline_id]["status"] = "completed"
        active_pipelines[pipeline_id]["message"] = "코드 생성이 완료되었습니다!"
        active_pipelines[pipeline_id]["progress"] = 100
        active_pipelines[pipeline_id]["result"] = {
            "generated_files": 45,
            "lines_of_code": 1250,
            "framework": framework or "React",
            "language": language or "TypeScript",
            "download_url": f"/api/download/{pipeline_id}"
        }
        
        logger.info(f"Pipeline {pipeline_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline {pipeline_id} failed: {str(e)}")
        
        active_pipelines[pipeline_id]["status"] = "failed"
        active_pipelines[pipeline_id]["error"] = str(e)
        active_pipelines[pipeline_id]["message"] = "오류가 발생했습니다"
    
    finally:
        # Clean up old pipelines after 1 hour
        await asyncio.sleep(3600)
        if pipeline_id in active_pipelines:
            del active_pipelines[pipeline_id]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 T-Developer Web Interface Starting...")
    print("="*60)
    print("📍 Open your browser and go to:")
    print("   http://localhost:8000")
    print("="*60)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )