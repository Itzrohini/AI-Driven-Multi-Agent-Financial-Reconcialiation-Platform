import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from celery import Celery
from workflows.swarm_orchestrator import run_swarm_workflow
from repositories.erp_repository import ERPRepository
from services.document_service import get_document, update_document_status
from services.pdf_extraction_service import extract_text_from_pdf, classify_document, extract_structured_data

# Configure Celery to use Redis (from docker-compose or local)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "investigation_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="process_payment_event")
def process_payment_event_task(payment_id: str):
    """
    Background task to process a payment event using the Swarm Orchestrator.
    """
    payments = ERPRepository.get_payments()
    payment = next((p for p in payments if p.payment_id == payment_id), None)
    
    if not payment:
        return {"status": "error", "detail": f"Payment {payment_id} not found."}
        
    payment_message = f"Process payment {payment_id} from {payment.sender_name} for {payment.amount}. Flags: {payment.flags}"
    
    # Execute the Swarm workflow
    import redis, json, os
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    try:
        redis_client.publish("swarm_events", json.dumps({"type": "workflow_start", "data": {"payment_id": payment_id}}))
    except: pass
    
    result = run_swarm_workflow(payment_message)
    final_message = result.messages[-1]["content"] if result.messages else "No result"
    history = [m["content"] for m in result.messages if "content" in m and m["content"]]
    
    try:
        redis_client.publish("swarm_events", json.dumps({"type": "workflow_end", "data": {"payment_id": payment_id, "decision": final_message}}))
    except: pass
    
    # Parse the Decision Agent's output to check if human review is needed
    import json
    try:
        json_str = final_message
        if json_str.startswith("```json"):
            json_str = json_str.strip("```json\n").strip("```").strip()
        decision_data = json.loads(json_str)
        
        needs_review = decision_data.get("requires_human_review", False) or decision_data.get("decision") == "Review"
        
        if needs_review:
            context = {
                "payment_id": payment_id,
                "amount": payment.amount,
                "sender": payment.sender_name,
                "flags": payment.flags,
                "history": history,
                "evidence": decision_data.get("evidence", []),
                "confidence": decision_data.get("confidence", 0.0)
            }
            task_id = celery_app.current_task.request.id if celery_app.current_task else payment_id
            ERPRepository.add_to_hitl_queue(task_id, payment_id, context, decision_data.get("reasoning", ""))
            
        if decision_data.get("decision") == "Missing Information":
            ERPRepository.save_pending_investigation(payment_id, history, decision_data.get("reasoning", ""))
            from workflows.swarm_orchestrator import run_communication_workflow
            comm_result = run_communication_workflow(payment_id, history, decision_data.get("reasoning", ""))
            
    except Exception as e:
        print(f"Failed to parse decision JSON or add to hitl queue: {e}")
    
    return {
        "status": "completed",
        "decision": final_message,
        "history": history
    }

@celery_app.task(name="resume_payment_event")
def resume_payment_event_task(payment_id: str, reply_text: str):
    pending = ERPRepository.get_pending_investigation(payment_id)
    if not pending:
        return {"status": "error", "detail": f"Pending investigation for {payment_id} not found."}
        
    payments = ERPRepository.get_payments()
    payment = next((p for p in payments if p.payment_id == payment_id), None)
    
    history = pending.get("history", [])
    payment_message = f"We are resuming an investigation for payment {payment_id}. \n\nHere is the previous investigation history:\n"
    payment_message += "\n".join(history)
    payment_message += f"\n\nThe customer has replied with the following information:\n{reply_text}\n\nPlease evaluate this new information and make a final decision."
    
    import redis, json, os
    redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    try:
        redis_client.publish("swarm_events", json.dumps({"type": "workflow_start", "data": {"payment_id": payment_id}}))
    except: pass
    
    result = run_swarm_workflow(payment_message)
    final_message = result.messages[-1]["content"] if result.messages else "No result"
    new_history = [m["content"] for m in result.messages if "content" in m and m["content"]]
    
    try:
        redis_client.publish("swarm_events", json.dumps({"type": "workflow_end", "data": {"payment_id": payment_id, "decision": final_message}}))
    except: pass
    
    try:
        json_str = final_message
        if json_str.startswith("```json"):
            json_str = json_str.strip("```json\n").strip("```").strip()
        decision_data = json.loads(json_str)
        
        needs_review = decision_data.get("requires_human_review", False) or decision_data.get("decision") == "Review"
        
        if needs_review:
            context = {
                "payment_id": payment_id,
                "amount": payment.amount if payment else 0,
                "sender": payment.sender_name if payment else "Unknown",
                "flags": payment.flags if payment else [],
                "history": history + ["--- RESUMED ---"] + new_history,
                "evidence": decision_data.get("evidence", []),
                "confidence": decision_data.get("confidence", 0.0)
            }
            task_id = celery_app.current_task.request.id if celery_app.current_task else f"resume-{payment_id}"
            ERPRepository.add_to_hitl_queue(task_id, payment_id, context, decision_data.get("reasoning", ""))
            
    except Exception as e:
        print(f"Failed to parse decision JSON after resume: {e}")
        
    return {
        "status": "resumed",
        "decision": final_message
    }

@celery_app.task(name="process_document")
def process_document_task(doc_id: str):
    doc = get_document(doc_id)
    if not doc:
        return {"status": "failed", "error": "Document not found"}
        
    storage_path = doc.get("storage_location")
    
    try:
        update_document_status(doc_id, "EXTRACTING")
        text = extract_text_from_pdf(storage_path)
        
        if not text:
            update_document_status(doc_id, "FAILED", {"error": "No text could be extracted"})
            return {"status": "failed"}
            
        update_document_status(doc_id, "CLASSIFYING")
        doc_type = classify_document(text)
        update_document_status(doc_id, "VALIDATING_DATA", {"document_type": doc_type})
        
        if doc_type in ["UNKNOWN"]:
            update_document_status(doc_id, "AWAITING_REVIEW", {"error": "Unknown document type"})
            return {"status": "awaiting_review"}
            
        structured_data = extract_structured_data(text, doc_type)
        confidence = structured_data.get("confidence", 0.0)
        
        if confidence < 0.8:
            update_document_status(doc_id, "AWAITING_REVIEW", {
                "extracted_data": structured_data,
                "extraction_confidence": confidence
            })
            return {"status": "awaiting_review"}
            
        update_document_status(doc_id, "PERSISTING", {
            "extracted_data": structured_data,
            "extraction_confidence": confidence
        })
        
        # Here we map to MongoDB domain collections (invoices, payments, etc.)
        # and trigger process_payment_event_task if it's a REMITTANCE
        
        if doc_type == "REMITTANCE":
            # For MVP, trigger the payment event workflow immediately
            ERPRepository.get_payments()
            new_payment = {
                "payment_id": structured_data.get("payment_reference", f"PAY-{doc_id}"),
                "sender_name": structured_data.get("customer_name", "Unknown"),
                "amount": structured_data.get("payment_amount", 0.0),
                "date": structured_data.get("payment_date", "2026-08-25"),
                "remittance_text": f"Parsed from {doc_id}",
                "method": "PDF_EXTRACTION",
                "flags": []
            }
            with open(os.path.join(os.path.dirname(__file__), "..", "data", "payments.json"), "a") as f:
                pass # Simplistic append for demo
                
            process_payment_event_task.delay(new_payment["payment_id"])
            
        update_document_status(doc_id, "COMPLETED")
        return {"status": "completed", "doc_type": doc_type}
        
    except Exception as e:
        update_document_status(doc_id, "FAILED", {"error": str(e)})
        return {"status": "failed", "error": str(e)}
