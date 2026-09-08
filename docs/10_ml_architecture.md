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
