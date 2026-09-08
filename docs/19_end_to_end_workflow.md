# End-to-End Workflow

**Status:** COMPLETED

## Purpose
Document a complete realistic workflow example.

## Findings
### Scenario: Unreconciled Partial Payment
1. **Event:** Customer Globex Inc sends a $12,500 wire. ERP cannot match it because Invoice 5002 is for $15,000.
2. **Trigger:** Event webhook hits FastAPI. LangGraph is instantiated.
3. **Investigation Agent:** Asks Payment Agent to ID customer. Payment Agent IDs Globex.
4. **Investigation Agent:** Asks AR Agent for ledger status. AR Agent finds a $2,500 credit memo.
5. **Investigation Agent:** Asks Risk Agent to score. Risk Agent returns 0.1 (Low Risk).
6. **Investigation Agent:** Asks Policy Agent for rules on credit memos. Policy Agent returns "Rule AR-101: Apply credit memo to short pays under $5k."
7. **Investigation Agent:** Asks Treasury Agent for impact. Treasury Agent calculates "$2,500 cash flow deficit vs forecast."
8. **Decision Agent:** Correlates findings. Calculates 96% confidence. Recommends: "Auto-Resolve: Apply $12,500 payment + $2,500 credit memo to Invoice 5002."
9. **Execution:** API call made to mock ERP. State marked as `resolved`.
