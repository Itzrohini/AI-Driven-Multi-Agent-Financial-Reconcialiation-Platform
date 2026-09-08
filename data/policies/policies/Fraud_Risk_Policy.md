# Fraud and Risk Policy

## 1. High Risk Transactions
Any transaction flagged with suspicious origins or from a customer in a "high" risk tier must NEVER be auto-resolved. 
- **Rule ID**: RISK-201
- **Action**: Force human review regardless of AI confidence score.

## 2. Tolerance Thresholds
Payments that differ from the invoice amount by less than $10.00 can be automatically written off as a tolerance discrepancy.
- **Rule ID**: RISK-202
- **Action**: Auto-resolve (Write-off).
