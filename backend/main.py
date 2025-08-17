#!/usr/bin/env python3
"""FastAPI backend server for T-Developer v2."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables from parent directory
load_dotenv(Path(__file__).parent.parent / ".env")

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

# Import existing agent infrastructure
from core.agent_manager import get_agent_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize agent manager
agent_manager = get_agent_manager()


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(agent_manager.start_worker())
    logger.info("Agent manager worker started")
    yield
    # Shutdown
    agent_manager.stop_worker()
    logger.info("Agent manager worker stopped")


# Create FastAPI app
app = FastAPI(
    title="T-Developer Backend",
    description="Self-evolving service factory API",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from api.routes.context import router as context_router

app.include_router(context_router)


# WebSocket manager for real-time updates
class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")


manager = ConnectionManager()

# Global state for evolution
evolution_state = {
    "status": "idle",  # idle, running, completed, failed
    "current_phase": None,
    "progress": 0,
    "results": [],
    "start_time": None,
    "end_time": None,
}

# Agent instances (simulated for now)
agents = {
    "research": {
        "id": "research-001",
        "name": "ResearchAgent",
        "type": "research",
        "status": "ready",
        "metrics": {"tasksCompleted": 42, "successRate": 95, "avgExecutionTime": 2.5},
        "lastActivity": datetime.now().isoformat(),
    },
    "planner": {
        "id": "planner-001",
        "name": "PlannerAgent",
        "type": "planner",
        "status": "ready",
        "metrics": {"tasksCompleted": 38, "successRate": 92, "avgExecutionTime": 1.8},
        "lastActivity": datetime.now().isoformat(),
    },
    "refactor": {
        "id": "refactor-001",
        "name": "RefactorAgent",
        "type": "refactor",
        "status": "ready",
        "metrics": {"tasksCompleted": 35, "successRate": 88, "avgExecutionTime": 3.2},
        "lastActivity": datetime.now().isoformat(),
    },
    "evaluator": {
        "id": "evaluator-001",
        "name": "EvaluatorAgent",
        "type": "evaluator",
        "status": "ready",
        "metrics": {"tasksCompleted": 40, "successRate": 98, "avgExecutionTime": 1.5},
        "lastActivity": datetime.now().isoformat(),
    },
}


# Request models
class EvolutionRequest(BaseModel):
    """Request to start evolution."""

    target_path: str
    max_cycles: int = 1
    focus_areas: list[str] = ["documentation", "quality", "performance"]
    dry_run: bool = True


class AgentTaskRequest(BaseModel):
    """Request to execute agent task."""

    task_type: str
    parameters: dict[str, Any]


# API Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "T-Developer Backend",
        "version": "2.0.0",
        "status": "running",
        "evolution_status": evolution_state["status"],
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "T-Developer v2 Backend",
        "timestamp": datetime.now().isoformat(),
        "evolution_status": evolution_state["status"],
        "agents_ready": sum(1 for a in agents.values() if a["status"] == "ready"),
    }


@app.get("/api/agents")
async def get_agents():
    """Get all agents."""
    # Get real agent status from agent manager
    agent_status = agent_manager.get_agent_status()

    # Add additional info for UI
    for agent in agent_status:
        agent["id"] = f"{agent['type']}-001"
        agent["status"] = "ready"
        agent["lastActivity"] = datetime.now().isoformat()

    return agent_status


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent."""
    for agent in agents.values():
        if agent["id"] == agent_id:
            return agent
    raise HTTPException(status_code=404, detail="Agent not found")


@app.post("/api/agents/{agent_id}/execute")
async def execute_agent_task(agent_id: str, request: AgentTaskRequest):
    """Execute task on specific agent."""
    agent = None
    for a in agents.values():
        if a["id"] == agent_id:
            agent = a
            break

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Update agent status
    agent["status"] = "busy"
    agent["lastActivity"] = datetime.now().isoformat()

    # Simulate task execution
    await asyncio.sleep(1)

    # Update metrics
    agent["metrics"]["tasksCompleted"] += 1
    agent["status"] = "ready"

    # Send WebSocket update
    await manager.broadcast(
        {
            "type": "agent:status",
            "agentId": agent_id,
            "status": agent["status"],
            "metrics": agent["metrics"],
        }
    )

    return {
        "success": True,
        "agent_id": agent_id,
        "task_type": request.task_type,
        "result": "Task completed successfully",
    }


@app.get("/api/evolution/status")
async def get_evolution_status():
    """Get current evolution status."""
    return evolution_state


@app.post("/api/evolution/start")
async def start_evolution(request: EvolutionRequest):
    """Start evolution cycle."""
    global evolution_state

    if evolution_state["status"] == "running":
        raise HTTPException(status_code=400, detail="Evolution already running")

    # Update state
    evolution_state = {
        "status": "running",
        "current_phase": "research",
        "progress": 0,
        "results": [],
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "target_path": request.target_path,
        "dry_run": request.dry_run,
    }

    # Start evolution in background
    asyncio.create_task(run_evolution_cycle(request))

    # Send WebSocket update
    await manager.broadcast({"type": "evolution:started", "status": evolution_state})

    return {"success": True, "message": "Evolution started", "status": evolution_state}


@app.post("/api/evolution/stop")
async def stop_evolution():
    """Stop evolution cycle."""
    global evolution_state

    if evolution_state["status"] != "running":
        raise HTTPException(status_code=400, detail="No evolution running")

    evolution_state["status"] = "stopped"
    evolution_state["end_time"] = datetime.now().isoformat()

    # Send WebSocket update
    await manager.broadcast({"type": "evolution:stopped", "status": evolution_state})

    return {"success": True, "message": "Evolution stopped", "status": evolution_state}


@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics."""
    total_tasks = sum(a["metrics"]["tasksCompleted"] for a in agents.values())
    avg_success = sum(a["metrics"]["successRate"] for a in agents.values()) / len(agents)

    return {
        "agents": {
            "total": len(agents),
            "ready": sum(1 for a in agents.values() if a["status"] == "ready"),
            "busy": sum(1 for a in agents.values() if a["status"] == "busy"),
        },
        "tasks": {"completed": total_tasks, "success_rate": avg_success},
        "evolution": {
            "cycles_completed": len(evolution_state.get("results", [])),
            "current_status": evolution_state["status"],
        },
    }


@app.get("/api/metrics/realtime")
async def get_realtime_metrics():
    """Get real-time metrics."""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": 45.2,  # Simulated
        "memory_usage": 62.8,  # Simulated
        "active_tasks": sum(1 for a in agents.values() if a["status"] == "busy"),
        "queue_size": 0,
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)

    # Send initial connection message
    await websocket.send_json(
        {
            "type": "connection",
            "message": "Connected to T-Developer backend",
            "timestamp": datetime.now().isoformat(),
        }
    )

    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()

            # Echo back for now
            await websocket.send_json(
                {"type": "echo", "data": data, "timestamp": datetime.now().isoformat()}
            )

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)


# Evolution cycle implementation using evolution engine
async def run_evolution_cycle(request: EvolutionRequest):
    """Run complete evolution cycle using the evolution engine."""
    global evolution_state

    try:
        from core.evolution_engine import EvolutionConfig, EvolutionEngine

        # Create evolution config
        config = EvolutionConfig(
            target_path=request.target_path,
            max_cycles=request.max_cycles,
            focus_areas=request.focus_areas,
            dry_run=request.dry_run,
        )

        # Create evolution engine with broadcast callback
        engine = EvolutionEngine(broadcast_callback=manager.broadcast)

        # Run evolution
        results = await engine.run_evolution(config)

        # Update global state
        evolution_state["status"] = "completed"
        evolution_state["current_phase"] = None
        evolution_state["progress"] = 100
        evolution_state["end_time"] = datetime.now().isoformat()
        evolution_state["results"] = [
            {
                "cycle": r.cycle_number,
                "research": r.research_result,
                "plan": r.plan_result,
                "implementation": r.implementation_result,
                "evaluation": r.evaluation_result,
                "metrics": r.metrics,
            }
            for r in results
        ]

        await manager.broadcast(
            {
                "type": "evolution:completed",
                "status": evolution_state,
                "results": evolution_state["results"],
            }
        )

        logger.info(f"Evolution completed: {len(results)} cycles")

    except Exception as e:
        logger.error(f"Evolution cycle failed: {e}")
        evolution_state["status"] = "failed"
        evolution_state["error"] = str(e)

        await manager.broadcast({"type": "evolution:failed", "error": str(e)})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
