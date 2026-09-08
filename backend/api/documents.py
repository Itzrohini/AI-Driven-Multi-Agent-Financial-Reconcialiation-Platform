from fastapi import APIRouter, UploadFile, File, HTTPException
from services.document_service import save_and_register_document, get_document, update_document_status
from worker import process_document_task

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        metadata = save_and_register_document(file)
        
        # Dispatch background task for text extraction and intelligence
        process_document_task.delay(metadata["document_id"])
        
        return metadata
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/{document_id}")
async def get_document_status(document_id: str):
    doc = get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.post("/{document_id}/review")
async def review_document(document_id: str, action: str):
    # 'action' can be 'approve' or 'reject'
    doc = get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if action == "approve":
        update_document_status(document_id, "COMPLETED", {"review_notes": "Approved by human"})
        return {"status": "approved"}
    else:
        update_document_status(document_id, "REJECTED", {"review_notes": "Rejected by human"})
        return {"status": "rejected"}
