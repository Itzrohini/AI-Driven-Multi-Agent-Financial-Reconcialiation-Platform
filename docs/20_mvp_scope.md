# MVP Scope

**Status:** COMPLETED

## Purpose
Document the minimum viable prototype scope.

## Findings
The MVP focuses on proving the Agent-to-Agent communication pattern on a constrained problem.

### In Scope
1. **Scenario:** Handling "Short Pays" and "Missing Remittances".
2. **Agents:** Orchestrator, Payment, AR, Risk, Policy, Decision. (Treasury excluded for MVP to reduce scope).
3. **Data:** Synthetic static JSON files (`data/synthetic/`) simulating the ERP and Payment events.
4. **RAG:** Markdown-based policies queried via a local Qdrant container.
5. **Human-in-the-Loop:** Basic REST endpoint to log human approval.

### Out of Scope
- Real ERP integrations (e.g., SAP, Oracle).
- Actual live payment stream ingestion (Kafka).
- Advanced auth (OAuth2/SSO).
- Production Kubernetes deployment.
