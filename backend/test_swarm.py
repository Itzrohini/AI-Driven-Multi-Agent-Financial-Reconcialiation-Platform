import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables (OPENAI_API_KEY, etc.)
load_dotenv()

# We need to make sure the OPENAI_API_KEY is present
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY is not set. The Swarm agents need this to run.")
    print("Please set it in your backend/.env file or run: export OPENAI_API_KEY='your-key'")
    exit(1)

from workflows.swarm_orchestrator import run_swarm_workflow

def main():
    print("==================================================")
    print("Starting Swarm Agent Test...")
    print("==================================================")
    
    # We simulate a payment event message that would normally come from the Celery worker
    # We use 'Globex' as sender since MockERP has 'Globex Treasury'
    payment_message = "Process payment PAY-999 from Globex for 15000. No PO number was provided. Flags: []"
    
    print(f"User Request: {payment_message}\n")
    
    try:
        # Run the workflow
        result = run_swarm_workflow(payment_message)
        
        print("\n==================================================")
        print("Swarm Interaction History:")
        print("==================================================")
        
        # Iterate through the messages and print them cleanly
        for msg in result.messages:
            role = msg.get("role", "Unknown").upper()
            content = msg.get("content", "")
            name = msg.get("sender", role)  # 'sender' is injected by Swarm for agent messages
            
            # Print tool calls if any
            if msg.get("tool_calls"):
                for tool in msg["tool_calls"]:
                    func = tool.get("function", {})
                    print(f"[{name}] called tool -> {func.get('name')}({func.get('arguments')})")
            
            if content:
                print(f"[{name}]: {content}\n")
                
        print("==================================================")
        print("Final Result:")
        final_message = result.messages[-1].get("content", "No content found.")
        print(final_message)
        
        # Test Communication Agent if Missing Information
        import json
        try:
            json_str = final_message
            if json_str.startswith("```json"):
                json_str = json_str.strip("```json\n").strip("```").strip()
            decision_data = json.loads(json_str)
            
            if decision_data.get("decision") == "Missing Information":
                print("\n==================================================")
                print("Testing Communication Workflow...")
                print("==================================================")
                from workflows.swarm_orchestrator import run_communication_workflow
                history = [m["content"] for m in result.messages if "content" in m and m["content"]]
                
                comm_result = run_communication_workflow("PAY-999", history, decision_data.get("reasoning", ""))
                
                for msg in comm_result.messages:
                    if msg.get("tool_calls"):
                        for tool in msg["tool_calls"]:
                            func = tool.get("function", {})
                            print(f"[Communication Agent] called tool -> {func.get('name')}({func.get('arguments')})")
                    if msg.get("content"):
                        print(f"[Communication Agent]: {msg['content']}\n")
                        
        except Exception as e:
            print(f"Failed to parse or run communication workflow: {e}")
            
    except Exception as e:
        print(f"\nAn error occurred during swarm execution: {e}")

if __name__ == "__main__":
    main()
