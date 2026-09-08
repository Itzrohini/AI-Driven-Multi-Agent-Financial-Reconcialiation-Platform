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

class PolicyDocument(BaseModel):
    document_type: str = "policy"
    customer_id: Optional[str] = None
    company_name: Optional[str] = None
    effective_date: Optional[str] = None
    text: str
    source: str