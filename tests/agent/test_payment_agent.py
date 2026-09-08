import pytest
from agents.payment_agent import payment_agent_node

def test_payment_agent_finds_customer():
    # Setup state with mock payment
    state = {
        "history": [],
        "payment_data": type('obj', (object,), {
            "sender_name": "Globex Treasury", 
            "amount": 12500.0,
            "payment_id": "PAY-9002"
        })
    }
    
    # We rely on mock_erp data here. Assuming Globex exists.
    result = payment_agent_node(state)
    
    assert "identified_customer" in result
    assert result["identified_customer"]["name"] == "Globex Inc"
    assert "PaymentAgent: Identified customer" in result["history"][-1]

def test_payment_agent_missing_data():
    state = {"history": [], "payment_data": None}
    result = payment_agent_node(state)
    assert "identified_customer" not in result
    assert "No payment data found" in result["history"][-1]
