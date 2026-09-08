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
