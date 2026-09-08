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
