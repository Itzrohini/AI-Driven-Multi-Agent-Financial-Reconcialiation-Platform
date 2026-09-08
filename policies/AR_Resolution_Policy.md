# Accounts Receivable Resolution Policy

## 1. Short Payments
If a customer submits a payment that is less than the invoice amount due (a "short pay"), the system must investigate the reason.

### 1.1 Credit Memo Application
If the customer has an outstanding credit memo (available_credit) on their account, and the short pay amount exactly matches the invoice amount minus the credit memo amount, the credit memo should be applied to resolve the invoice.
- **Rule ID**: AR-101
- **Condition**: `payment_amount == invoice_amount - available_credit`
- **Action**: Apply payment and credit memo to invoice. Auto-resolve if customer is in good standing and credit memo is <= $5,000.

### 1.2 Unexplained Short Pays
If a short pay cannot be explained by a credit memo or documented dispute, it must be flagged for human review. If the customer risk tier is "high", escalate immediately.
