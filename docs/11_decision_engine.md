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
