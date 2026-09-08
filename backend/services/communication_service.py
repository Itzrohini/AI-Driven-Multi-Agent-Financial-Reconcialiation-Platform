import os
import json
from datetime import datetime

MOCK_INBOX_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_inbox.json")

def send_mock_email(to_email: str, subject: str, body: str, payment_id: str):
    """
    Simulates sending an email to a customer and saving it in a mock inbox file.
    """
    inbox = []
    if os.path.exists(MOCK_INBOX_PATH):
        with open(MOCK_INBOX_PATH, "r", encoding="utf-8") as f:
            try:
                inbox = json.load(f)
            except json.JSONDecodeError:
                inbox = []
                
    email_record = {
        "id": f"msg_{datetime.utcnow().timestamp()}",
        "payment_id": payment_id,
        "to": to_email,
        "from": "ar-automation@globex.com",
        "subject": subject,
        "body": body,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "sent",
        "reply": None
    }
    
    inbox.append(email_record)
    
    # Save back
    os.makedirs(os.path.dirname(MOCK_INBOX_PATH), exist_ok=True)
    with open(MOCK_INBOX_PATH, "w", encoding="utf-8") as f:
        json.dump(inbox, f, indent=2)
        
    return f"Email successfully drafted and sent to {to_email}."

def get_mock_inbox():
    if os.path.exists(MOCK_INBOX_PATH):
        with open(MOCK_INBOX_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []
