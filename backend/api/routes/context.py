"""SharedContextStore API endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException
from core.shared_context import get_context_store

router = APIRouter(prefix="/api/context", tags=["context"])


@router.get("/current")
async def get_current_context() -> dict[str, Any]:
    """Get current evolution context."""
    store = get_context_store()
    context = await store.get_context()

    if not context:
        raise HTTPException(status_code=404, detail="No active evolution context")

    return {
        "evolution_id": context.evolution_id,
        "created_at": context.created_at.isoformat(),
        "target_path": context.target_path,
        "focus_areas": context.focus_areas,
        "current_phase": context.current_phase,
        "status": context.status,
        "has_data": {
            "original_analysis": bool(context.original_analysis),
            "external_research": bool(context.external_research),
            "improvement_plan": bool(context.improvement_plan),
            "implementation_log": bool(context.implementation_log),
            "evaluation_results": bool(context.evaluation_results),
        },
    }


@router.get("/comparison/{evolution_id}")
async def get_comparison_data(evolution_id: str) -> dict[str, Any]:
    """Get comparison data for three-way evaluation."""
    store = get_context_store()
    comparison = await store.get_comparison_data(evolution_id)

    if not comparison:
        raise HTTPException(status_code=404, detail=f"Evolution {evolution_id} not found")

    return comparison


@router.post("/export/{evolution_id}")
async def export_context(evolution_id: str) -> dict[str, Any]:
    """Export evolution context to file."""
    store = get_context_store()

    # Get context to verify it exists
    context = await store.get_context(evolution_id)
    if not context:
        raise HTTPException(status_code=404, detail=f"Evolution {evolution_id} not found")

    export_path = await store.export_context(evolution_id)

    if not export_path:
        raise HTTPException(status_code=500, detail="Failed to export context")

    import os

    file_size = os.path.getsize(export_path) if os.path.exists(export_path) else 0

    return {
        "export_path": export_path,
        "size_bytes": file_size,
        "download_url": f"/api/context/download/{os.path.basename(export_path)}",
    }


@router.get("/list")
async def list_contexts() -> dict[str, Any]:
    """List all evolution contexts."""
    store = get_context_store()
    contexts = await store.get_all_contexts()

    return {"contexts": contexts, "total": len(contexts)}


@router.get("/details/{evolution_id}")
async def get_context_details(evolution_id: str) -> dict[str, Any]:
    """Get detailed context information."""
    store = get_context_store()
    context = await store.get_context(evolution_id)

    if not context:
        raise HTTPException(status_code=404, detail=f"Evolution {evolution_id} not found")

    return context.to_dict()


@router.delete("/{evolution_id}")
async def delete_context(evolution_id: str) -> dict[str, Any]:
    """Delete an evolution context."""
    store = get_context_store()
    context = await store.get_context(evolution_id)

    if not context:
        raise HTTPException(status_code=404, detail=f"Evolution {evolution_id} not found")

    # Delete from store
    async with store.lock:
        if evolution_id in store.contexts:
            del store.contexts[evolution_id]
            if store.current_evolution_id == evolution_id:
                store.current_evolution_id = None

    return {"status": "deleted", "evolution_id": evolution_id}
