"""🧬 T-Developer Main API - Optimized"""
import asyncio
import json
import logging
import os
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="T-Developer API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class ProjectRequest(BaseModel):
    input: str
    requirements: Optional[Dict] = {}
    options: Optional[Dict] = {}


class ProjectResponse(BaseModel):
    success: bool
    project_id: str
    message: str
    download_url: Optional[str] = None
    preview_url: Optional[str] = None


# Global state
projects = {}
PROJECTS_DIR = Path("/tmp/t_developer_projects")
PROJECTS_DIR.mkdir(exist_ok=True)


# Core Pipeline Integration
async def run_agent_pipeline(input_text: str, requirements: Dict, options: Dict) -> Dict:
    """Run the 9-agent pipeline"""
    try:
        # Import agents
        from src.agents.unified.assembly.agent import AssemblyAgent
        from src.agents.unified.component_decision.agent import ComponentDecisionAgent
        from src.agents.unified.download.agent import DownloadAgent
        from src.agents.unified.generation.agent import GenerationAgent
        from src.agents.unified.match_rate.agent import MatchRateAgent
        from src.agents.unified.nl_input.agent import NLInputAgent
        from src.agents.unified.parser.agent import ParserAgent
        from src.agents.unified.search.agent import SearchAgent
        from src.agents.unified.ui_selection.agent import UISelectionAgent

        # Pipeline execution
        pipeline_result = {}

        # Stage 1: NL Input Processing
        nl_agent = NLInputAgent()
        nl_result = await nl_agent.process(input_text, requirements)
        pipeline_result["nl_processed"] = nl_result

        # Stage 2: UI Selection
        ui_agent = UISelectionAgent()
        ui_result = await ui_agent.process(nl_result, requirements)
        pipeline_result["ui_selected"] = ui_result

        # Stage 3: Parsing
        parser_agent = ParserAgent()
        parsed_result = await parser_agent.process(nl_result, ui_result)
        pipeline_result["parsed"] = parsed_result

        # Stage 4: Component Decision
        comp_agent = ComponentDecisionAgent()
        components = await comp_agent.process(parsed_result, requirements)
        pipeline_result["components"] = components

        # Stage 5: Match Rate Analysis
        match_agent = MatchRateAgent()
        match_analysis = await match_agent.process(components, requirements)
        pipeline_result["match_analysis"] = match_analysis

        # Stage 6: Search & Discovery
        search_agent = SearchAgent()
        search_results = await search_agent.process(match_analysis, components)
        pipeline_result["search_results"] = search_results

        # Stage 7: Code Generation
        gen_agent = GenerationAgent()
        generated_code = await gen_agent.process(search_results, components)
        pipeline_result["generated_code"] = generated_code

        # Stage 8: Assembly
        assembly_agent = AssemblyAgent()
        assembled_project = await assembly_agent.process(generated_code, components)
        pipeline_result["assembled"] = assembled_project

        # Stage 9: Download Package
        download_agent = DownloadAgent()
        download_result = await download_agent.process(assembled_project)
        pipeline_result["download"] = download_result

        return {
            "success": True,
            "pipeline_result": pipeline_result,
            "final_output": download_result,
        }

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return {"success": False, "error": str(e)}


def create_project_zip(project_data: Dict, project_id: str) -> str:
    """Create downloadable project ZIP"""
    project_dir = PROJECTS_DIR / project_id
    project_dir.mkdir(exist_ok=True)

    # Write project files
    if "files" in project_data:
        for file_info in project_data["files"]:
            file_path = project_dir / file_info["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_info["content"])

    # Create ZIP
    zip_path = PROJECTS_DIR / f"{project_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in project_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(project_dir)
                zipf.write(file_path, arcname)

    return str(zip_path)


# API Endpoints
@app.get("/")
async def root():
    return {"message": "T-Developer API", "version": "2.0.0", "status": "active"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/generate", response_model=ProjectResponse)
async def generate_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    """Main project generation endpoint"""
    project_id = str(uuid.uuid4())

    try:
        # Store project info
        projects[project_id] = {
            "status": "processing",
            "created_at": datetime.now(),
            "input": request.input,
            "requirements": request.requirements,
            "options": request.options,
        }

        # Run pipeline
        result = await run_agent_pipeline(request.input, request.requirements, request.options)

        if result["success"]:
            # Create ZIP
            zip_path = create_project_zip(result["final_output"], project_id)

            # Update project
            projects[project_id].update(
                {
                    "status": "completed",
                    "result": result,
                    "zip_path": zip_path,
                    "download_url": f"/download/{project_id}",
                    "preview_url": f"/preview/{project_id}",
                }
            )

            return ProjectResponse(
                success=True,
                project_id=project_id,
                message="Project generated successfully",
                download_url=f"/download/{project_id}",
                preview_url=f"/preview/{project_id}",
            )
        else:
            projects[project_id].update({"status": "failed", "error": result.get("error")})
            raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))

    except Exception as e:
        logger.error(f"Generation error: {e}")
        if project_id in projects:
            projects[project_id]["status"] = "failed"
            projects[project_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{project_id}")
async def get_project_status(project_id: str):
    """Get project generation status"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]
    return {
        "project_id": project_id,
        "status": project["status"],
        "created_at": project["created_at"].isoformat(),
        "download_url": project.get("download_url"),
        "preview_url": project.get("preview_url"),
    }


@app.get("/download/{project_id}")
async def download_project(project_id: str):
    """Download project ZIP file"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]
    if project["status"] != "completed":
        raise HTTPException(status_code=400, detail="Project not ready for download")

    zip_path = project.get("zip_path")
    if not zip_path or not Path(zip_path).exists():
        raise HTTPException(status_code=404, detail="Project file not found")

    return FileResponse(
        zip_path, media_type="application/zip", filename=f"t_developer_project_{project_id}.zip"
    )


@app.get("/preview/{project_id}")
async def preview_project(project_id: str):
    """Preview project structure"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]
    if project["status"] != "completed":
        raise HTTPException(status_code=400, detail="Project not ready for preview")

    result = project.get("result", {})
    final_output = result.get("final_output", {})

    return {
        "project_id": project_id,
        "files": final_output.get("files", []),
        "structure": final_output.get("structure", {}),
        "summary": final_output.get("summary", {}),
    }


@app.get("/projects")
async def list_projects():
    """List all projects"""
    project_list = []
    for pid, project in projects.items():
        project_list.append(
            {
                "project_id": pid,
                "status": project["status"],
                "created_at": project["created_at"].isoformat(),
                "input": project["input"][:100] + "..."
                if len(project["input"]) > 100
                else project["input"],
            }
        )

    return {"projects": project_list, "total": len(project_list)}


@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete project and cleanup files"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    # Cleanup files
    project_dir = PROJECTS_DIR / project_id
    zip_path = PROJECTS_DIR / f"{project_id}.zip"

    if project_dir.exists():
        import shutil

        shutil.rmtree(project_dir)

    if zip_path.exists():
        zip_path.unlink()

    del projects[project_id]
    return {"message": "Project deleted successfully"}


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500, content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
