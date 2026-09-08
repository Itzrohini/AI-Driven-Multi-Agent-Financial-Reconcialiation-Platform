import pytest
from agents.decision_agent import decision_agent_node

def test_decision_agent_auto_resolve():
    state = {
        "history": [],
        "risk_score": 0.1,
        "policies_cited": ["AR-101: Apply credit memos to short pays under $5k."]
    }
    result = decision_agent_node(state)
    
    assert result["decision"] == "Auto-Resolve: Apply Payment + Credit Memo"
    assert result["confidence"] == 0.96

def test_decision_agent_escalate_high_risk():
    state = {
        "history": [],
        "risk_score": 0.8,
        "policies_cited": []
    }
    result = decision_agent_node(state)
    
    assert "Escalate" in result["decision"]
    assert result["confidence"] == 1.0

def test_decision_agent_human_review():
    state = {
        "history": [],
        "risk_score": 0.2,
        "policies_cited": []
    }
    result = decision_agent_node(state)
    
    assert "Human Review" in result["decision"]
    assert result["confidence"] == 0.5
