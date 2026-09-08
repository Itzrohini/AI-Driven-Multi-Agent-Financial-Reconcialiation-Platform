import json
import os
import pymongo
from datetime import datetime
import uuid
from models.domain import Customer, Invoice, PaymentEvent
from typing import List, Optional

# Connect to MongoDB
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = pymongo.MongoClient(MONGO_URI)
db = client.financial_collaboration

class ERPRepository:
    @staticmethod
    def get_customers() -> List[Customer]:
        docs = db.erp_customers.find({})
        return [Customer(**doc) for doc in docs]

    @staticmethod
    def get_invoices() -> List[Invoice]:
        docs = db.erp_invoices.find({})
        return [Invoice(**doc) for doc in docs]
            
    @staticmethod
    def get_payments() -> List[PaymentEvent]:
        docs = db.erp_payments.find({})
        return [PaymentEvent(**doc) for doc in docs]

    @classmethod
    def find_customer_by_name(cls, name: str) -> Optional[Customer]:
        if not name:
            return None
        # Extract the root company name (e.g. 'Globex' from 'Globex Treasury')
        search_term = name.split()[0]
        
        # Use native MongoDB regex search for case-insensitive lookup
        doc = db.erp_customers.find_one({"name": {"$regex": search_term, "$options": "i"}})
        if doc:
            return Customer(**doc)
        return None

    @classmethod
    def get_invoices_for_customer(cls, customer_id: str) -> List[Invoice]:
        # Native MongoDB exact match
        docs = db.erp_invoices.find({"customer_id": customer_id, "status": "open"})
        return [Invoice(**doc) for doc in docs]

    @staticmethod
    def add_to_hitl_queue(task_id: str, payment_id: str, context: dict, reasoning: str):
        item = {
            "hitl_id": task_id,
            "payment_id": payment_id,
            "context": context,
            "reasoning": reasoning,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        db.hitl_queue.insert_one(item)

    @staticmethod
    def get_hitl_queue() -> List[dict]:
        docs = db.hitl_queue.find({"status": "pending"})
        results = []
        for doc in docs:
            doc.pop("_id", None)
            results.append(doc)
        return results

    @staticmethod
    def resolve_hitl_item(hitl_id: str, resolution: str):
        db.hitl_queue.update_one(
            {"hitl_id": hitl_id},
            {"$set": {"status": "resolved", "resolution": resolution, "resolved_at": datetime.utcnow().isoformat()}}
        )

    @staticmethod
    def save_pending_investigation(payment_id: str, history: list, reasoning: str):
        db.pending_investigations.update_one(
            {"payment_id": payment_id},
            {
                "$set": {
                    "history": history,
                    "reasoning": reasoning,
                    "status": "awaiting_customer",
                    "updated_at": datetime.utcnow().isoformat()
                }
            },
            upsert=True
        )

    @staticmethod
    def get_pending_investigation(payment_id: str):
        doc = db.pending_investigations.find_one({"payment_id": payment_id})
        if doc:
            doc.pop("_id", None)
        return doc
