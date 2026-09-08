from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from repositories.erp_repository import ERPRepository
from rag.retriever import insert_historical_decision
import json

router = APIRouter(prefix="/api/hitl", tags=["HITL Queue"])

class ResolutionRequest(BaseModel):
    resolution: str  # e.g., "Approved", "Rejected"
    notes: str = ""

@router.get("/")
def get_queue():
    items = ERPRepository.get_hitl_queue()
    return {"queue": items}

@router.post("/{hitl_id}/resolve")
def resolve_item(hitl_id: str, req: ResolutionRequest):
    # Fetch item to get context for Memory (Phase 2)
    items = ERPRepository.get_hitl_queue()
    item = next((i for i in items if i.get("hitl_id") == hitl_id), None)
    
    # Phase 1: Mark as resolved in DB
    ERPRepository.resolve_hitl_item(hitl_id, req.resolution)
    
    # Phase 2: Generate embedding and store in Qdrant
    if item:
        context_str = json.dumps(item.get("context", {}))
        memory_text = f"Payment Details: {context_str}\nAgent Reasoning: {item.get('reasoning')}\nHuman Resolution: {req.resolution}\nNotes: {req.notes}"
        insert_historical_decision(memory_text, req.resolution, hitl_id)
        
    return {"status": "success", "hitl_id": hitl_id, "resolution": req.resolution}
