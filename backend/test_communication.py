import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from workflows.swarm_orchestrator import run_communication_workflow
from services.communication_service import get_mock_inbox

def main():
    print("==================================================")
    print("Testing Communication Agent Directly")
    print("==================================================")
    
    payment_id = "PAY-DEMO"
    reasoning = "We are missing a valid Purchase Order number for this $15,000 transaction. Section 4.2 of the contract strictly requires a PO for invoices over $10,000."
    history = [
        "Payment Agent found customer CUS-1002 (Globex)",
        "AR Agent found Open Invoice INV-5002 for $15,000",
        "Risk Agent reported Risk Score 0.1",
        "Policy Agent found Contract_Globex.md which says PO required over $10k"
    ]
    
    print(f"Triggering workflow for {payment_id}...")
    try:
        result = run_communication_workflow(payment_id, history, reasoning)
        
        print("\nCommunication Agent Result:")
        for msg in result.messages:
            if msg.get("tool_calls"):
                for tool in msg["tool_calls"]:
                    func = tool.get("function", {})
                    print(f"-> Called tool: {func.get('name')}({func.get('arguments')})")
            if msg.get("content"):
                print(f"-> Agent: {msg['content']}")
                
        print("\nChecking mock_inbox.json...")
        inbox = get_mock_inbox()
        if inbox:
            latest = inbox[-1]
            print("\nLatest Email Sent:")
            print(f"To: {latest['to']}")
            print(f"Subject: {latest['subject']}")
            print(f"Body: \n{latest['body']}")
        else:
            print("Inbox is empty!")
            
    except Exception as e:
        print(f"Error testing Communication Agent: {e}")

if __name__ == "__main__":
    main()
