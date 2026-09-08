from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractedField(BaseModel):
    value: str | float | int | list | dict = Field(description="The extracted value")
    confidence: float = Field(description="Confidence score between 0 and 1")
    source: Optional[str] = Field(None, description="Page number or section")

class InvoiceLineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total: float

class InvoiceData(BaseModel):
    document_type: str = "INVOICE"
    invoice_number: str
    customer_id: Optional[str] = None
    customer_name: str
    invoice_date: str
    due_date: Optional[str] = None
    currency: str
    subtotal: float
    tax: float
    total_amount: float
    line_items: List[InvoiceLineItem] = []
    payment_terms: Optional[str] = None
    confidence: float = Field(description="Overall extraction confidence between 0 and 1")

class InvoiceReference(BaseModel):
    invoice_number: str
    allocated_amount: float

class RemittanceData(BaseModel):
    document_type: str = "REMITTANCE"
    payment_reference: str
    customer_id: Optional[str] = None
    customer_name: str
    payment_amount: float
    currency: str
    payment_date: str
    invoice_references: List[InvoiceReference] = []
    unallocated_amount: float = 0.0
    confidence: float = Field(description="Overall extraction confidence between 0 and 1")

class BankStatementTransaction(BaseModel):
    transaction_date: str
    value_date: Optional[str] = None
    transaction_reference: Optional[str] = None
    description: str
    debit: float = 0.0
    credit: float = 0.0
    balance: Optional[float] = None
    counterparty: Optional[str] = None

class BankStatementData(BaseModel):
    document_type: str = "BANK_STATEMENT"
    account_number: str
    currency: str
    statement_period: Optional[str] = None
    transactions: List[BankStatementTransaction] = []
    confidence: float = Field(description="Overall extraction confidence between 0 and 1")

class PolicyData(BaseModel):
    document_type: str = "POLICY"
    policy_id: Optional[str] = None
    policy_title: str
    policy_content: str = Field(description="The full raw text of the policy")
    confidence: float = Field(description="Overall extraction confidence between 0 and 1")

class ClassificationResult(BaseModel):
    document_type: str = Field(description="One of: INVOICE, REMITTANCE, BANK_STATEMENT, POLICY, CUSTOMER_STATEMENT, UNKNOWN")
