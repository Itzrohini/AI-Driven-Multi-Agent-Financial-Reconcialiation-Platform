from fpdf import FPDF
import os

pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(40, 10, 'Mock Remittance Advice')
pdf.ln(20)
pdf.set_font('Arial', '', 12)
pdf.cell(40, 10, 'Date: 2026-08-25')
pdf.ln(10)
pdf.cell(40, 10, 'Customer: ABC Corporation (CUS-1002)')
pdf.ln(10)
pdf.cell(40, 10, 'Payment Reference: PAY-1024')
pdf.ln(10)
pdf.cell(40, 10, 'Amount Paid: $12,500.00 USD')
pdf.ln(20)
pdf.cell(40, 10, 'Invoices Paid:')
pdf.ln(10)
pdf.cell(40, 10, '- INV-8821: $12,000.00')
pdf.ln(10)
pdf.cell(40, 10, 'Unallocated: $500.00')

os.makedirs('/data/storage/raw', exist_ok=True)
os.makedirs('/data/storage/processed', exist_ok=True)

pdf.output('/data/storage/raw/mock_remittance.pdf')
print('Created mock_remittance.pdf in data/storage/raw/')
