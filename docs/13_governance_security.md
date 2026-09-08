# Governance & Security

**Status:** COMPLETED

## Purpose
Document permissions, RBAC, and security policies.

## Findings
### Agent Least Privilege
Agents are strictly scoped. The Risk Agent cannot call the `get_open_invoices` tool. Most importantly, only the Decision Agent (and only under specific auto-resolve conditions) can call the `execute_financial_transaction` tool.

### PII Redaction
Before any unstructured remittance data is sent to an external LLM API, a lightweight local regex/NLP filter redacts Social Security Numbers and raw bank account numbers.

### Auditability
Every tool call, policy citation, and state change is logged to the `audit_logs` MongoDB collection with a trace ID.
