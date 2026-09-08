import os
import hashlib
import shutil
from datetime import datetime
from pymongo import MongoClient
import uuid

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "storage")

client = MongoClient(MONGO_URI)
db = client.financial_collaboration
source_documents = db.source_documents

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

def generate_file_hash(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def is_duplicate(file_hash: str) -> bool:
    doc = source_documents.find_one({"checksum": file_hash})
    return doc is not None

def save_and_register_document(upload_file) -> dict:
    doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
    file_extension = os.path.splitext(upload_file.filename)[1]
    storage_path = os.path.join(STORAGE_DIR, f"{doc_id}{file_extension}")
    
    # Save file to object storage mock
    with open(storage_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    file_hash = generate_file_hash(storage_path)
    
    if is_duplicate(file_hash):
        os.remove(storage_path) # Clean up
        raise ValueError("Duplicate document detected.")
        
    file_size = os.path.getsize(storage_path)
    
    metadata = {
        "document_id": doc_id,
        "file_name": upload_file.filename,
        "storage_location": storage_path,
        "checksum": file_hash,
        "file_size": file_size,
        "uploaded_at": datetime.utcnow().isoformat(),
        "processing_status": "UPLOADED",
        "document_type": "UNKNOWN",
        "extraction_confidence": 0.0,
        "extracted_data": None
    }
    
    source_documents.insert_one(metadata)
    # Remove _id for JSON serialization
    metadata.pop("_id")
    return metadata

def update_document_status(doc_id: str, status: str, updates: dict = None):
    update_fields = {"processing_status": status}
    if updates:
        update_fields.update(updates)
        
    source_documents.update_one(
        {"document_id": doc_id},
        {"$set": update_fields}
    )

def get_document(doc_id: str) -> dict:
    doc = source_documents.find_one({"document_id": doc_id})
    if doc:
        doc.pop("_id", None)
    return doc
