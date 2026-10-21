"""
pdf_generator.py - Professional PDF Invoice Generation with ReportLab for FinPilot AI.
"""

from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

_PROJECT_ROOT = Path(__file__).parent.parent
_INVOICES_DIR = _PROJECT_ROOT / "data" / "invoices"


def generate_invoice_pdf(
    invoice_data: dict[str, Any],
    client_data: dict[str, Any],
    business_data: dict[str, Any] | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """
    Generates a PDF document for an invoice.
    """
    _INVOICES_DIR.mkdir(parents=True, exist_ok=True)
    inv_id = str(invoice_data.get("id", "invoice"))
    target_path = Path(output_path) if output_path else _INVOICES_DIR / f"{inv_id}.pdf"

    b_data = business_data or {
        "name": os.getenv("BUSINESS_NAME", "FinPilot Solutions India"),
        "address": "Bandra Kurla Complex, Mumbai, Maharashtra 400051",
        "gstin": "27AAPFU0939F1ZV",
        "email": "billing@finpilot.ai",
        "phone": "+91 98200 12345",
    }

    doc = SimpleDocTemplate(
        str(target_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#475569"),
    )
    bold_style = ParagraphStyle(
        "BoldText",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
    )
    draft_banner_style = ParagraphStyle(
        "DraftBanner",
        parent=styles["Normal"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#b91c1c"),
        fontName="Helvetica-Bold",
        alignment=1,
    )

    elements = []

    # Status / Draft Watermark
    status = str(invoice_data.get("status", "draft")).upper()
    if status == "DRAFT":
        elements.append(
            Paragraph("--- DRAFT INVOICE — FOR REVIEW ONLY (NOT A TAX INVOICE) ---", draft_banner_style)
        )
        elements.append(Spacer(1, 10))

    # Header Row: Business Info on Left, Invoice Details on Right
    inv_num = invoice_data.get("invoice_number", "DRAFT-XXXX")
    inv_date = str(invoice_data.get("invoice_date", ""))
    due_date = str(invoice_data.get("due_date", ""))

    header_table_data = [
        [
            Paragraph(f"<b>{b_data['name']}</b><br/>{b_data['address']}<br/>GSTIN: {b_data['gstin']}<br/>Email: {b_data['email']}", meta_style),
            Paragraph(f"<b>TAX INVOICE</b><br/><br/><b>Invoice #:</b> {inv_num}<br/><b>Date:</b> {inv_date}<br/><b>Due Date:</b> {due_date}<br/><b>Status:</b> {status}", meta_style),
        ]
    ]
    header_table = Table(header_table_data, colWidths=[300, 240])
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # Bill To Section
    client_name = client_data.get("company_name") or client_data.get("name", "Valued Client")
    client_contact = client_data.get("name", "")
    client_gstin = client_data.get("gstin") or "Unregistered / Consumer"
    client_addr = client_data.get("billing_address") or "N/A"
    client_state = client_data.get("state_code", "27")

    bill_to_data = [
        [
            Paragraph(f"<b>BILL TO:</b><br/><b>{client_name}</b><br/>Attn: {client_contact}<br/>{client_addr}<br/>State Code: {client_state}<br/>GSTIN: {client_gstin}", meta_style)
        ]
    ]
    bill_to_table = Table(bill_to_data, colWidths=[540])
    bill_to_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    elements.append(bill_to_table)
    elements.append(Spacer(1, 15))

    # Items Table Header
    items_header = [
        Paragraph("<b>#</b>", bold_style),
        Paragraph("<b>Description</b>", bold_style),
        Paragraph("<b>HSN/SAC</b>", bold_style),
        Paragraph("<b>Qty</b>", bold_style),
        Paragraph("<b>Rate (₹)</b>", bold_style),
        Paragraph("<b>Tax %</b>", bold_style),
        Paragraph("<b>Total (₹)</b>", bold_style),
    ]
    items_table_data = [items_header]

    line_items = invoice_data.get("line_items", [])
    for idx, item in enumerate(line_items, 1):
        desc = item.get("description", "")
        hsn = item.get("hsn_sac_code") or "-"
        qty = str(item.get("quantity", "1"))
        rate = f"{Decimal(str(item.get('unit_price', '0.00'))):,.2f}"
        tax_pct = f"{Decimal(str(item.get('tax_rate_pct', '18.00'))):,.0f}%"
        total = f"{Decimal(str(item.get('line_total', '0.00'))):,.2f}"

        items_table_data.append([
            Paragraph(str(idx), meta_style),
            Paragraph(desc, meta_style),
            Paragraph(hsn, meta_style),
            Paragraph(qty, meta_style),
            Paragraph(rate, meta_style),
            Paragraph(tax_pct, meta_style),
            Paragraph(total, meta_style),
        ])

    items_table = Table(items_table_data, colWidths=[25, 230, 60, 40, 65, 45, 75])
    items_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    elements.append(items_table)
    elements.append(Spacer(1, 15))

    # Summary Totals Section
    subtotal = f"₹{Decimal(str(invoice_data.get('subtotal', '0.00'))):,.2f}"
    discount = f"-₹{Decimal(str(invoice_data.get('discount_total', '0.00'))):,.2f}"
    cgst = f"₹{Decimal(str(invoice_data.get('cgst_amount', '0.00'))):,.2f}"
    sgst = f"₹{Decimal(str(invoice_data.get('sgst_amount', '0.00'))):,.2f}"
    igst = f"₹{Decimal(str(invoice_data.get('igst_amount', '0.00'))):,.2f}"
    total_tax = f"₹{Decimal(str(invoice_data.get('total_tax', '0.00'))):,.2f}"
    grand_total = f"₹{Decimal(str(invoice_data.get('grand_total', '0.00'))):,.2f}"
    paid = f"₹{Decimal(str(invoice_data.get('amount_paid', '0.00'))):,.2f}"
    due = f"₹{Decimal(str(invoice_data.get('amount_due', '0.00'))):,.2f}"

    tax_type = invoice_data.get("tax_type", "intra_state")
    summary_rows = [
        [Paragraph("Subtotal:", meta_style), Paragraph(subtotal, bold_style)],
    ]
    if Decimal(str(invoice_data.get("discount_total", "0.00"))) > 0:
        summary_rows.append([Paragraph("Discount:", meta_style), Paragraph(discount, bold_style)])

    if tax_type == "intra_state":
        summary_rows.extend([
            [Paragraph("CGST:", meta_style), Paragraph(cgst, meta_style)],
            [Paragraph("SGST:", meta_style), Paragraph(sgst, meta_style)],
        ])
    elif tax_type == "inter_state":
        summary_rows.append([Paragraph("IGST:", meta_style), Paragraph(igst, meta_style)])

    summary_rows.extend([
        [Paragraph("Total Tax:", meta_style), Paragraph(total_tax, meta_style)],
        [Paragraph("<b>Grand Total:</b>", bold_style), Paragraph(f"<b>{grand_total}</b>", bold_style)],
        [Paragraph("Amount Paid:", meta_style), Paragraph(paid, meta_style)],
        [Paragraph("<b>Balance Due:</b>", bold_style), Paragraph(f"<b>{due}</b>", bold_style)],
    ])

    summary_table = Table(summary_rows, colWidths=[120, 100])
    summary_table.setStyle(
        TableStyle([
            ("LINEBELOW", (0, -3), (-1, -3), 1, colors.HexColor("#cbd5e1")),
            ("LINEBELOW", (0, -1), (-1, -1), 1.5, colors.HexColor("#0f172a")),
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])
    )

    # Wrap summary in alignment table
    totals_wrapper = Table([[Paragraph("", meta_style), summary_table]], colWidths=[320, 220])
    totals_wrapper.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements.append(totals_wrapper)
    elements.append(Spacer(1, 25))

    # Notes & Payment Instructions
    notes_text = invoice_data.get("notes") or "Payment due within 15 days of invoice date. Bank transfers to ICICI Bank A/C: 000405001234, IFSC: ICIC0000004."
    footer_text = Paragraph(f"<b>Notes & Payment Instructions:</b><br/>{notes_text}", meta_style)
    elements.append(footer_text)

    doc.build(elements)
    return target_path
