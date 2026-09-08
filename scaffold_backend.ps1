$BaseDir = "c:\Users\User\projects\Agent-to-Agent Financial Collaboration\backend"

$Files = @{}

$Files["requirements.txt"] = @'
fastapi==0.103.2
uvicorn==0.23.2
pydantic==2.4.2
langchain==0.0.310
langgraph==0.0.10
qdrant-client==1.6.2
scikit-learn==1.3.1
pandas==2.1.1
python-dotenv==1.0.0
'@

$Files["models\__init__.py"] = ""
$Files["models\domain.py"] = @'
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Customer(BaseModel):
    customer_id: str
    name: str
    risk_tier: str
    available_credit: float
    standing: str

class Invoice(BaseModel):
    invoice_id: str
    customer_id: str
    amount_due: float
    due_date: str
    status: str

class PaymentEvent(BaseModel):
    payment_id: str
    sender_name: str
    amount: float
    date: str
    remittance_text: Optional[str] = None
    method: str
    flags: List[str] = []

class InvestigationState(BaseModel):
    event_id: str
    status: str = "pending"
    payment_data: Optional[PaymentEvent] = None
    identified_customer: Optional[Customer] = None
    open_invoices: List[Invoice] = []
    credit_memos: float = 0.0
    risk_score: float = 0.0
    risk_factors: List[str] = []
    policies_cited: List[str] = []
    treasury_impact: str = ""
    decision: Optional[str] = None
    confidence: float = 0.0
    history: List[str] = []
'@

$Files["repositories\__init__.py"] = ""
$Files["repositories\mock_erp.py"] = @'
import json
import os
from models.domain import Customer, Invoice, PaymentEvent
from typing import List, Optional

# Mock ERP reads from the synthetic data generated in Phase 1
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

class MockERP:
    @staticmethod
    def get_customers() -> List[Customer]:
        path = os.path.join(DATA_DIR, "customers.json")
        if not os.path.exists(path): return []
        with open(path, "r") as f:
            return [Customer(**c) for c in json.load(f)]

    @staticmethod
    def get_invoices() -> List[Invoice]:
        path = os.path.join(DATA_DIR, "invoices.json")
        if not os.path.exists(path): return []
        with open(path, "r") as f:
            return [Invoice(**i) for i in json.load(f)]
            
    @staticmethod
    def get_payments() -> List[PaymentEvent]:
        path = os.path.join(DATA_DIR, "payments.json")
        if not os.path.exists(path): return []
        with open(path, "r") as f:
            return [PaymentEvent(**p) for p in json.load(f)]

    @classmethod
    def find_customer_by_name(cls, name: str) -> Optional[Customer]:
        name_lower = name.lower()
        for c in cls.get_customers():
            if c.name.lower() in name_lower or name_lower in c.name.lower():
                return c
        return None

    @classmethod
    def get_invoices_for_customer(cls, customer_id: str) -> List[Invoice]:
        return [i for i in cls.get_invoices() if i.customer_id == customer_id and i.status == "open"]
'@

$Files["agents\__init__.py"] = ""
$Files["agents\payment_agent.py"] = @'
from models.domain import InvestigationState
from repositories.mock_erp import MockERP

def payment_agent_node(state: dict) -> dict:
    # MVP: Mock payment extraction and customer ID
    history = state.get("history", [])
    payment_data = state.get("payment_data")
    if not payment_data:
        history.append("PaymentAgent: No payment data found.")
        return {"history": history}
    
    # Try to find customer
    customer = MockERP.find_customer_by_name(payment_data.sender_name)
    if customer:
        history.append(f"PaymentAgent: Identified customer {customer.customer_id} ({customer.name}).")
        return {"identified_customer": customer.dict(), "history": history}
    else:
        history.append("PaymentAgent: Could not identify customer.")
        return {"history": history}
'@

$Files["agents\ar_agent.py"] = @'
from repositories.mock_erp import MockERP

def ar_agent_node(state: dict) -> dict:
    history = state.get("history", [])
    customer = state.get("identified_customer")
    
    if not customer:
        history.append("ARAgent: No customer identified, cannot fetch ledger.")
        return {"history": history}
        
    invoices = MockERP.get_invoices_for_customer(customer["customer_id"])
    credit_memos = customer.get("available_credit", 0.0)
    
    history.append(f"ARAgent: Found {len(invoices)} open invoices and ${credit_memos} in credit memos.")
    
    return {
        "open_invoices": [i.dict() for i in invoices],
        "credit_memos": credit_memos,
        "history": history
    }
'@

$Files["agents\risk_agent.py"] = @'
def risk_agent_node(state: dict) -> dict:
    # MVP: Deterministic risk scoring based on flags and customer tier
    history = state.get("history", [])
    payment = state.get("payment_data", {})
    customer = state.get("identified_customer", {})
    
    flags = payment.get("flags", [])
    tier = customer.get("risk_tier", "unknown")
    
    score = 0.1 # Base low risk
    factors = []
    
    if "suspicious_origin" in flags:
        score += 0.5
        factors.append("suspicious_origin")
    
    if tier == "high":
        score += 0.4
        factors.append("high_risk_customer")
        
    history.append(f"RiskAgent: Calculated anomaly score of {score}.")
    
    return {
        "risk_score": score,
        "risk_factors": factors,
        "history": history
    }
'@

$Files["agents\policy_agent.py"] = @'
def policy_agent_node(state: dict) -> dict:
    # MVP: Hardcoded policy retrieval simulation (Mock RAG)
    history = state.get("history", [])
    payment = state.get("payment_data", {})
    invoices = state.get("open_invoices", [])
    credit_memos = state.get("credit_memos", 0.0)
    
    policies = []
    
    # Check for short pay scenario
    if invoices and payment:
        target_inv = invoices[0] # Simplification for MVP
        if payment["amount"] < target_inv["amount_due"]:
            if payment["amount"] + credit_memos == target_inv["amount_due"]:
                policies.append("AR-101: Apply credit memos to short pays under $5k.")
                history.append("PolicyAgent: Retrieved AR-101 (Credit Memo Application).")
            else:
                policies.append("RISK-202: Tolerance threshold exceeded.")
                history.append("PolicyAgent: Retrieved RISK-202 (Tolerance).")
                
    if not policies:
        history.append("PolicyAgent: No specific policies triggered.")
        
    return {
        "policies_cited": policies,
        "history": history
    }
'@

$Files["agents\decision_agent.py"] = @'
def decision_agent_node(state: dict) -> dict:
    history = state.get("history", [])
    risk_score = state.get("risk_score", 0.0)
    policies = state.get("policies_cited", [])
    
    if risk_score >= 0.7:
        decision = "Escalate: High Fraud Risk"
        confidence = 1.0
    elif "AR-101: Apply credit memos to short pays under $5k." in policies:
        decision = "Auto-Resolve: Apply Payment + Credit Memo"
        confidence = 0.96
    else:
        decision = "Human Review: Cannot automatically reconcile."
        confidence = 0.5
        
    history.append(f"DecisionAgent: Recommended {decision} with {confidence*100}% confidence.")
    
    return {
        "decision": decision,
        "confidence": confidence,
        "history": history
    }
'@

$Files["workflows\__init__.py"] = ""
$Files["workflows\graph.py"] = @'
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import operator
from agents.payment_agent import payment_agent_node
from agents.ar_agent import ar_agent_node
from agents.risk_agent import risk_agent_node
from agents.policy_agent import policy_agent_node
from agents.decision_agent import decision_agent_node

# Define State Type
class GraphState(TypedDict):
    event_id: str
    payment_data: dict
    identified_customer: Optional[dict]
    open_invoices: List[dict]
    credit_memos: float
    risk_score: float
    risk_factors: List[str]
    policies_cited: List[str]
    decision: Optional[str]
    confidence: float
    history: List[str]

# Create Graph
workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("payment", payment_agent_node)
workflow.add_node("ar_ledger", ar_agent_node)
workflow.add_node("risk", risk_agent_node)
workflow.add_node("policy", policy_agent_node)
workflow.add_node("decision", decision_agent_node)

# Add Edges (Linear MVP Workflow)
workflow.set_entry_point("payment")
workflow.add_edge("payment", "ar_ledger")
workflow.add_edge("ar_ledger", "risk")
workflow.add_edge("risk", "policy")
workflow.add_edge("policy", "decision")
workflow.add_edge("decision", END)

# Compile Graph
app = workflow.compile()
'@

$Files["api\__init__.py"] = ""
$Files["api\main.py"] = @'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from workflows.graph import app as workflow_app
from repositories.mock_erp import MockERP

app = FastAPI(title="Agent-to-Agent Financial Collaboration Platform")

class EventRequest(BaseModel):
    payment_id: str

@app.post("/api/events/webhook")
async def process_event(req: EventRequest):
    # 1. Fetch payment event from Mock ERP
    payments = MockERP.get_payments()
    payment = next((p for p in payments if p.payment_id == req.payment_id), None)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment event not found.")
        
    # 2. Initialize State
    initial_state = {
        "event_id": req.payment_id,
        "payment_data": payment.dict(),
        "history": [f"Event Received: {req.payment_id}"]
    }
    
    # 3. Execute LangGraph Workflow
    result = workflow_app.invoke(initial_state)
    
    return {
        "status": "completed",
        "decision": result.get("decision"),
        "confidence": result.get("confidence"),
        "history": result.get("history")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'@

# Ensure all parent directories exist
$Files.Keys | ForEach-Object {
    $filePath = Join-Path $BaseDir $_
    $dirPath = Split-Path $filePath
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Force -Path $dirPath | Out-Null
    }
}

# Write files
foreach ($key in $Files.Keys) {
    Set-Content -Path (Join-Path $BaseDir $key) -Value $Files[$key] -Encoding UTF8
}

Write-Host "Backend codebase scaffolded successfully."
