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

@celery_app.task(bind=True, name='generate_project_async', queue='projects')
def generate_project_async(
    self,
    project_id: str,
    query: str,
    requirements: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """프로젝트 비동기 생성"""
    
    db = SessionLocal()
    try:
        # Update task state
        current_task.update_state(
            state='PROCESSING',
            meta={'stage': 'initialization', 'progress': 0}
        )
        
        # Get project from database
        project = db.query(Project).filter_by(id=project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        project.status = 'processing'
        db.commit()
        
        # Stage 1: NL Processing (10%)
        current_task.update_state(
            state='PROCESSING',
            meta={'stage': 'nl_processing', 'progress': 10}
        )
        nl_result = process_nl_input(query, requirements)
        
        # Stage 2: UI Framework Selection (20%)
        current_task.update_state(
            state='PROCESSING',
            meta={'stage': 'ui_selection', 'progress': 20}
        )
        ui_framework = select_ui_framework(nl_result)
        
        # Stage 3: Component Decision (30%)
        current_task.update_state(
            state='PROCESSING',
            meta={'stage': 'component_decision', 'progress': 30}
        )
        components = decide_components(nl_result, ui_framework)
        
        # Stage 4: Code Generation (50%)
        current_task.update_state(
            state='PROCESSING',
            meta={'stage': 'code_generation', 'progress': 50}
        )
        generated_code = generate_code(components, ui_framework)
        
        # Stage 5: Project Assembly (70%)
        current_task.update_state(
            state='PROCESSING',
            meta={'stage': 'project_assembly', 'progress': 70}
        )
        project_path = assemble_project(project_id, generated_code)
        
        # Stage 6: Create ZIP (90%)
        current_task.update_state(
            state='PROCESSING',
            meta={'stage': 'creating_zip', 'progress': 90}
        )
        zip_path = create_project_zip(project_path, project_id)
        
        # Stage 7: Update database (100%)
        current_task.update_state(
            state='PROCESSING',
            meta={'stage': 'finalizing', 'progress': 95}
        )
        
        project.status = 'completed'
        project.file_path = str(zip_path)
        project.download_url = f"/api/v1/download/{project_id}"
        project.completed_at = datetime.utcnow()
        project.file_size = os.path.getsize(zip_path)
        project.metadata = {
            'framework': ui_framework,
            'components': components,
            'generation_time': (datetime.utcnow() - project.created_at).total_seconds()
        }
        db.commit()
        
        # Log agent executions
        log_agent_executions(db, project_id, {
            'nl_processing': nl_result,
            'ui_selection': ui_framework,
            'component_decision': components
        })
        
        return {
            'project_id': project_id,
            'status': 'completed',
            'download_url': project.download_url,
            'file_size': project.file_size,
            'generation_time': project.metadata['generation_time']
        }
        
    except Exception as e:
        # Handle failure
        if project:
            project.status = 'failed'
            project.metadata = {'error': str(e)}
            db.commit()
        
        # Re-raise for Celery retry
        raise self.retry(exc=e)
        
    finally:
        db.close()


@celery_app.task(name='cleanup_old_projects', queue='projects')
def cleanup_old_projects(days: int = 7) -> Dict[str, int]:
    """오래된 프로젝트 정리"""
    
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Find old projects
        old_projects = db.query(Project).filter(
            Project.created_at < cutoff_date,
            Project.status.in_(['completed', 'failed'])
        ).all()
        
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
            'deleted_projects': deleted_count,
            'cleaned_size_mb': cleaned_size / (1024 * 1024)
        }
        
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name='send_project_notification', queue='emails')
def send_project_notification(
    user_email: str,
    project_id: str,
    status: str,
    download_url: Optional[str] = None
) -> bool:
    """프로젝트 완료 알림 전송"""
    
    from ..tasks.email_tasks import send_email
    
    if status == 'completed':
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


# Helper functions
def process_nl_input(query: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
    """NL 입력 처리 (실제 구현 필요)"""
    # TODO: Implement actual NL processing
    return {
        'intent': 'create_web_app',
        'features': requirements.get('features', []),
        'complexity': 'medium'
    }

def select_ui_framework(nl_result: Dict[str, Any]) -> str:
    """UI 프레임워크 선택 (실제 구현 필요)"""
    # TODO: Implement actual framework selection
    return 'react'

def decide_components(nl_result: Dict[str, Any], framework: str) -> list:
    """컴포넌트 결정 (실제 구현 필요)"""
    # TODO: Implement actual component decision
    return ['navbar', 'hero', 'features', 'footer']

def generate_code(components: list, framework: str) -> Dict[str, str]:
    """코드 생성 (실제 구현 필요)"""
    # TODO: Implement actual code generation
    return {
        'index.html': '<html>...</html>',
        'app.js': 'console.log("Hello");',
        'style.css': 'body { margin: 0; }'
    }

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
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in project_path.rglob('*'):
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
            input_data={'query': result},
            output_data=result,
            execution_time=1.0,  # Should be actual time
            created_at=datetime.utcnow()
        )
        db.add(execution)
    db.commit()