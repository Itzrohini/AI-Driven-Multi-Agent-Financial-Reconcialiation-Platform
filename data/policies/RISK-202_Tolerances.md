# Global Policy: RISK-202 Payment Tolerances

## Overview
This policy defines the acceptable financial tolerances for overpayments and underpayments.

## Rules
1. **Underpayment Tolerance**: If a payment is received that is short by $10.00 USD or less, and no credit memos are available, the remaining balance should be automatically written off to the "Small Balance Write-Off" general ledger account.
2. **Overpayment Tolerance**: If a payment exceeds the invoice amount by $10.00 USD or less, the excess should be logged as "Unapplied Cash" rather than creating a new credit memo, to prevent ledger pollution.
3. **Escalation**: Any discrepancy greater than the $10.00 tolerance (that is not resolved by a valid credit memo) must be routed to the Human Review Queue.

*Last Updated: 2026-03-20*
