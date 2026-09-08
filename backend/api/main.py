import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from repositories.erp_repository import ERPRepository
from worker import celery_app, process_payment_event_task
from api.documents import router as documents_router
from api.hitl import router as hitl_router
import redis.asyncio as aioredis
import os
import json
import asyncio

app = FastAPI(title="Agent-to-Agent Financial Collaboration Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(hitl_router)

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = aioredis.from_url(redis_url)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("swarm_events")
    
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_text(message["data"].decode("utf-8"))
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        await pubsub.unsubscribe("swarm_events")
        await redis_client.close()

class EventRequest(BaseModel):
    payment_id: str

@app.post("/api/events/webhook", status_code=202)
async def process_event(req: EventRequest):
    # 1. Fetch payment event from Mock ERP to validate it exists
    payments = ERPRepository.get_payments()
    print("AVAILABLE PAYMENTS:", [p.payment_id for p in payments], "REQUESTED:", req.payment_id)
    payment = next((p for p in payments if p.payment_id == req.payment_id), None)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment event not found.")
        
    # 2. Dispatch the Celery Task
    task = process_payment_event_task.delay(req.payment_id)
    
    # 3. Return 202 Accepted immediately with the task_id
    return {
        "status": "accepted",
        "message": "Payment exception is being investigated autonomously.",
        "task_id": task.id
    }

@app.get("/api/debug/payments")
def debug_payments():
    return [p.payment_id for p in ERPRepository.get_payments()]

@app.get("/api/investigations/{task_id}")
async def get_investigation_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.state == 'PENDING':
        return {"status": "pending"}
    elif task.state != 'FAILURE':
        return task.result
    else:
        return {"status": "failed", "error": str(task.info)}

@app.get("/api/inbox")
def get_inbox():
    from services.communication_service import get_mock_inbox
    return get_mock_inbox()

class ReplyRequest(BaseModel):
    payment_id: str
    message: str

@app.post("/api/inbox/reply")
async def reply_to_inbox(req: ReplyRequest):
    # Retrieve pending investigation to make sure it exists
    pending = ERPRepository.get_pending_investigation(req.payment_id)
    if not pending:
        raise HTTPException(status_code=404, detail="Pending investigation not found.")
        
    # Dispatch the Celery task to resume
    from worker import resume_payment_event_task
    task = resume_payment_event_task.delay(req.payment_id, req.message)
    
    return {
        "status": "accepted",
        "message": "Reply received. Resuming investigation.",
        "task_id": task.id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
