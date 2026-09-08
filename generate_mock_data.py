import json
import os
import random
from datetime import datetime, timedelta
import pymongo

DATA_DIR = "data"
POLICIES_DIR = "policies"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(POLICIES_DIR, exist_ok=True)

def generate_customers():
    return [
        {
            "customer_id": "CUS-1001",
            "name": "Acme Corp",
            "industry": "Manufacturing",
            "risk_tier": "low",
            "available_credit": 0.0,
            "standing": "good"
        },
        {
            "customer_id": "CUS-1002",
            "name": "Globex Inc",
            "industry": "Technology",
            "risk_tier": "medium",
            "available_credit": 2500.0, # They have a credit memo
            "standing": "good"
        },
        {
            "customer_id": "CUS-1003",
            "name": "Initech",
            "industry": "Software",
            "risk_tier": "high",
            "available_credit": 0.0,
            "standing": "poor",
            "notes": "History of late payments and unexplained short pays."
        }
    ]

def generate_invoices():
    now = datetime.now()
    return [
        {
            "invoice_id": "INV-5001",
            "customer_id": "CUS-1001",
            "amount_due": 10000.0,
            "due_date": (now - timedelta(days=5)).isoformat(),
            "status": "open"
        },
        {
            "invoice_id": "INV-5002",
            "customer_id": "CUS-1002",
            "amount_due": 15000.0,
            "due_date": (now + timedelta(days=10)).isoformat(),
            "status": "open"
        },
        {
            "invoice_id": "INV-5003",
            "customer_id": "CUS-1003",
            "amount_due": 50000.0,
            "due_date": (now - timedelta(days=30)).isoformat(),
            "status": "open"
        }
    ]

def generate_payments():
    now = datetime.now()
    return [
        # Scenario 1: Clean Match
        {
            "payment_id": "PAY-9001",
            "sender_name": "Acme Corp Accounts Payable",
            "amount": 10000.0,
            "date": now.isoformat(),
            "remittance_text": "Payment for INV-5001",
            "method": "ACH"
        },
        # Scenario 2: Short Pay with Credit Memo (The main example scenario)
        {
            "payment_id": "PAY-9002",
            "sender_name": "Globex Treasury",
            "amount": 12500.0,
            "date": now.isoformat(),
            "remittance_text": "Invoice 5002 payment", # Missing INV prefix, partial amount
            "method": "WIRE"
        },
        # Scenario 3: High Risk / Unexplained
        {
            "payment_id": "PAY-9003",
            "sender_name": "Unknown Entity XYZ",
            "amount": 48000.0,
            "date": now.isoformat(),
            "remittance_text": "For Initech",
            "method": "WIRE",
            "flags": ["suspicious_origin", "amount_mismatch"]
        }
    ]

def generate_policies():
    policies = {
        "AR_Resolution_Policy.md": """# Accounts Receivable Resolution Policy

## 1. Short Payments
If a customer submits a payment that is less than the invoice amount due (a "short pay"), the system must investigate the reason.

### 1.1 Credit Memo Application
If the customer has an outstanding credit memo (available_credit) on their account, and the short pay amount exactly matches the invoice amount minus the credit memo amount, the credit memo should be applied to resolve the invoice.
- **Rule ID**: AR-101
- **Condition**: `payment_amount == invoice_amount - available_credit`
- **Action**: Apply payment and credit memo to invoice. Auto-resolve if customer is in good standing and credit memo is <= $5,000.

### 1.2 Unexplained Short Pays
If a short pay cannot be explained by a credit memo or documented dispute, it must be flagged for human review. If the customer risk tier is "high", escalate immediately.
""",
        "Fraud_Risk_Policy.md": """# Fraud and Risk Policy

## 1. High Risk Transactions
Any transaction flagged with suspicious origins or from a customer in a "high" risk tier must NEVER be auto-resolved. 
- **Rule ID**: RISK-201
- **Action**: Force human review regardless of AI confidence score.

## 2. Tolerance Thresholds
Payments that differ from the invoice amount by less than $10.00 can be automatically written off as a tolerance discrepancy.
- **Rule ID**: RISK-202
- **Action**: Auto-resolve (Write-off).
"""
    }
    
    for filename, content in policies.items():
        with open(os.path.join(POLICIES_DIR, filename), "w") as f:
            f.write(content)

def main():
    customers = generate_customers()
    invoices = generate_invoices()
    payments = generate_payments()
    
    # Write to local JSON for backup/debugging
    with open(os.path.join(DATA_DIR, "customers.json"), "w") as f:
        json.dump(customers, f, indent=2)
        
    with open(os.path.join(DATA_DIR, "invoices.json"), "w") as f:
        json.dump(invoices, f, indent=2)
        
    with open(os.path.join(DATA_DIR, "payments.json"), "w") as f:
        json.dump(payments, f, indent=2)
        
    # Generate Policies for Qdrant RAG
    generate_policies()
    
    # Push to MongoDB
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = pymongo.MongoClient(mongo_uri)
    db = client.financial_collaboration
    
    db.erp_customers.delete_many({})
    db.erp_invoices.delete_many({})
    db.erp_payments.delete_many({})
    
    db.erp_customers.insert_many(customers)
    db.erp_invoices.insert_many(invoices)
    db.erp_payments.insert_many(payments)
    
    print(f"Successfully generated mock data in {DATA_DIR}/ and policies in {POLICIES_DIR}/")
    print(f"Successfully pushed ERP data to MongoDB collections: erp_customers, erp_invoices, erp_payments")

if __name__ == "__main__":
    main()
