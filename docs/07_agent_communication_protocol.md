# Agent Communication Protocol

**Status:** COMPLETED

## Purpose
Document the communication protocol between agents.

## Findings
Agents communicate asynchronously by updating a shared state object managed by LangGraph.

### State Schema (JSON)
```json
{
  "event_id": "evt_123",
  "investigation_status": "in_progress",
  "current_assignee": "risk_agent",
  "context": {
    "payment_amount": 12500,
    "invoice_amount": 15000
  },
  "agent_responses": {
    "ar_agent": {
      "findings": "Customer has a $2500 credit memo.",
      "timestamp": "2026-08-25T10:00:00Z"
    },
    "policy_agent": {
      "cited_rule": "AR-101",
      "text": "Apply credit memos to short pays under $5k."
    }
  },
  "decision": null
}
```
### Conflict Resolution
If agent outputs conflict, the Decision Agent applies strict weighting: Risk overrides AR; Policy overrides Risk.
