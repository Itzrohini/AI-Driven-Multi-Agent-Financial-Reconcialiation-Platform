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
