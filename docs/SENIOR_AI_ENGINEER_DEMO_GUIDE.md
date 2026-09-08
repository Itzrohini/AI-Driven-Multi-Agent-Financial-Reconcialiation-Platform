# Agent-to-Agent Financial Collaboration

### 30-Second Project Summary
This project is an event-driven, multi-agent financial collaboration system designed to investigate payment anomalies such as short-pays, unexplained payments, and policy-related exceptions. An incoming financial event is processed asynchronously via a webhook, investigated sequentially by a chain of specialized AI agents, grounded against enterprise policies using RAG, and finally converted into a deterministic business decision (such as Auto-Approve or Human Review).

---

## Demo Flow

### Step 1 — Show the Overall System Architecture

**File to open:**
[`architecture/system_architecture.mmd`](file:///c:/Users/User/projects/Agent-to-Agent%20Financial%20Collaboration/architecture/system_architecture.mmd)

**What I should show:**
Point to the flow starting from `Payment Streams` (Webhook), moving to the `FastAPI Gateway`, offloading to the Orchestration engine, branching through the 5 agents, interacting with Qdrant/MongoDB, and resolving back to the ERP.

**What I should explain:**
> "This represents our event-driven ingestion pipeline. When a payment exception occurs, our FastAPI gateway accepts the webhook payload and immediately returns a 202 Accepted. The payload is pushed onto a Redis queue, where a Celery worker picks it up and initializes our multi-agent orchestrator. The orchestration layer communicates with a simulated MongoDB ERP and queries a Qdrant Vector DB for policy RAG before outputting a deterministic decision."

**Technical points to highlight:**
* **Event-driven architecture:** Decouples ingestion from execution.
* **Async processing:** Critical because LLMs introduce high latency; we cannot block the webhook.
* **Separation of responsibilities:** Clear boundary between infrastructure (FastAPI/Celery) and cognitive processing (Swarm Agents).
* **Note on diagram accuracy:** Mention that while the diagram says "LangGraph State Engine", the actual implementation has been built using **OpenAI Swarm** to focus on stateless handoffs, which we will see in the code.

**Expected questions:**
* *Q: How does the system scale under a burst of payment webhooks?*
  * **Answer:** Because we offload processing to Celery and Redis, the FastAPI layer can accept thousands of events per second. The bottleneck becomes LLM API rate limits, which we manage by scaling Celery concurrency and implementing backoff retries.
* *Q: Why MongoDB for the ERP?*
  * **Answer:** It's just a mock repository for this prototype. In production, this would be an integration layer (e.g., SAP or Oracle APIs).

---

### Step 2 — Agent Architecture

**File to open:**
[`architecture/agent_architecture.mmd`](file:///c:/Users/User/projects/Agent-to-Agent%20Financial%20Collaboration/architecture/agent_architecture.mmd)

**What I should explain:**
* **Agent topology:** The system uses a strict sequential handoff pattern.
* **Why multiple specialized agents:** A single agent with a massive prompt and 20 tools would hallucinate and degrade in reasoning quality. By splitting them (e.g., Risk Agent vs. Policy Agent), we constrain their context window and limit the tools they can execute, resulting in higher accuracy.

**Agent Flow Breakdown:**
| Agent | Responsibility | Tools | Input | Output | Handoff |
| ----- | -------------- | ----- | ----- | ------ | ------- |
| **Payment Agent** | Extract payment info & identify customer | `get_customer_by_name` | Payment message | Customer ID & Credit | AR Agent |
| **AR Agent** | Lookup open invoices & credit | `get_customer_invoices` | Customer ID | Open invoices | Risk Agent |
| **Risk Agent** | Evaluate transaction anomalies | `assess_risk` | Flags, Risk Tier | Risk Score | Policy Agent |
| **Policy Agent** | Retrieve corporate rules | `query_policies` | Risk context | Relevant Policies | Decision Agent |
| **Decision Agent** | Emit final structured JSON | (None) | Aggregated context | Structured JSON | (End of Workflow) |

---

### Step 3 — API Entry Point

**File to open:**
[`backend/api/main.py`](file:///c:/Users/User/projects/Agent-to-Agent%20Financial%20Collaboration/backend/api/main.py)

**What to show:**
Show the `@app.post("/api/events/webhook")` endpoint.

**Explanation:**
> "Here is the webhook entry point. It receives a `payment_id`, validates that the payment actually exists in the ERP to prevent spoofing, and then immediately calls `process_payment_event_task.delay()`. It returns a 202 Accepted with a Celery Task ID."

**Technical points to highlight:**
* Returning 202 Accepted avoids holding open HTTP connections during long LLM inference times.
* Validates against `ERPRepository` before enqueuing, saving expensive LLM calls on invalid payloads.

---

### Step 4 — Background Worker

**File to open:**
[`backend/worker.py`](file:///c:/Users/User/projects/Agent-to-Agent%20Financial%20Collaboration/backend/worker.py)

**What to show:**
Show the `process_payment_event_task` function.

**Explanation:**
> "The Celery worker picks up the task here. It hydrates the payment details into a natural language prompt string and triggers the Swarm workflow. The results and message history are aggregated and returned as the task state."

**Execution Flow:**
`Webhook → FastAPI → Redis Queue → Celery Worker → Swarm Orchestrator`

---

## Deep Dive Into Agent Orchestration

**File to open:**
[`backend/workflows/swarm_orchestrator.py`](file:///c:/Users/User/projects/Agent-to-Agent%20Financial%20Collaboration/backend/workflows/swarm_orchestrator.py)

### 6.1 LLM Configuration
**Show:** Lines 14-27 (`PatchedChatCompletions`)
> "We are utilizing Gemini (`gemini-3.5-flash`) via the OpenAI SDK wrapper. However, Gemini's API strictly rejects `null` values for optional fields and requires `content` to be at least an empty string. To fix this without modifying the core Swarm library, I implemented a monkey patch (`PatchedChatCompletions`) that recursively strips None values from the request payloads before they hit the API. This ensures flawless compatibility."

### 6.2 Agent Definitions & Handoff Mechanism
**Show:** Lines 29-40 (`transfer_to_...`) and Lines 73-123 (Agent instantiations).
> "We define 5 distinct agents. Notice the handoff mechanism: `transfer_to_ar_agent` simply returns the `ar_agent` object. Swarm handles preserving the message history context seamlessly during the transition. The sequence is strictly enforced by only giving each agent the tool to transition to the *next* specific agent in the chain."

### 6.3 Tool Calling
**Show:** Lines 41-71 (Tool definitions like `get_customer_invoices` and `assess_risk`).
> "We wrap deterministic database queries into simple Python functions. For example, `get_customer_invoices` queries MongoDB. We do NOT let the LLM write SQL or Mongo queries itself. We enforce deterministic data retrieval, bounding the LLM to only interpret the results, not invent the query."

---

## Deep Dive Into RAG

**File to open:**
[`backend/rag/retriever.py`](file:///c:/Users/User/projects/Agent-to-Agent%20Financial%20Collaboration/backend/rag/retriever.py)

**What to show:**
Show `search_policies` and the embedding model initialization.

**Explanation:**
> "To prevent the LLM from hallucinating financial rules, we ground the Policy Agent using RAG. We use Qdrant for vector storage and FastEmbed with `BAAI/bge-small-en-v1.5` for local, fast embeddings without extra network calls. When the Policy Agent calls `query_policies`, this script embeds the query, performs a cosine similarity search in Qdrant, and returns the actual markdown text of the policy."

**Flow:**
`Policy Document → MarkdownTextSplitter → FastEmbed → Qdrant → Semantic Search → Policy Agent Context`

---

## Mock ERP / Data Simulation

**File to open:**
[`generate_mock_data.py`](file:///c:/Users/User/projects/Agent-to-Agent%20Financial%20Collaboration/generate_mock_data.py)

**What to show:**
Scroll to `generate_payments()` and `generate_policies()`.

**Explanation:**
> "To prove the system works, this script seeds MongoDB with edge-case scenarios and generates markdown policies for Qdrant."

**Key Scenarios to Highlight:**
* **PAY-9002 (The Short Pay Scenario):** Globex Treasury paid $12,500 on an invoice of $15,000. However, the system knows Globex has an `available_credit` of $2,500. The RAG policy (`AR-101`) explicitly states that if payment + available credit equals the invoice, it can be auto-resolved. 
* **PAY-9003 (The Fraud Scenario):** An unknown entity sent $48,000 with a `suspicious_origin` flag. The RAG policy (`RISK-201`) explicitly states that high-risk flags must *never* be auto-resolved, forcing the Decision Agent to output "Review".

---

## Complete End-to-End Execution

```text
ERP/Webhook Payload
    ↓
FastAPI (Returns 202 Accepted)
    ↓
Celery Task (Hydrates payment ID to full message)
    ↓
Swarm Orchestrator
    ↓
Payment Agent (Calls get_customer_by_name → finds Globex)
    ↓
AR Agent (Calls get_customer_invoices → finds $15k invoice & $2.5k credit)
    ↓
Risk Agent (Calls assess_risk → returns low risk score)
    ↓
Policy Agent (Calls query_policies → retrieves AR-101 rule)
    ↓
Decision Agent (Analyzes context → emits JSON {"decision": "Auto-Approve"})
```

---

## Live Demo — Exact Commands

*Note: Run these from the project root `c:\Users\User\projects\Agent-to-Agent Financial Collaboration`.*

### Step 1 — Start infrastructure
```powershell
docker-compose up -d mongo qdrant redis
```

### Step 2 — Generate mock data
```powershell
# Ensure you are in the python venv first
python generate_mock_data.py
```

### Step 3 — Ingest policies
```powershell
python backend/rag/ingest.py
```

### Step 4 — Direct Orchestrator Demo (Bypass API/Celery)
**File to show:** [`backend/test_swarm.py`](file:///c:/Users/User/projects/Agent-to-Agent%20Financial%20Collaboration/backend/test_swarm.py)
```powershell
python backend/test_swarm.py
```
> "By running this script, we can bypass the async infrastructure and watch the agent chain-of-thought print directly to standard output. You will see exactly which tools each agent invoked and the final JSON decision."

---

## What Is AI and What Is Deterministic?

| Component | AI/LLM | Deterministic | Reason |
| :--- | :---: | :---: | :--- |
| **Payment extraction** | ✅ | | Understanding unstructured remittance text |
| **Invoice/Customer lookup**| | ✅ | Hardcoded repository queries guarantee accuracy |
| **Risk calculation** | | ✅ | Formulaic rule sets based on flags (Tool output) |
| **Policy retrieval** | | ✅ | Vector similarity search (RAG) |
| **Final decision** | ✅ | | Synthesizing all retrieved facts into a final verdict |

*Why this matters:* Financial systems require auditability. We limit the LLM's job to *reasoning* and *routing*. All data retrieval and calculation is delegated to deterministic Python functions.

---

## Why Multi-Agent Instead of One Agent?

**Advantages:**
* **Separation of concerns:** Risk rules do not pollute the AR lookup logic.
* **Controlled Handoffs:** We force a sequential pipeline, guaranteeing all steps are evaluated.
* **Tool Isolation:** The Risk Agent cannot accidentally execute an AR query, preventing runaway LLM loops.

**Disadvantages:**
* **Latency:** Multiple LLM calls mean processing takes seconds rather than milliseconds.
* **Cost:** Context windows grow as message history is appended and passed between agents.

*Conclusion:* In finance, accuracy and explainability outweigh latency. A multi-agent system provides the necessary audit trail for compliance.

---

## Why OpenAI Swarm? (And Swarm vs LangGraph)

**Why Swarm?** Swarm is incredibly lightweight. It focuses purely on stateless agent handoffs and tool calling without the heavy abstraction overhead of LangGraph.

| Feature | Swarm (Current) | LangGraph (Future) |
| :--- | :--- | :--- |
| Agent handoff | Simple function returns | Graph edges |
| Stateful workflows | No (Relies on message history) | Yes (Checkpointers) |
| Human-in-the-loop | Hard to interrupt/resume | Built-in via breakpoints |
| Graph control | Loosely defined by functions | Strictly defined cyclic graphs |

*Production Roadmap:* While Swarm is excellent for this prototype, a true production system would migrate to LangGraph to utilize persistent state checkpointers, enabling us to pause the workflow for human approval and resume it later.

---

## Current Prototype vs Production Architecture

### Implemented Today
* Event-driven API and Celery queue.
* OpenAI Swarm orchestration with Gemini via patch.
* Local Qdrant RAG ingestion and retrieval.
* MongoDB Mock ERP.

### Mocked / Simulated
* The ERP is just a local MongoDB database seeded by a python script.
* Authentication and Authorization are entirely disabled.

### Production Gaps
* **Idempotency:** The worker does not guarantee idempotency. If Celery retries a task, the Swarm workflow will run twice.
* **Human-in-the-loop (HITL):** Currently, the system outputs "Review", but there is no actual frontend queue to pause the workflow, get user input, and resume.
* **Observability:** We need LangSmith or OpenTelemetry to trace agent token usage and exact tool execution times.
* **Secrets Management:** Keys are in local `.env` files rather than AWS Secrets Manager or HashiCorp Vault.

---

## Questions a Senior AI Engineer May Ask

**Q: Why use Celery and Redis if the system is meant to be intelligent?**
*Answer:* LLM calls take time (10-30 seconds for a multi-agent chain). We cannot hold a webhook HTTP connection open that long. Celery provides the necessary async decoupling, retry logic, and queue management.

**Q: What happens if the `gemini-3.5-flash` model hallucinates a tool call?**
*Answer:* The tools are strongly typed. If the LLM hallucinates arguments, the Python execution will throw a TypeError, the error will be appended to the message history, and the LLM gets a chance to correct itself in the next turn.

**Q: How do you prevent irrelevant policies from confusing the Policy Agent?**
*Answer:* We chunk the markdown policies into small 500-character blocks using `MarkdownTextSplitter` and limit the Qdrant retrieval to the top 2 results (`limit=2`). This keeps the context window dense with high-value signal.

**Q: How do you guarantee the Decision Agent outputs valid JSON?**
*Answer:* Currently, we rely on prompt engineering (`Respond with a structured JSON-like format`). For true production readiness, we would enforce OpenAI's `response_format={ "type": "json_object" }` or use Pydantic validation frameworks like Instructor.

---

## Demo Narration Script

### Step 1 — The Setup
**Open:** `architecture/system_architecture.mmd`
**Say:** "This is our event-driven ingestion pipeline. We decouple the webhook ingestion using FastAPI from the heavy LLM orchestration using Celery and Redis."

### Step 2 — The Brain
**Open:** `backend/workflows/swarm_orchestrator.py`
**Show:** The `PatchedChatCompletions` class and the Agent definitions.
**Say:** "We are orchestrating 5 specialized agents using Swarm, patched to support Gemini. By separating responsibilities—AR lookup vs Risk vs Policy—we keep context windows focused and hallucination rates near zero."

### Step 3 — The Grounding
**Open:** `backend/rag/retriever.py`
**Show:** `search_policies` function.
**Say:** "To ensure compliance, the Policy Agent uses Qdrant and FastEmbed for local vector search. It dynamically reads corporate rules—like tolerance thresholds—before allowing the Decision agent to act."

### Step 4 — The Execution
**Open:** Terminal
**Execute:** `python backend/test_swarm.py`
**Say:** "Let's run a test. Watch the stdout. You can see the Payment Agent routing to the AR Agent, which queries the database, routing to the Risk Agent, and finally the Decision Agent auto-resolves the short-pay by correctly applying a simulated credit memo."

---

## File-by-File Presentation Order

| Order | File | What to Show | Why It Matters |
| ----- | ---- | ------------ | -------------- |
| 1 | `architecture/system_architecture.mmd` | System architecture | Sets the high-level async pipeline context. |
| 2 | `architecture/agent_architecture.mmd` | Agent topology | Explains the multi-agent delegation pattern. |
| 3 | `backend/workflows/swarm_orchestrator.py` | Agents/tools/handoffs | Shows the core LLM orchestration and Gemini patch. |
| 4 | `backend/rag/retriever.py` | RAG retrieval | Proves the LLM is grounded in deterministic policies. |
| 5 | `generate_mock_data.py` | Financial scenarios | Explains the complex edge case (PAY-9002) being solved. |
| 6 | `backend/test_swarm.py` | Live Execution | Proves the agent chain works exactly as designed. |

---

## Final 10-Minute Demo Version

* **Minute 0–1 (Problem):** "Resolving payment exceptions requires analyzing ledgers, risk, and corporate policies. This project automates that using a multi-agent system."
* **Minute 1–2 (Architecture):** Show `system_architecture.mmd`. "Webhooks hit FastAPI, drop into Redis, and are processed by a Celery worker to prevent HTTP blocking."
* **Minute 2–4 (Orchestration):** Show `swarm_orchestrator.py`. Walk through the 5 agents (Payment -> AR -> Risk -> Policy -> Decision). Highlight the Gemini API patch.
* **Minute 4–6 (Determinism):** Show the tool functions. Explain that data fetching is deterministic Python; the LLM only reasons over the result.
* **Minute 6–7 (RAG):** Show `rag/retriever.py`. Explain how corporate policies are vectorized in Qdrant so the LLM follows the rules.
* **Minute 7–10 (Live Demo):** Run `test_swarm.py`. Point at the terminal output showing the tool calls, the handoffs, and the final JSON decision structure. Acknowledge production gaps (HITL checkpointers, Idempotency) to close out strongly.
