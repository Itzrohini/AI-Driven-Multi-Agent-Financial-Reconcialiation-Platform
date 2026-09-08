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
