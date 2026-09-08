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
