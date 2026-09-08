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
