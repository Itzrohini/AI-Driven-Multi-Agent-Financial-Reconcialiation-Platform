$BaseDir = "c:\Users\User\projects\Agent-to-Agent Financial Collaboration"

$Docs = @{}

$Docs["05_solution_architecture.md"] = @'
# Solution Architecture

**Status:** COMPLETED

## Purpose
Document the high-level solution architecture.

## Findings
The platform leverages a hybrid architecture combining deterministic rules, traditional machine learning, and LLM-powered agentic workflows.

### Core Components
1. **API Gateway & Event Ingestion (FastAPI):** Receives incoming financial events (e.g., unreconciled payments) via asynchronous webhooks.
2. **Orchestration Engine (LangGraph):** Manages the state and routing of the multi-agent workflow. It maintains the investigation context and triggers specialized agents.
3. **Specialized Agents:** Domain-specific LLMs (or deterministic functions) that perform narrow tasks (Payment matching, AR Ledger analysis, Risk scoring, Policy retrieval, Treasury impact).
4. **Vector Database (Qdrant):** Stores embeddings of corporate financial policies for Retrieval-Augmented Generation (RAG).
5. **Operational Database (MongoDB):** Stores the raw financial events, the complete agent investigation state (LangGraph state persistence), and human feedback.
6. **ML Engine:** Traditional machine learning models (e.g., Isolation Forests via scikit-learn) for fast, deterministic anomaly detection.

### Flow
Financial Event -> API -> MongoDB -> LangGraph Orchestrator -> Agent Collaboration -> Decision Engine -> Auto-Resolve API Call OR Human Review Queue.
'@

$Docs["06_agent_architecture.md"] = @'
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
'@

$Docs["07_agent_communication_protocol.md"] = @'
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
'@

$Docs["08_langgraph_architecture.md"] = @'
# LangGraph Architecture

**Status:** COMPLETED

## Purpose
Document the state graph and workflows.

## Findings
The system uses LangGraph to define a cyclic, stateful workflow.

### Nodes
- **ReceiveEvent:** Initializes the graph state.
- **Node_Payment, Node_AR, Node_Risk, Node_Treasury, Node_Policy:** The specialized agent nodes that append their findings to the state.
- **Node_Decision:** The final reasoning step.
- **Node_HumanReview:** A breakpoint node where the graph halts execution until a human provides input.

### Edges
- The Investigation Agent acts as the router, creating conditional edges (`if task == 'check_risk', route to Node_Risk`).
- All agent nodes route back to the Investigation Agent until the Investigation Agent determines all data is gathered, at which point it routes to `Node_Decision`.
'@

$Docs["09_rag_architecture.md"] = @'
# RAG Architecture

**Status:** COMPLETED

## Purpose
Document the retrieval-augmented generation architecture.

## Findings
The Policy Agent uses RAG to ensure decisions comply with corporate rules, preventing hallucinations.

### Architecture
1. **Ingestion:** Corporate markdown documents (AR Policy, Fraud Policy) are split into 500-token chunks.
2. **Embeddings:** Converted to vector embeddings.
3. **Database:** Stored in Qdrant (local/Dockerized).
4. **Retrieval:** The Policy Agent generates a query based on the exception context (e.g., "short pay with credit memo"). Qdrant returns the top-K relevant chunks.
5. **Prompting:** The LLM is strictly instructed: "You must ONLY recommend actions explicitly supported by the retrieved policies. You must cite the Rule ID."
'@

$Docs["10_ml_architecture.md"] = @'
# ML Architecture

**Status:** COMPLETED

## Purpose
Document the traditional ML architecture.

## Findings
The project adheres to the principle: **Do not use LLMs for everything.**

### Anomaly Detection (Risk Agent)
- **Problem:** LLMs are poor at numerical anomaly detection and too slow for real-time risk scoring.
- **Solution:** We use an `Isolation Forest` (via scikit-learn) trained on historical payment data.
- **Input:** Payment amount, frequency, customer risk tier, geographic origin.
- **Output:** A normalized anomaly score (0.0 to 1.0).

This traditional ML score is appended to the LangGraph state, where the LLM Decision Agent uses it as context to make its final recommendation.
'@

$Docs["11_decision_engine.md"] = @'
# Decision Engine

**Status:** COMPLETED

## Purpose
Document the decision engine and confidence scoring.

## Findings
The Decision Agent calculates a confidence score based on the completeness of the evidence and alignment with policies.

### Logic Matrix
- **Confidence >= 95% AND ML Risk Score < 0.3:** Auto-Resolve (e.g., automatically apply payment + credit memo).
- **Confidence 80-94% OR ML Risk Score 0.3-0.7:** Route to Human Approval Queue.
- **Confidence < 80% OR ML Risk Score > 0.7:** Escalate / Reject.

### Hard Overrides
In financial systems, safety is paramount. If the `Fraud_Risk_Policy` dictates a rejection, the LLM cannot override it, regardless of its internal confidence.
'@

$Docs["12_human_in_the_loop.md"] = @'
# Human-in-the-Loop

**Status:** COMPLETED

## Purpose
Document the workflows for human review and escalation.

## Findings
When the LangGraph routes to the `Node_HumanReview`, the execution is paused.

### The Analyst Experience
An analyst opens the internal portal and sees:
1. The original exception.
2. The AI's **Reasoning Summary**.
3. The **Evidence** (cited policy documents, ERP data).
4. The AI's **Recommendation** (e.g., "Write off $5.00 tolerance").

The analyst clicks "Approve" or "Reject". This unpauses the LangGraph to finalize the transaction, and writes the decision to the `feedback_store` for future evaluation.
'@

$Docs["13_governance_security.md"] = @'
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
'@

$Docs["14_api_architecture.md"] = @'
# API Architecture

**Status:** COMPLETED

## Purpose
Document the REST API endpoints and schemas.

## Findings
Built with FastAPI.

### Key Endpoints
- `POST /api/events/webhook`: Receives incoming payment events. Triggers async LangGraph execution.
- `GET /api/investigations/{id}`: Returns the current state/findings of an ongoing or completed investigation.
- `POST /api/investigations/{id}/approve`: Endpoint for the human-in-the-loop to approve an AI recommendation.
- `GET /api/forecasts/liquidity`: Endpoint for the Treasury dashboard to pull the calculated cash impact of unresolved exceptions.
'@

$Docs["15_database_architecture.md"] = @'
# Database Architecture

**Status:** COMPLETED

## Purpose
Document the database collections and schemas.

## Findings
MongoDB is used for its flexibility in storing varied JSON structures (like LangGraph state).

### Key Collections
1. `financial_events`: The raw incoming triggers.
2. `investigations`: The persisted LangGraph state.
3. `policies`: Metadata for the RAG documents.
4. `human_feedback`: Stores AI recommendation vs Human final action.
5. `audit_logs`: Immutable logs of every agent action.
'@

$Docs["16_event_architecture.md"] = @'
# Event Architecture

**Status:** COMPLETED

## Purpose
Document the asynchronous event-driven architecture.

## Findings
To ensure the system scales without blocking, financial events are processed asynchronously.

1. **Ingestion:** Event arrives via webhook. FastAPI returns `202 Accepted` immediately.
2. **Queueing:** Event ID is pushed to a background task queue (FastAPI BackgroundTasks or a lightweight Redis queue for the MVP).
3. **Execution:** A worker picks up the event and invokes the LangGraph orchestrator.
'@

$Docs["17_evaluation_framework.md"] = @'
# Evaluation Framework

**Status:** COMPLETED

## Purpose
Document the metrics and evaluation framework.

## Findings
We will build a test suite of ~50 synthetic financial exceptions to evaluate the system before production.

### Metrics
1. **Auto-Resolution Accuracy:** Did the AI correctly resolve the "happy path" exceptions?
2. **Escalation Precision:** Did the AI correctly flag high-risk transactions without auto-resolving?
3. **Groundedness / Hallucination Rate:** Did the Policy Agent cite a real Rule ID for every policy-based decision?
4. **Tool Call Accuracy:** Did agents call the correct tools with the correct arguments?
'@

$Docs["18_observability.md"] = @'
# Observability

**Status:** COMPLETED

## Purpose
Document tracing, logging, and monitoring.

## Findings
Debugging multi-agent systems is notoriously difficult.
- **LangSmith:** We will integrate LangSmith (or an equivalent open-source tracing tool) to visually inspect the LLM prompts, token usage, and tool outputs for every step in the LangGraph.
- **Structured Logging:** All backend logs will use JSON format, including the `trace_id` of the investigation, allowing easy searching across API and Agent logs.
'@

$Docs["19_end_to_end_workflow.md"] = @'
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
'@

foreach ($key in $Docs.Keys) {
    Set-Content -Path (Join-Path $BaseDir "docs\$key") -Value $Docs[$key] -Encoding UTF8
}

$Mmds = @{}

$Mmds["system_architecture.mmd"] = @'
```mermaid
flowchart TD
    subgraph External
        ERP[Mock ERP]
        PaymentGateway[Payment Streams]
    end

    subgraph API Layer
        FastAPI[FastAPI Gateway]
    end

    subgraph Orchestration
        LangGraph[LangGraph State Engine]
    end

    subgraph Agents
        OrchAgent[Investigation Agent]
        PayAgent[Payment Agent]
        ARAgent[AR/AP Agent]
        RiskAgent[Risk Agent - ML]
        TreasuryAgent[Treasury Agent]
        PolicyAgent[Policy Agent - RAG]
        DecAgent[Decision Agent]
    end

    subgraph Data
        Mongo[(MongoDB)]
        Qdrant[(Qdrant Vector DB)]
    end

    PaymentGateway -->|Webhook| FastAPI
    FastAPI -->|Start Workflow| LangGraph
    LangGraph --> OrchAgent
    OrchAgent --> PayAgent & ARAgent & RiskAgent & TreasuryAgent & PolicyAgent
    PayAgent & ARAgent & RiskAgent & TreasuryAgent & PolicyAgent --> DecAgent
    
    PolicyAgent <--> Qdrant
    FastAPI <--> Mongo
    DecAgent -->|Auto-Resolve| ERP
```
'@

$Mmds["agent_architecture.mmd"] = @'
```mermaid
flowchart TD
    A[Investigation Orchestrator] --> B[Payment Intelligence]
    A --> C[AR/AP Ledger]
    A --> D[Risk & Fraud]
    A --> E[Treasury]
    A --> F[Policy & Rules]
    
    B & C & D & E & F --> G{Decision Engine}
    
    G -->|High Confidence| H[Auto Execute Tool]
    G -->|Medium Confidence| I[Human Review Queue]
    G -->|Low Confidence / High Risk| J[Escalation Queue]
```
'@

$Mmds["langgraph_workflow.mmd"] = @'
```mermaid
stateDiagram-v2
    [*] --> ReceiveEvent
    ReceiveEvent --> Orchestrator
    
    Orchestrator --> PaymentNode : if needs payment data
    Orchestrator --> ARNode : if needs ledger data
    Orchestrator --> RiskNode : if needs risk score
    Orchestrator --> PolicyNode : if needs rules
    Orchestrator --> TreasuryNode : if needs cash impact
    
    PaymentNode --> Orchestrator
    ARNode --> Orchestrator
    RiskNode --> Orchestrator
    PolicyNode --> Orchestrator
    TreasuryNode --> Orchestrator
    
    Orchestrator --> DecisionNode : if investigation complete
    
    DecisionNode --> AutoResolve : confidence >= 95%
    DecisionNode --> HumanReview : confidence < 95%
    
    HumanReview --> ExecuteHumanAction
    AutoResolve --> AuditLog
    ExecuteHumanAction --> AuditLog
    
    AuditLog --> [*]
```
'@

$Mmds["event_architecture.mmd"] = @'
```mermaid
sequenceDiagram
    participant Webhook as Payment Gateway
    participant API as FastAPI
    participant Queue as Task Queue
    participant Worker as LangGraph Worker
    participant DB as MongoDB

    Webhook->>API: POST /event (Exception)
    API->>DB: Create Event Record
    API->>Queue: Push Task (event_id)
    API-->>Webhook: 202 Accepted
    
    Queue->>Worker: Pop Task
    Worker->>Worker: Run Agent Workflow
    Worker->>DB: Update Investigation State
```
'@

$Mmds["deployment_architecture.mmd"] = @'
```mermaid
flowchart TD
    subgraph Docker Compose
        API[FastAPI App container]
        Worker[Celery/Background Worker container]
        Mongo[(MongoDB container)]
        Qdrant[(Qdrant container)]
        Redis[(Redis container for queues)]
    end
    
    API <--> Mongo
    Worker <--> Mongo
    Worker <--> Qdrant
    Worker <--> LLM[External LLM API]
    API <--> Redis
    Worker <--> Redis
```
'@

foreach ($key in $Mmds.Keys) {
    Set-Content -Path (Join-Path $BaseDir "architecture\$key") -Value $Mmds[$key] -Encoding UTF8
}

Write-Host "Architecture docs and diagrams populated successfully."
