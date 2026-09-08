# Agent Architecture

**Status:** COMPLETED

## Purpose
Document the specialized agent architecture.

## Findings
The system avoids a single, monolithic "God Agent" to enforce least-privilege access and improve accuracy. 

### 1. Investigation Agent (Orchestrator)
- **Role:** Breaks down the financial exception and coordinates the sub-agents.
- **Tools:** `delegate_task`

### 2. Payment Intelligence Agent
- **Role:** Analyzes the raw payment data (e.g., unstructured email text, wire details).
- **Tools:** `extract_remittance`, `find_customer`

### 3. AR/AP Ledger Agent
- **Role:** Interfaces with the mock ERP to check accounting balances.
- **Tools:** `get_open_invoices`, `get_credit_memos`

### 4. Risk/Fraud Agent
- **Role:** Evaluates transaction risk using traditional ML.
- **Tools:** `calculate_anomaly_score`

### 5. Treasury Agent
- **Role:** Assesses the cash flow impact of the exception.
- **Tools:** `calculate_liquidity_impact`

### 6. Policy (RAG) Agent
- **Role:** Retrieves relevant financial policies to ground the investigation.
- **Tools:** `search_corporate_policies`

### 7. Decision Agent
- **Role:** Synthesizes all findings into a final recommendation and confidence score.
- **Tools:** `execute_resolution`, `route_to_human`
