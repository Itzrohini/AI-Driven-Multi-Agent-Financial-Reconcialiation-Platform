import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from repositories.erp_repository import ERPRepository

ERPRepository.save_pending_investigation(
    payment_id="PAY-999",
    history=[
        "Payment Agent found customer CUS-1002 (Globex)",
        "AR Agent found Open Invoice INV-5002 for $15,000",
        "Risk Agent reported Risk Score 0.1",
        "Policy Agent found Contract_Globex.md which says PO required over $10k"
    ],
    reasoning="We are missing a valid Purchase Order number for this $15,000 transaction. Section 4.2 of the contract strictly requires a PO for invoices over $10,000."
)

print("Successfully seeded pending investigation for PAY-999.")
