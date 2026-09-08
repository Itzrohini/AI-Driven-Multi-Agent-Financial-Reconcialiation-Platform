import pytest
from workflows.graph import app
from repositories.mock_erp import MockERP

def test_happy_path_workflow():
    # Scenario: Clean Match
    payment = MockERP.get_payments()[0] # PAY-9001, Acme Corp
    
    initial_state = {
        "event_id": payment.payment_id,
        "payment_data": payment.dict(),
        "history": ["Event Received"]
    }
    
    result = app.invoke(initial_state)
    
    # Ensure it went through all steps
    history = result.get("history", [])
    
    # In a clean match without credit memos, it should likely go to Human Review right now
    # because our MVP policy agent only handles AR-101 (credit memos).
    assert "DecisionAgent:" in history[-1]
    assert "confidence" in result
