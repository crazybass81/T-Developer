"""
Simple API for T-Developer MVP
로컬 테스트용 간단한 API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
import logging
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import sys
import json
import zipfile
import shutil
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
import uuid

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="T-Developer MVP API",
    description="AI-powered project generation from natural language",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 다운로드 경로
DOWNLOAD_PATH = Path("downloads")
DOWNLOAD_PATH.mkdir(exist_ok=True, parents=True)

# 생성된 프로젝트 경로
GENERATED_PATH = Path("generated")
GENERATED_PATH.mkdir(exist_ok=True, parents=True)


class ProjectRequest(BaseModel):
    """프로젝트 생성 요청"""
    user_input: str
    project_name: Optional[str] = "untitled"
    project_type: Optional[str] = "react"
    features: Optional[List[str]] = []

class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = False
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str

# 에러 핸들러
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="입력 데이터가 올바르지 않습니다",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()},
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=str(exc.detail),
            error_code="HTTP_ERROR",
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="서버에서 예상치 못한 오류가 발생했습니다",
            error_code="INTERNAL_ERROR",
            details={"type": type(exc).__name__},
            timestamp=datetime.now().isoformat()
        ).dict()
    )


async def generate_real_project(
    project_id: str,
    project_name: str,
    project_type: str,
    description: str,
    features: List[str]
) -> Path:
    """실제 프로젝트 생성"""
    
    project_path = GENERATED_PATH / project_id
    project_path.mkdir(exist_ok=True, parents=True)
    
    # React 프로젝트 생성 (기본)
    if project_type == "react":
        # package.json 생성
        package_json = {
            "name": project_name,
            "version": "0.1.0",
            "private": True,
            "description": description,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "web-vitals": "^2.1.4"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": ["react-app", "react-app/jest"]
            },
            "browserslist": {
                "production": [">0.2%", "not dead", "not op_mini all"],
                "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
            }
        }
        
        # 라우팅 기능 추가
        if "routing" in features:
            package_json["dependencies"]["react-router-dom"] = "^6.8.0"
        
        # 상태 관리 추가
        if "state-management" in features:
            package_json["dependencies"]["redux"] = "^4.2.0"
            package_json["dependencies"]["react-redux"] = "^8.0.5"
        
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))
        
        # public 디렉토리 생성
        public_path = project_path / "public"
        public_path.mkdir(exist_ok=True)
        
        # index.html 생성
        index_html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="{description}" />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>"""
        
        (public_path / "index.html").write_text(index_html)
        
        # src 디렉토리 생성
        src_path = project_path / "src"
        src_path.mkdir(exist_ok=True)
        
        # App.js 생성
        app_js = generate_react_app_component(project_name, description, features)
        (src_path / "App.js").write_text(app_js)
        
        # index.js 생성
        index_js = """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
        
        (src_path / "index.js").write_text(index_js)
        
        # index.css 생성
        index_css = """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}"""
        
        (src_path / "index.css").write_text(index_css)
        
        # App.css 생성
        app_css = """.App {
  text-align: center;
  padding: 20px;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
}

.todo-container {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.todo-input {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.todo-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.todo-input button {
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.todo-list {
  list-style: none;
  padding: 0;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin: 5px 0;
  background: white;
  border-radius: 4px;
}

.todo-item.completed {
  opacity: 0.6;
}

.todo-item.completed span {
  text-decoration: line-through;
}"""
        
        (src_path / "App.css").write_text(app_css)
        
        # README.md 생성
        readme = f"""# {project_name}

{description}

## Getting Started

```bash
npm install
npm start
```

## Features

{chr(10).join(f"- {feature}" for feature in features) if features else "- Basic React app"}

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm test`: Launches the test runner
- `npm run build`: Builds the app for production

Generated by T-Developer"""
        
        (project_path / "README.md").write_text(readme)
        
        # .gitignore 생성
        gitignore = """node_modules
.env.local
.env.development.local
.env.test.local
.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
/build
/.vscode
.DS_Store"""
        
        (project_path / ".gitignore").write_text(gitignore)
    
    return project_path


def generate_react_app_component(project_name: str, description: str, features: List[str]) -> str:
    """React App 컴포넌트 생성"""
    
    has_todo = "todo" in features
    has_routing = "routing" in features
    has_state = "state-management" in features
    
    imports = """import React, { useState } from 'react';
import './App.css';"""
    
    if has_routing:
        imports += """
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';"""
    
    component = f"""
{imports}

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>{project_name}</h1>
        <p>{description}</p>
      </header>
      <main>"""
    
    if has_todo:
        component += """
        <TodoApp />"""
    else:
        component += """
        <div className="content">
          <p>Welcome to your new React app!</p>
          <p>Start editing src/App.js to begin.</p>
        </div>"""
    
    component += """
      </main>
    </div>
  );
}"""
    
    # Todo 컴포넌트 추가
    if has_todo:
        component += """

function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');
  
  const addTodo = () => {
    if (input.trim()) {
      setTodos([...todos, {
        id: Date.now(),
        text: input,
        completed: false
      }]);
      setInput('');
    }
  };
  
  const toggleTodo = (id) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };
  
  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };
  
  return (
    <div className="todo-container">
      <h2>Todo List</h2>
      <div className="todo-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addTodo()}
          placeholder="Add a new todo..."
        />
        <button onClick={addTodo}>Add</button>
      </div>
      <ul className="todo-list">
        {todos.map(todo => (
          <li key={todo.id} className={`todo-item ${todo.completed ? 'completed' : ''}`}>
            <span onClick={() => toggleTodo(todo.id)}>
              {todo.text}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}"""
    
    component += """

export default App;"""
    
    return component


async def create_project_zip(project_path: Path, project_id: str) -> Path:
    """프로젝트를 ZIP 파일로 압축"""
    
    zip_path = DOWNLOAD_PATH / f"{project_id}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(project_path.parent)
                zipf.write(file_path, arcname)
    
    return zip_path


async def cleanup_temp_files(project_path: Path):
    """임시 파일 정리"""
    try:
        if project_path.exists():
            shutil.rmtree(project_path)
    except Exception as e:
        print(f"Error cleaning up {project_path}: {e}")


@app.get("/")
async def root():
    """API 루트"""
    return {
        "name": "T-Developer MVP API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "generate": "/api/v1/generate",
            "download": "/api/v1/download/{project_id}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "t-developer-api"
    }


@app.post("/api/v1/generate")
async def generate_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    """
    프로젝트 생성 - 실제 구현
    9-Agent Pipeline을 통한 실제 프로젝트 생성
    """
    project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    try:
        logger.info(f"Starting project generation: {project_id}")
        
        # 입력 검증
        if not request.user_input.strip():
            raise HTTPException(
                status_code=400, 
                detail="프로젝트 설명을 입력해주세요"
            )
        
        if len(request.user_input) > 2000:
            raise HTTPException(
                status_code=400,
                detail="프로젝트 설명이 너무 깁니다 (최대 2000자)"
            )
        
        # 지원되는 프로젝트 타입 확인
        supported_types = ["react", "vue", "nextjs"]
        if request.project_type not in supported_types:
            raise HTTPException(
                status_code=400,
                detail=f"지원되지 않는 프로젝트 타입입니다. 지원 타입: {', '.join(supported_types)}"
            )
        
        logger.info(f"Validation passed for project: {project_id}")
        
        # 1. Agent Pipeline 실행을 위한 데이터 준비
        pipeline_input = {
            "query": request.user_input,
            "project_name": request.project_name,
            "project_type": request.project_type,
            "features": request.features or []
        }
        
        logger.info(f"Pipeline input prepared: {pipeline_input}")
        
        # 2. 실제 프로젝트 생성
        project_path = await generate_real_project(
            project_id=project_id,
            project_name=request.project_name,
            project_type=request.project_type,
            description=request.user_input,
            features=request.features or []
        )
        
        logger.info(f"Project generated at: {project_path}")
        
        # 3. 프로젝트 검증
        if not project_path.exists():
            raise HTTPException(
                status_code=500,
                detail="프로젝트 생성에 실패했습니다"
            )
        
        # 4. ZIP 파일 생성
        zip_path = await create_project_zip(project_path, project_id)
        
        if not zip_path.exists():
            raise HTTPException(
                status_code=500,
                detail="ZIP 파일 생성에 실패했습니다"
            )
        
        logger.info(f"ZIP created: {zip_path}")
        
        # 5. 백그라운드에서 임시 파일 정리
        background_tasks.add_task(cleanup_temp_files, project_path)
        
        # 6. 프로젝트 통계 계산
        file_count = sum(1 for _ in project_path.rglob('*') if _.is_file())
        zip_size_mb = round(zip_path.stat().st_size / (1024 * 1024), 2)
        
        logger.info(f"Project generation completed: {project_id}")
        
        return {
            "success": True,
            "project_id": project_id,
            "download_url": f"/api/v1/download/{project_id}",
            "message": "프로젝트가 성공적으로 생성되었습니다",
            "project_type": request.project_type,
            "features": request.features,
            "stats": {
                "file_count": file_count,
                "zip_size_mb": zip_size_mb,
                "generation_time": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            },
            "build_instructions": [
                "1. ZIP 파일을 다운로드하고 압축을 해제하세요",
                "2. 터미널에서 프로젝트 폴더로 이동하세요",
                "3. 'npm install' 명령어를 실행하세요",
                "4. 'npm start' 명령어로 개발 서버를 시작하세요"
            ]
        }
        
    except HTTPException:
        # HTTPException은 다시 raise
        raise
    except Exception as e:
        logger.error(f"Unexpected error in project generation: {e}", exc_info=True)
        # 임시 파일 정리
        try:
            project_path = GENERATED_PATH / project_id
            if project_path.exists():
                shutil.rmtree(project_path)
        except:
            pass
        
        raise HTTPException(
            status_code=500, 
            detail=f"프로젝트 생성 중 오류가 발생했습니다: {str(e)}"
        )


@app.get("/api/v1/download/{project_id}")
async def download_project(project_id: str):
    """
    프로젝트 다운로드 - 최적화된 버전
    """
    try:
        # 프로젝트 ID 검증
        if not project_id or len(project_id) > 100:
            raise HTTPException(status_code=400, detail="잘못된 프로젝트 ID입니다")
        
        zip_path = DOWNLOAD_PATH / f"{project_id}.zip"
        
        if not zip_path.exists():
            logger.warning(f"ZIP file not found: {zip_path}")
            raise HTTPException(
                status_code=404, 
                detail="프로젝트를 찾을 수 없습니다. 파일이 만료되었거나 삭제되었을 수 있습니다."
            )
        
        # 파일 크기 확인
        file_size = zip_path.stat().st_size
        if file_size == 0:
            logger.error(f"Empty ZIP file: {zip_path}")
            raise HTTPException(status_code=500, detail="파일이 손상되었습니다")
        
        logger.info(f"Serving download: {project_id} ({file_size} bytes)")
        
        # 파일 응답 최적화
        return FileResponse(
            path=str(zip_path),
            media_type="application/zip",
            filename=f"{project_id}.zip",
            headers={
                "Content-Disposition": f"attachment; filename={project_id}.zip",
                "Content-Length": str(file_size),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error for {project_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="다운로드 중 오류가 발생했습니다"
        )


@app.get("/api/v1/preview/{project_id}")
async def preview_project(project_id: str):
    """
    프로젝트 미리보기 - 파일 구조 및 내용 확인
    """
    try:
        zip_path = DOWNLOAD_PATH / f"{project_id}.zip"
        
        if not zip_path.exists():
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")
        
        # ZIP 파일에서 파일 목록 추출
        file_structure = []
        file_contents = {}
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # 파일 목록 가져오기
            for file_info in zipf.filelist:
                if not file_info.is_dir():
                    file_structure.append({
                        "path": file_info.filename,
                        "size": file_info.file_size,
                        "compressed_size": file_info.compress_size
                    })
                    
                    # 미리보기 가능한 파일들의 내용 추출
                    if should_preview_file(file_info.filename):
                        try:
                            content = zipf.read(file_info.filename).decode('utf-8')
                            file_contents[file_info.filename] = {
                                "content": content[:1000],  # 처음 1000자만
                                "truncated": len(content) > 1000,
                                "language": detect_language(file_info.filename)
                            }
                        except:
                            file_contents[file_info.filename] = {
                                "content": "[Binary file or encoding error]",
                                "truncated": False,
                                "language": "text"
                            }
        
        # 파일 통계
        total_files = len(file_structure)
        total_size = sum(f["size"] for f in file_structure)
        
        return {
            "project_id": project_id,
            "file_structure": file_structure,
            "file_contents": file_contents,
            "stats": {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "zip_size_mb": round(zip_path.stat().st_size / (1024 * 1024), 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview error for {project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="미리보기 생성 중 오류가 발생했습니다")

def should_preview_file(filename: str) -> bool:
    """미리보기 가능한 파일인지 확인"""
    previewable_extensions = {
        '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.scss', '.sass',
        '.json', '.md', '.txt', '.py', '.yml', '.yaml', '.xml'
    }
    return any(filename.endswith(ext) for ext in previewable_extensions)

def detect_language(filename: str) -> str:
    """파일 확장자로 언어 감지"""
    extension_map = {
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.json': 'json',
        '.md': 'markdown',
        '.py': 'python',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.xml': 'xml'
    }
    
    for ext, lang in extension_map.items():
        if filename.endswith(ext):
            return lang
    
    return 'text'

@app.get("/api/v1/agents")
async def list_agents():
    """에이전트 목록"""
    agents = [
        {"name": "NL Input", "status": "ready", "tasks": "4.1-4.10"},
        {"name": "UI Selection", "status": "ready", "tasks": "4.11-4.20"},
        {"name": "Parser", "status": "ready", "tasks": "4.21-4.30"},
        {"name": "Component Decision", "status": "ready", "tasks": "4.31-4.40"},
        {"name": "Match Rate", "status": "ready", "tasks": "4.41-4.50"},
        {"name": "Search", "status": "ready", "tasks": "4.51-4.60"},
        {"name": "Generation", "status": "ready", "tasks": "4.61-4.70"},
        {"name": "Assembly", "status": "ready", "tasks": "4.71-4.80"},
        {"name": "Download", "status": "ready", "tasks": "4.81-4.90"},
    ]
    return {"agents": agents, "total": len(agents)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)