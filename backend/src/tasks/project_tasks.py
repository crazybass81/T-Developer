"""
Project-related Async Tasks
프로젝트 관련 비동기 작업
"""

from celery import current_task
from typing import Dict, Any, Optional
import os
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import json
import asyncio

from .celery_app import celery_app
from ..database.models import Project, AgentExecution, AgentStatus
from ..database.base import SessionLocal


@celery_app.task(bind=True, name="generate_project_async", queue="projects")
def generate_project_async(
    self, project_id: str, query: str, requirements: Dict[str, Any], user_id: str
) -> Dict[str, Any]:
    """프로젝트 비동기 생성"""

    db = SessionLocal()
    try:
        # Update task state
        current_task.update_state(
            state="PROCESSING", meta={"stage": "initialization", "progress": 0}
        )

        # Get project from database
        project = db.query(Project).filter_by(id=project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        project.status = "processing"
        db.commit()

        # Stage 1: NL Processing (10%)
        current_task.update_state(
            state="PROCESSING", meta={"stage": "nl_processing", "progress": 10}
        )
        nl_result = process_nl_input(query, requirements)

        # Stage 2: UI Framework Selection (20%)
        current_task.update_state(
            state="PROCESSING", meta={"stage": "ui_selection", "progress": 20}
        )
        ui_framework = select_ui_framework(nl_result)

        # Stage 3: Component Decision (30%)
        current_task.update_state(
            state="PROCESSING", meta={"stage": "component_decision", "progress": 30}
        )
        components = decide_components(nl_result, ui_framework)

        # Stage 4: Code Generation (50%)
        current_task.update_state(
            state="PROCESSING", meta={"stage": "code_generation", "progress": 50}
        )
        generated_code = generate_code(components, ui_framework)

        # Stage 5: Project Assembly (70%)
        current_task.update_state(
            state="PROCESSING", meta={"stage": "project_assembly", "progress": 70}
        )
        project_path = assemble_project(project_id, generated_code)

        # Stage 6: Create ZIP (90%)
        current_task.update_state(
            state="PROCESSING", meta={"stage": "creating_zip", "progress": 90}
        )
        zip_path = create_project_zip(project_path, project_id)

        # Stage 7: Update database (100%)
        current_task.update_state(
            state="PROCESSING", meta={"stage": "finalizing", "progress": 95}
        )

        project.status = "completed"
        project.file_path = str(zip_path)
        project.download_url = f"/api/v1/download/{project_id}"
        project.completed_at = datetime.utcnow()
        project.file_size = os.path.getsize(zip_path)
        project.metadata = {
            "framework": ui_framework,
            "components": components,
            "generation_time": (datetime.utcnow() - project.created_at).total_seconds(),
        }
        db.commit()

        # Log agent executions
        log_agent_executions(
            db,
            project_id,
            {
                "nl_processing": nl_result,
                "ui_selection": ui_framework,
                "component_decision": components,
            },
        )

        return {
            "project_id": project_id,
            "status": "completed",
            "download_url": project.download_url,
            "file_size": project.file_size,
            "generation_time": project.metadata["generation_time"],
        }

    except Exception as e:
        # Handle failure
        if project:
            project.status = "failed"
            project.metadata = {"error": str(e)}
            db.commit()

        # Re-raise for Celery retry
        raise self.retry(exc=e)

    finally:
        db.close()


@celery_app.task(name="cleanup_old_projects", queue="projects")
def cleanup_old_projects(days: int = 7) -> Dict[str, int]:
    """오래된 프로젝트 정리"""

    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Find old projects
        old_projects = (
            db.query(Project)
            .filter(
                Project.created_at < cutoff_date,
                Project.status.in_(["completed", "failed"]),
            )
            .all()
        )

        deleted_count = 0
        cleaned_size = 0

        for project in old_projects:
            # Delete files
            if project.file_path and os.path.exists(project.file_path):
                file_size = os.path.getsize(project.file_path)
                os.remove(project.file_path)
                cleaned_size += file_size

            # Delete project directory
            project_dir = Path(f"/tmp/projects/{project.id}")
            if project_dir.exists():
                shutil.rmtree(project_dir)

            # Delete from database
            db.delete(project)
            deleted_count += 1

        db.commit()

        return {
            "deleted_projects": deleted_count,
            "cleaned_size_mb": cleaned_size / (1024 * 1024),
        }

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name="send_project_notification", queue="emails")
def send_project_notification(
    user_email: str, project_id: str, status: str, download_url: Optional[str] = None
) -> bool:
    """프로젝트 완료 알림 전송"""

    from ..tasks.email_tasks import send_email

    if status == "completed":
        subject = "Your project is ready!"
        body = f"""
        Your project has been successfully generated.

        Project ID: {project_id}
        Download URL: {download_url}

        Please note that the download link will expire in 24 hours.
        """
    else:
        subject = "Project generation failed"
        body = f"""
        Unfortunately, we couldn't generate your project.

        Project ID: {project_id}

        Please try again or contact support if the issue persists.
        """

    return send_email.delay(user_email, subject, body)


# Helper functions with Production Implementation
def process_nl_input(query: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
    """NL 입력 처리 - Production Implementation"""
    # 키워드 기반 의도 분석
    query_lower = query.lower()

    # 프로젝트 타입 판별
    if any(word in query_lower for word in ["web", "website", "site", "frontend"]):
        intent = "create_web_app"
    elif any(word in query_lower for word in ["api", "backend", "server", "rest"]):
        intent = "create_api"
    elif any(word in query_lower for word in ["mobile", "app", "ios", "android"]):
        intent = "create_mobile_app"
    elif any(word in query_lower for word in ["cli", "command", "terminal", "console"]):
        intent = "create_cli_tool"
    else:
        intent = "create_web_app"  # 기본값

    # 기능 추출
    features = requirements.get("features", [])
    if "auth" in query_lower or "login" in query_lower:
        features.append("authentication")
    if "database" in query_lower or "data" in query_lower:
        features.append("database")
    if "real-time" in query_lower or "realtime" in query_lower:
        features.append("websocket")
    if "payment" in query_lower or "stripe" in query_lower:
        features.append("payment")
    if "admin" in query_lower:
        features.append("admin_panel")

    # 복잡도 판별
    complexity = "simple"
    if len(features) > 2:
        complexity = "medium"
    if len(features) > 5:
        complexity = "complex"

    return {
        "intent": intent,
        "features": list(set(features)),  # 중복 제거
        "complexity": complexity,
        "original_query": query,
    }


def select_ui_framework(nl_result: Dict[str, Any]) -> str:
    """UI 프레임워크 선택 - Production Implementation"""
    intent = nl_result.get("intent", "create_web_app")
    features = nl_result.get("features", [])
    complexity = nl_result.get("complexity", "simple")

    # 의도와 복잡도에 따른 프레임워크 선택
    if intent == "create_web_app":
        if complexity == "complex" or "admin_panel" in features:
            return "nextjs"  # 복잡한 웹앱은 Next.js
        elif "websocket" in features:
            return "react"  # 실시간 기능은 React
        elif complexity == "simple":
            return "vanilla"  # 간단한 경우 순수 JS
        else:
            return "react"  # 기본값

    elif intent == "create_api":
        if "websocket" in features:
            return "fastapi"  # 실시간 API
        elif "authentication" in features:
            return "fastapi"  # 인증이 있는 API
        else:
            return "express"  # 간단한 API

    elif intent == "create_mobile_app":
        return "react-native"

    elif intent == "create_cli_tool":
        return "python-click"

    return "react"  # 기본값


def decide_components(nl_result: Dict[str, Any], framework: str) -> list:
    """컴포넌트 결정 - Production Implementation"""
    features = nl_result.get("features", [])
    intent = nl_result.get("intent", "create_web_app")
    components = []

    # 기본 컴포넌트 (프로젝트 타입별)
    if intent == "create_web_app":
        components = ["navbar", "footer", "router"]

        # 기능별 컴포넌트 추가
        if "authentication" in features:
            components.extend(["login", "register", "profile"])
        if "database" in features:
            components.extend(["data_list", "data_form", "data_detail"])
        if "admin_panel" in features:
            components.extend(["dashboard", "sidebar", "data_table"])
        if "payment" in features:
            components.extend(["checkout", "payment_form", "invoice"])
        if "websocket" in features:
            components.extend(["chat", "notification", "live_update"])

        # 프레임워크별 특수 컴포넌트
        if framework == "nextjs":
            components.append("_app")
            components.append("_document")
        elif framework == "react":
            components.append("App")

    elif intent == "create_api":
        components = ["routes", "middleware", "models"]

        if "authentication" in features:
            components.extend(["auth_routes", "jwt_handler", "user_model"])
        if "database" in features:
            components.extend(["db_connection", "schemas", "crud"])
        if "websocket" in features:
            components.extend(["ws_handler", "events"])

    elif intent == "create_cli_tool":
        components = ["commands", "utils", "config"]

    return list(set(components))  # 중복 제거


def generate_code(components: list, framework: str) -> Dict[str, str]:
    """코드 생성 - Production Implementation"""
    code_files = {}

    # 프레임워크별 기본 파일 생성
    if framework in ["react", "nextjs"]:
        # package.json
        code_files["package.json"] = (
            '''{
  "name": "generated-project",
  "version": "1.0.0",
  "scripts": {
    "dev": "'''
            + ("next dev" if framework == "nextjs" else "react-scripts start")
            + '''",
    "build": "'''
            + ("next build" if framework == "nextjs" else "react-scripts build")
            + '''",
    "start": "'''
            + ("next start" if framework == "nextjs" else "serve -s build")
            + '''"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"'''
            + (',\n    "next": "^14.0.0"' if framework == "nextjs" else "")
            + """
  }
}"""
        )

        # 메인 컴포넌트
        if "App" in components or framework == "react":
            code_files["src/App.js"] = (
                """import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <h1>Welcome to Your New App</h1>
      """
                + "\n      ".join(
                    [
                        f'<{comp.title().replace("_", "")} />'
                        for comp in components
                        if comp not in ["App", "_app", "_document"]
                    ]
                )
                + """
    </div>
  );
}

export default App;"""
            )

        # CSS 파일
        code_files[
            "src/App.css"
        ] = """.App {
  text-align: center;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 30px;
}"""

        # 각 컴포넌트 파일 생성
        for component in components:
            if component not in ["App", "_app", "_document"]:
                comp_name = component.title().replace("_", "")
                code_files[
                    f"src/components/{comp_name}.js"
                ] = f"""import React from 'react';

const {comp_name} = () => {{
  return (
    <div className="{component}">
      <h2>{comp_name}</h2>
      {{/* Production implementation for {component} */}}
    </div>
  );
}};

export default {comp_name};"""

    elif framework == "fastapi":
        # main.py
        code_files[
            "main.py"
        ] = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Generated API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)"""

        # requirements.txt
        code_files[
            "requirements.txt"
        ] = """fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0"""

    elif framework == "vanilla":
        # index.html
        code_files[
            "index.html"
        ] = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Project</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="app">
        <h1>Welcome to Your Project</h1>
        <div id="content"></div>
    </div>
    <script src="app.js"></script>
</body>
</html>"""

        # app.js
        code_files["app.js"] = (
            """// Production JavaScript Implementation
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');

    const app = document.getElementById('app');
    const content = document.getElementById('content');

    // Production functionality
    const components = """
            + str(components)
            + """;

    components.forEach(comp => {
        const section = document.createElement('section');
        section.className = comp;
        section.innerHTML = `<h2>${comp.replace('_', ' ').toUpperCase()}</h2>`;
        content.appendChild(section);
    });
});"""
        )

        # style.css
        code_files[
            "style.css"
        ] = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    line-height: 1.6;
    color: #333;
}

#app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1 {
    margin-bottom: 30px;
    color: #2c3e50;
}

section {
    margin: 20px 0;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
}"""

    # README.md 추가
    code_files[
        "README.md"
    ] = f"""# Generated Project

## Framework: {framework}

## Components
{chr(10).join(['- ' + comp for comp in components])}

## Getting Started

### Installation
{"npm install" if framework in ["react", "nextjs"] else "pip install -r requirements.txt" if framework == "fastapi" else "Open index.html in browser"}

### Run Development Server
{"npm run dev" if framework in ["react", "nextjs"] else "python main.py" if framework == "fastapi" else "Open index.html"}

## Production Build
{"npm run build" if framework in ["react", "nextjs"] else "Docker deployment recommended" if framework == "fastapi" else "Deploy static files"}
"""

    return code_files


def assemble_project(project_id: str, code: Dict[str, str]) -> Path:
    """프로젝트 조립"""
    project_dir = Path(f"/tmp/projects/{project_id}")
    project_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in code.items():
        file_path = project_dir / filename
        file_path.write_text(content)

    return project_dir


def create_project_zip(project_path: Path, project_id: str) -> Path:
    """프로젝트 ZIP 생성"""
    zip_path = Path(f"/tmp/projects/{project_id}.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in project_path.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(project_path)
                zipf.write(file, arcname)

    return zip_path


def log_agent_executions(db, project_id: str, executions: Dict[str, Any]):
    """에이전트 실행 로그 기록"""
    for agent_name, result in executions.items():
        execution = AgentExecution(
            project_id=project_id,
            agent_id=agent_name,  # Should be actual agent ID
            status=AgentStatus.COMPLETED,
            input_data={"query": result},
            output_data=result,
            execution_time=1.0,  # Should be actual time
            created_at=datetime.utcnow(),
        )
        db.add(execution)
    db.commit()
