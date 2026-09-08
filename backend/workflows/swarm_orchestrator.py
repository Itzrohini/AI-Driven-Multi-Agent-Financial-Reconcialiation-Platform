import os
import openai
from swarm import Swarm, Agent
from repositories.erp_repository import ERPRepository
from rag.retriever import search_policies, search_historical_decisions
from services.communication_service import send_mock_email

def strip_nones(obj):
    if isinstance(obj, dict):
        return {k: strip_nones(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [strip_nones(item) for item in obj]
    return obj

# Patch OpenAI Client for Gemini Compatibility Bug
class PatchedChatCompletions:
    def __init__(self, original_chat_completions):
        self.original = original_chat_completions
        
    def create(self, *args, **kwargs):
        import time
        if 'messages' in kwargs:
            # Gemini strictly rejects `null` values for optional fields like refusal, audio, function_call, etc.
            kwargs['messages'] = strip_nones(kwargs['messages'])
            # It also requires 'content' to at least be an empty string instead of missing if it's an assistant message
            for m in kwargs['messages']:
                if m.get('role') == 'assistant' and 'content' not in m:
                    m['content'] = ""
                    
        # Auto-retry for 429 Rate Limits (Gemini Free Tier)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return self.original.create(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"\n[Rate Limit Hit] Waiting 20 seconds before retrying... (Attempt {attempt+1}/3)")
                    time.sleep(20)
                else:
                    raise e

import json
import redis
import os

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

def publish_event(event_type: str, data: dict):
    try:
        payload = {"type": event_type, "data": data}
        redis_client.publish("swarm_events", json.dumps(payload))
    except:
        pass

def transfer_to_ar_agent():
    publish_event("agent_transfer", {"from": "Payment Agent", "to": "Accounts Receivable Agent"})
    return ar_agent

def transfer_to_risk_agent():
    publish_event("agent_transfer", {"from": "Accounts Receivable Agent", "to": "Risk Agent"})
    return risk_agent

def transfer_to_policy_agent():
    publish_event("agent_transfer", {"from": "Risk Agent", "to": "Policy Agent"})
    return policy_agent

def transfer_to_decision_agent():
    publish_event("agent_transfer", {"from": "Policy Agent", "to": "Decision Agent"})
    return decision_agent

def query_past_decisions(flags: str, amount: str) -> str:
    """Check how humans previously resolved similar escalated payments."""
    query = f"Payment with flags {flags} and amount {amount}"
    results = search_historical_decisions(query)
    return "\n".join(results) if results else "No historical human decisions found for similar cases."

# --- Tools ---
def get_customer_by_name(name: str) -> str:
    """Look up a customer in the ERP by their name."""
    customer = ERPRepository.find_customer_by_name(name)
    if customer:
        return f"Customer Found: ID={customer.customer_id}, Name={customer.name}, RiskTier={customer.risk_tier}, Credit={customer.available_credit}"
    return "Customer not found."

def get_customer_invoices(customer_id: str) -> str:
    """Retrieve open invoices for a specific customer ID."""
    invoices = ERPRepository.get_invoices_for_customer(customer_id)
    if not invoices:
        return "No open invoices found."
    return f"Found {len(invoices)} invoices: " + ", ".join([f"Inv {i.invoice_id} (Due: {i.amount_due})" for i in invoices])

def query_policies(query: str, customer_id: str = None) -> str:
    """Search the vector database for internal policies or customer contracts related to the payment situation."""
    results = search_policies(query, customer_id=customer_id)
    return "\n".join(results) if results else "No relevant policies found."

def assess_risk(flags: str, tier: str) -> str:
    """Calculate risk score based on anomaly flags and customer tier."""
    score = 0.1
    factors = []
    if "suspicious" in flags.lower():
        score += 0.5
        factors.append("suspicious_origin")
    if tier.lower() == "high":
        score += 0.4
        factors.append("high_risk_customer")
    return f"Risk Score: {score}, Factors: {factors}"

# --- Agents ---
payment_agent = Agent(
    name="Payment Agent",
    model="gemini-3.6-flash",
    instructions="""You are the Payment Agent. Your job is to extract payment information and identify the customer in the ERP.
    1. Use 'get_customer_by_name' to find the customer.
    2. Once identified, summarize the customer details.
    3. Transfer to the AR Agent.""",
    functions=[get_customer_by_name, transfer_to_ar_agent]
)

ar_agent = Agent(
    name="Accounts Receivable Agent",
    model="gemini-3.6-flash",
    instructions="""You are the Accounts Receivable Agent.
    1. Using the identified customer ID, use 'get_customer_invoices' to find their open invoices.
    2. Summarize their available credit and open invoices.
    3. Transfer to the Risk Agent.""",
    functions=[get_customer_invoices, transfer_to_risk_agent]
)

risk_agent = Agent(
    name="Risk Agent",
    model="gemini-3.6-flash",
    instructions="""You are the Risk Agent.
    1. Use 'assess_risk' to evaluate the transaction's anomaly risk. Pass any payment flags and the customer's risk tier.
    2. Note the final risk score.
    3. Transfer to the Policy Agent.""",
    functions=[assess_risk, transfer_to_policy_agent]
)

policy_agent = Agent(
    name="Policy Agent",
    model="gemini-3.6-flash",
    instructions="""You are the Policy Agent.
    1. Use 'query_policies' to look up relevant corporate rules or customer-specific contracts. If a customer ID was identified by earlier agents, be sure to pass it as 'customer_id' to retrieve their specific contract.
    2. Use 'query_past_decisions' to check how humans handled similar cases.
    3. Summarize the policies, contracts, and historical precedents.
    4. Transfer to the Decision Agent.""",
    functions=[query_policies, query_past_decisions, transfer_to_decision_agent]
)

decision_agent = Agent(
    name="Decision Agent",
    model="gemini-3.6-flash",
    instructions="""You are the final Decision Agent.
    Based on all the information gathered by the previous agents (Customer, Invoices, Risk Score, and Policies/Contracts), make a final determination on how to process the payment.
    Respond strictly with a JSON object in this format:
    {
      "decision": "Auto-Approve" | "Review" | "Reject" | "Missing Information",
      "confidence": <float between 0 and 1>,
      "reasoning": "<detailed explanation of the decision>",
      "evidence": ["<Source Document A>", "<Section B>"],
      "requires_human_review": <true/false>
    }
    Do not wrap the JSON in markdown code blocks if possible, just output raw JSON.
    """,
    functions=[]
)

def draft_email_tool(to_email: str, subject: str, body: str, payment_id: str) -> str:
    """Drafts and sends an email to the customer regarding missing information."""
    return send_mock_email(to_email, subject, body, payment_id)

communication_agent = Agent(
    name="Communication Agent",
    model="gemini-3.6-flash",
    instructions="""You are the Communication Agent. 
    Your job is to draft professional, concise emails to customers to request missing information (like a Purchase Order number or remittance advice) that prevented us from processing their payment.
    You will be provided with the Swarm's investigation history and the Decision Agent's reasoning.
    1. Identify the customer's email (make one up like contact@<companydomain>.com if not provided).
    2. Draft a polite email explaining the situation and asking for the missing info.
    3. Use the 'draft_email_tool' to send it.
    """,
    functions=[draft_email_tool]
)


def run_swarm_workflow(payment_message: str):
    """Entry point for the swarm workflow."""
    print("Starting Swarm Workflow...")
    
    # Lazy initialize client and apply the Gemini patch
    client = openai.OpenAI()
    
    if os.getenv("LANGCHAIN_API_KEY"):
        try:
            from langsmith import wrappers
            client = wrappers.wrap_openai(client)
            print("LangSmith tracing enabled.")
        except ImportError:
            pass
            
    client.chat.completions = PatchedChatCompletions(client.chat.completions)
    swarm_client = Swarm(client=client)
    
    response = swarm_client.run(
        agent=payment_agent,
        messages=[{"role": "user", "content": payment_message}],
        debug=True
    )
    return response

def run_communication_workflow(payment_id: str, history: list, reasoning: str):
    """Entry point for drafting communication when information is missing."""
    print(f"Starting Communication Workflow for {payment_id}...")
    
    client = openai.OpenAI()
    
    if os.getenv("LANGCHAIN_API_KEY"):
        try:
            from langsmith import wrappers
            client = wrappers.wrap_openai(client)
        except ImportError:
            pass
            
    client.chat.completions = PatchedChatCompletions(client.chat.completions)
    swarm_client = Swarm(client=client)
    
    context_message = f"Please draft an email for payment {payment_id}. The Decision Agent concluded we are missing information. Reasoning: {reasoning}\n\nInvestigation History:\n" + "\n".join(history)
    
    response = swarm_client.run(
        agent=communication_agent,
        messages=[{"role": "user", "content": context_message}],
        debug=True
    )
    return response
