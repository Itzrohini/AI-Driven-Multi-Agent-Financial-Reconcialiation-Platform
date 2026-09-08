# Event Architecture

**Status:** COMPLETED

## Purpose
Document the asynchronous event-driven architecture.

## Findings
To ensure the system scales without blocking, financial events are processed asynchronously.

1. **Ingestion:** Event arrives via webhook. FastAPI returns `202 Accepted` immediately.
2. **Queueing:** Event ID is pushed to a background task queue (FastAPI BackgroundTasks or a lightweight Redis queue for the MVP).
3. **Execution:** A worker picks up the event and invokes the LangGraph orchestrator.
