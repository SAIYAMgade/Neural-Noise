import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y'."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Skip cover page
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header
        self.drawString(54, letter[1] - 36, getattr(self, "header_title", "Corporate Financial Dossier"))
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
        
        # Footer
        self.line(54, 45, letter[0] - 54, 45)
        self.drawString(54, 32, "CONFIDENTIAL & STATUTORY FINANCIAL AUDIT — FY 2025-26")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()


def build_apex_global_pdf(out_path: str):
    """Builds a 24-page financial dossier for Apex Global Technologies Pvt Ltd."""
    doc = SimpleDocTemplate(
        out_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=26, leading=32, textColor=colors.HexColor("#1e1b4b"), alignment=1)
    subtitle_style = ParagraphStyle("CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=13, leading=18, textColor=colors.HexColor("#4338ca"), alignment=1)
    h1_style = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=colors.HexColor("#0f172a"), spaceAfter=10)
    h2_style = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=colors.HexColor("#334155"), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#334155"))
    body_bold = ParagraphStyle("BodyBold", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=colors.HexColor("#0f172a"))
    callout_style = ParagraphStyle("Callout", fontName="Helvetica-Oblique", fontSize=8.5, leading=12, textColor=colors.HexColor("#475569"))

    story = []

    # ================= PAGE 1: COVER =================
    story.append(Spacer(1, 120))
    story.append(Paragraph("APEX GLOBAL TECHNOLOGIES PVT LTD", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Annual Financial Operations Dossier & Statutory Audit", subtitle_style))
    story.append(Paragraph("Fiscal Year 2025 – 2026 | Financial Operations Report", callout_style))
    story.append(Spacer(1, 40))
    
    meta_table = Table([
        ["Corporate Entity:", "Apex Global Technologies Private Limited"],
        ["CIN / Reg No:", "U72200KA2021PTC148921"],
        ["GSTIN (Karnataka):", "29AAACA1234A1Z5 (State Code 29)"],
        ["Registered Address:", "Embassy TechVillage, Outer Ring Road, Bengaluru, Karnataka 560103"],
        ["Audit Period:", "01 April 2025 to 31 March 2026"],
        ["Audited Total Invoiced:", "INR 24,80,000.00 (24.80 Lakhs)"],
        ["Net Cash Flow Realized:", "INR 10,10,000.00 (10.10 Lakhs)"],
        ["Compliance Status:", "100% Tax Compliant (Intra-state & Inter-state GST Cleared)"]
    ], colWidths=[160, 320])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 80))
    story.append(Paragraph("CLASSIFICATION: PRIVILEGED & CONFIDENTIAL FINANCIAL DOSSIER", ParagraphStyle("RedAlert", parent=callout_style, textColor=colors.HexColor("#b91c1c"), alignment=1)))
    story.append(PageBreak())

    # ================= PAGE 2: EXECUTIVE LETTER & CONTENTS =================
    story.append(Paragraph("1. Executive Letter & Table of Contents", h1_style))
    story.append(Paragraph("To the Board of Directors & Independent Reviewers:", h2_style))
    story.append(Paragraph(
        "We hereby present the comprehensive Financial Operations Dossier for Apex Global Technologies Pvt Ltd for FY 2025-26. "
        "During this fiscal cycle, the organization consolidated its multi-cloud consulting, platform engineering, and AI automation operations, "
        "surpassing our invoiced milestone with INR 24,80,000 across domestic and export clients.", body_style
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Our collections efficiency stood at 74.6%, yielding INR 18,50,000 in direct bank deposits via RTGS/NEFT. Outstanding receivables total "
        "INR 6,30,000, with INR 2,10,000 marked as past 45-day overdue under formal recovery. Operational disbursements and vendor expenditures "
        "were maintained strictly at INR 8,40,000, ensuring an overall net operational cash surplus of INR 10,10,000.", body_style
    ))
    story.append(Spacer(1, 15))
    
    toc_data = [
        ["Section", "Description", "Pages"],
        ["Section 1", "Executive Letter, Table of Contents & Corporate Governance", "2"],
        ["Section 2", "Executive Financial Summary & KPI Scorecard (FY 2025-26)", "3"],
        ["Section 3", "State-wise Indian GST Schedule (CGST/SGST vs IGST Breakdown)", "4"],
        ["Section 4", "Itemized Tax Invoices Dossier (INV-2026-001 to INV-2026-010)", "5 – 14"],
        ["Section 5", "Enterprise Client Accounts & Double-Entry Ledgers", "15 – 18"],
        ["Section 6", "Operational Expenditure, Leases & Contractor Payouts", "19 – 21"],
        ["Section 7", "Cash Runway Modeling, Burn Analysis & Working Capital", "22 – 23"],
        ["Section 8", "Statutory Auditor Verification & Independent Sign-Off", "24"]
    ]
    t = Table(toc_data, colWidths=[80, 320, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e1b4b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ================= PAGE 3: EXECUTIVE KPI SCORECARD =================
    story.append(Paragraph("2. Executive Financial KPI Scorecard", h1_style))
    story.append(Paragraph("Aggregated Operating Metrics & Revenue Performance (FY 2025-26)", h2_style))
    
    kpi_cards = [
        ["Total Invoiced Revenue", "INR 24,80,000.00", "Total Collected Deposits", "INR 18,50,000.00"],
        ["Outstanding Receivables", "INR 6,30,000.00", "Total Past-Due Overdue", "INR 2,10,000.00"],
        ["Operational Expenditures", "INR 8,40,000.00", "Net Realized Cash Flow", "+ INR 10,10,000.00"],
        ["Gross Profit Margin", "66.1%", "Average Days Sales Outst.", "38.4 Days"]
    ]
    kpi_t = Table(kpi_cards, colWidths=[120, 120, 120, 120])
    kpi_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f1f5f9")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor("#1e1b4b")),
        ("TEXTCOLOR", (3, 0), (3, 0), colors.HexColor("#166534")),
        ("TEXTCOLOR", (1, 1), (1, 1), colors.HexColor("#b45309")),
        ("TEXTCOLOR", (3, 1), (3, 1), colors.HexColor("#b91c1c")),
        ("TEXTCOLOR", (3, 2), (3, 2), colors.HexColor("#15803d")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(kpi_t)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Quarterly Invoiced vs Collected Trajectory", h2_style))
    q_data = [
        ["Quarter", "Invoiced (INR)", "Collected (INR)", "Expenses (INR)", "Net Flow (INR)", "Realization %"],
        ["Q1 (Apr - Jun)", "5,20,000.00", "4,50,000.00", "1,90,000.00", "+ 2,60,000.00", "86.5%"],
        ["Q2 (Jul - Sep)", "6,80,000.00", "5,10,000.00", "2,10,000.00", "+ 3,00,000.00", "75.0%"],
        ["Q3 (Oct - Dec)", "5,90,000.00", "4,20,000.00", "2,05,000.00", "+ 2,15,000.00", "71.2%"],
        ["Q4 (Jan - Mar)", "6,90,000.00", "4,70,000.00", "2,35,000.00", "+ 2,35,000.00", "68.1%"],
        ["Fiscal FY26 Total", "24,80,000.00", "18,50,000.00", "8,40,000.00", "+ 10,10,000.00", "74.6%"]
    ]
    q_t = Table(q_data, colWidths=[90, 80, 80, 80, 85, 65])
    q_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#312e81")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8fafc")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0e7ff")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(q_t)
    story.append(PageBreak())

    # ================= PAGE 4: GST RECONCILIATION =================
    story.append(Paragraph("3. Statutory Indian GST Reconciliation Schedule", h1_style))
    story.append(Paragraph("Tax Liability Assessment (Karnataka Origin - State Code 29)", h2_style))
    story.append(Paragraph(
        "Apex Global Technologies operates under GSTIN 29AAACA1234A1Z5 registered in Bengaluru, Karnataka. "
        "Sales made to entities within Karnataka attract 9% Central GST (CGST) and 9% State GST (SGST). "
        "Inter-state transactions (Maharashtra, Delhi, Tamil Nadu, Telangana) attract 18% Integrated GST (IGST).", body_style
    ))
    story.append(Spacer(1, 12))
    
    gst_data = [
        ["Tax Type", "Taxable Base (INR)", "Rate", "Tax Amount (INR)", "ITC Offset (INR)", "Net Payable (INR)"],
        ["CGST (Intra-Karnataka)", "8,20,000.00", "9.0%", "73,800.00", "31,500.00", "42,300.00"],
        ["SGST (Intra-Karnataka)", "8,20,000.00", "9.0%", "73,800.00", "31,500.00", "42,300.00"],
        ["IGST (Inter-State MH, DL, TN)", "12,81,694.92", "18.0%", "2,30,705.08", "82,400.00", "1,48,305.08"],
        ["Zero-Rated / Software SEZ", "0.00", "0.0%", "0.00", "0.00", "0.00"],
        ["Consolidated GST Total", "21,01,694.92", "-", "3,78,305.08", "1,45,400.00", "2,32,905.08"]
    ]
    gst_t = Table(gst_data, colWidths=[130, 85, 45, 75, 75, 70])
    gst_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f0fdf4")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dcfce7")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(gst_t)
    story.append(Spacer(1, 20))
    story.append(Paragraph("GSTR-1 & GSTR-3B Filing Compliance Verification", h2_style))
    story.append(Paragraph("All monthly returns (Apr 2025 to Mar 2026) were filed on or before the 20th of subsequent months via GSTN portal. Nil penalties incurred.", body_style))
    story.append(PageBreak())

    # ================= PAGES 5 - 14: 10 ITEMIZED INVOICES =================
    invoices_apex = [
        ("INV-2026-001", "Infosense Technologies Pvt Ltd", "29AABCI5541L1Z0", "29 (KA)", "Cloud Modernization & DevOps Architecture", 250000, "paid", "2025-05-15", "2025-05-28"),
        ("INV-2026-002", "Titan Infrastructure Corp", "27AAACT9901M1ZA", "27 (MH)", "Enterprise Kubernetes Migration & Observability", 340000, "paid", "2025-06-20", "2025-07-02"),
        ("INV-2026-003", "Wipro Digital Engineering Labs", "29AAACW1122D1ZQ", "29 (KA)", "Generative AI LangGraph Pipeline Implementation", 180000, "paid", "2025-07-10", "2025-07-22"),
        ("INV-2026-004", "Zenith Media & Entertainment", "07AAGFZ9012C1Z8", "07 (DL)", "Automated Content Personalization Platform", 220000, "paid", "2025-08-18", "2025-09-01"),
        ("INV-2026-005", "Nexus Health Informatics Ltd", "33AABCN7788P1Z3", "33 (TN)", "HIPAA-Compliant Patient Telemetry Pipeline", 310000, "paid", "2025-09-25", "2025-10-12"),
        ("INV-2026-006", "Starlight Retail Solutions", "36AABCS4455E1ZV", "36 (TS)", "Omnichannel Real-Time Inventory Microservices", 270000, "paid", "2025-11-04", "2025-11-19"),
        ("INV-2026-007", "Aura Cloud Analytics Pvt Ltd", "27AABCA3311K1Z9", "27 (MH)", "Data Lakehouse & DBT Pipeline Construction", 280000, "paid", "2025-12-15", "2026-01-05"),
        ("INV-2026-008", "Kavach Security Solutions", "27AABCK5678B1Z2", "27 (MH)", "SOC 2 Type II Remediation & Cryptographic Audit", 210000, "overdue", "2026-01-10", "Pending"),
        ("INV-2026-009", "HyperScale SaaS Systems", "29AAACH8877B1ZN", "29 (KA)", "Multi-Tenant PostgreSQL Partitioning & Sharding", 240000, "issued", "2026-02-14", "Due in 15d"),
        ("INV-2026-010", "Quantum Edge Robotics LLP", "07AAGFQ4412R1Z7", "07 (DL)", "Edge AI Firmware Integration & Stream Telemetry", 180000, "issued", "2026-03-02", "Due in 25d")
    ]

    for inv_num, client, gstin, state, desc, base_amt, status, inv_date, pay_date in invoices_apex:
        story.append(Paragraph(f"Tax Invoice: {inv_num}", h1_style))
        is_interstate = "29" not in state
        tax_rate = 18.0
        tax_amt = round(base_amt * (tax_rate / 100.0), 2)
        total_amt = round(base_amt + tax_amt, 2)
        
        inv_head = [
            ["Invoice Number:", inv_num, "Date of Issue:", inv_date],
            ["Client Name:", client, "Place of Supply:", f"State Code {state}"],
            ["Client GSTIN:", gstin, "Payment Terms:", "Net 30 Days"],
            ["Issuer GSTIN:", "29AAACA1234A1Z5 (KA)", "Status:", status.upper()]
        ]
        head_t = Table(inv_head, colWidths=[100, 150, 100, 130])
        head_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(head_t)
        story.append(Spacer(1, 15))
        
        item_table = [
            ["Sl", "Service Description & Deliverable", "SAC Code", "Rate (INR)", "Qty", "Amount (INR)"],
            ["1", desc, "998314", f"{base_amt:,.2f}", "1.00", f"{base_amt:,.2f}"],
            ["", "Detailed Architectural Design & Production Verification", "998314", "Included", "-", "0.00"],
            ["", "Subtotal (Taxable Value)", "", "", "", f"{base_amt:,.2f}"],
        ]
        if is_interstate:
            item_table.append(["", "Integrated GST (IGST @ 18.0%)", "", "", "", f"{tax_amt:,.2f}"])
        else:
            cgst = tax_amt / 2.0
            item_table.append(["", "Central GST (CGST @ 9.0%)", "", "", "", f"{cgst:,.2f}"])
            item_table.append(["", "State GST (SGST @ 9.0%)", "", "", "", f"{cgst:,.2f}"])
        item_table.append(["", "Grand Total Payable (INR)", "", "", "", f"{total_amt:,.2f}"])
        
        it_t = Table(item_table, colWidths=[20, 240, 50, 60, 30, 80])
        it_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e1b4b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0e7ff")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(it_t)
        story.append(Spacer(1, 20))
        
        pay_info = [
            ["Bank Name:", "HDFC Bank Ltd, Richmond Road Branch, Bengaluru"],
            ["Account Number:", "50200088991122 (Current Account)"],
            ["IFSC Code:", "HDFC0000123"],
            ["Payment Verification:", f"Status: {status.upper()} | Bank Reference: {pay_date}"]
        ]
        p_t = Table(pay_info, colWidths=[120, 360])
        p_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(p_t)
        story.append(PageBreak())

    # ================= PAGES 15 - 18: CLIENT LEDGERS =================
    client_ledgers = [
        ("Titan Infrastructure Corp (MH · 27)", "INV-2026-002", 340000, 340000, 0, "NEFT-HDFC-991823"),
        ("Infosense Technologies (KA · 29)", "INV-2026-001", 250000, 250000, 0, "RTGS-ICICI-001928"),
        ("Zenith Media & Entertainment (DL · 07)", "INV-2026-004", 220000, 220000, 0, "IMPS-AXIS-882190"),
        ("Kavach Security Solutions (MH · 27)", "INV-2026-008", 210000, 0, 210000, "Overdue > 45 Days")
    ]

    for cname, inv, b_amt, c_amt, bal, ref in client_ledgers:
        story.append(Paragraph(f"Client Ledger Account: {cname}", h1_style))
        story.append(Paragraph("Double-Entry Bookkeeping Statement & Transaction Audit Trail", h2_style))
        
        ledg_data = [
            ["Date", "Reference Transaction", "Debit (INR)", "Credit (INR)", "Running Balance (INR)"],
            ["2025-04-01", "Opening Balance Brought Forward", "0.00", "0.00", "0.00"],
            ["2025-05-10", f"Tax Invoice Generated ({inv})", f"{b_amt:,.2f}", "0.00", f"{b_amt:,.2f} Dr"],
            ["2025-05-28", f"Bank Deposit Cleared ({ref})", "0.00", f"{c_amt:,.2f}", f"{bal:,.2f} {'Dr' if bal > 0 else 'Cr'}"],
            ["2026-03-31", "Period Closing Position", f"{b_amt:,.2f}", f"{c_amt:,.2f}", f"{bal:,.2f} {'Overdue' if bal > 0 else 'Settled'}"]
        ]
        l_t = Table(ledg_data, colWidths=[70, 190, 75, 75, 70])
        l_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8fafc")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(l_t)
        story.append(Spacer(1, 20))
        story.append(Paragraph("Account Standing & Verification Remarks:", h2_style))
        if bal == 0:
            story.append(Paragraph("This account is fully reconciled with zero outstanding balance. All TDS certificates (Form 16A) collected.", body_style))
        else:
            story.append(Paragraph(f"Account carries an outstanding debit balance of INR {bal:,.2f}. Three formal reminders issued. Statutory interest applicable under MSMED Act 2006.", body_style))
        story.append(PageBreak())

    # ================= PAGES 19 - 21: EXPENSES =================
    exp_sections = [
        ("Cloud Infrastructure, Compute & Hosting Disbursements", [
            ("AWS EMEA Cloud Infrastructure (EC2, S3, EKS)", "Monthly Compute Cluster", 240000, "Direct Debit"),
            ("Datadog Observability & APM Suite", "Monitoring & Alerts", 65000, "Credit Card"),
            ("Cloudflare Enterprise CDN & WAF", "Edge Security", 45000, "Credit Card"),
            ("Subtotal Cloud Compute", "", 350000, "")
        ]),
        ("Office Lease, Facilities & Operations", [
            ("Embassy TechVillage Managed Office Space", "Monthly Lease & Utilities", 220000, "Bank Transfer"),
            ("High-Speed Dedicated Fiber Bandwidth (Tata Comm)", "Redundant ISP Leased Line", 35000, "Direct Debit"),
            ("Office Hardware, Monitors & Ergo Furniture", "Asset Capex Write-off", 65000, "Vendor Invoice"),
            ("Subtotal Facilities", "", 320000, "")
        ]),
        ("Professional Contractor Retainers & Specialized Services", [
            ("DevOps & SRE Specialist Contractors (2 Eng)", "Fractional Retainer", 110000, "Bank Transfer"),
            ("Statutory Legal Counsel & Tax Advisory (KPMG)", "Audit & Advisory", 40000, "Vendor Invoice"),
            ("Employee Welfare, Health Insurance & Training", "HDFC ERGO Group Cover", 20000, "Annual Premium"),
            ("Subtotal Professional Services", "", 170000, "")
        ])
    ]

    for title, rows in exp_sections:
        story.append(Paragraph(f"Operational Expenses: {title}", h1_style))
        exp_table = [["Vendor / Service Provider", "Expenditure Purpose", "Disbursed Amount (INR)", "Payment Mode"]]
        for vname, purp, amt, mode in rows:
            exp_table.append([vname, purp, f"{amt:,.2f}" if amt else "", mode])
        
        e_t = Table(exp_table, colWidths=[180, 150, 80, 70])
        e_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c2d12")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff7ed")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fed7aa")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(e_t)
        story.append(Spacer(1, 20))
        story.append(Paragraph("Audit Note: All expense vouchers have been cross-checked with corresponding GST input tax credit (ITC) entries in GSTR-2B. Total eligible ITC claimed: INR 1,45,400.00.", body_style))
        story.append(PageBreak())

    # ================= PAGES 22 - 23: RUNWAY & SCENARIO ANALYSIS =================
    story.append(Paragraph("7. Cash Runway & Burn Scenario Analysis (Part 1)", h1_style))
    story.append(Paragraph("Monthly Operating Burn Rate vs Current Cash Reserves", h2_style))
    runway_data = [
        ["Scenario", "Monthly Revenue (INR)", "Monthly Burn (INR)", "Net Monthly Burn", "Projected Runway"],
        ["Base Case (Current Trajectory)", "2,06,666.00", "70,000.00", "+ 1,36,666.00 (Cash Positive)", "Infinite (Self-sustaining)"],
        ["Stressed (30% Revenue Drop)", "1,44,666.00", "70,000.00", "+ 74,666.00", "Self-sustaining"],
        ["Zero Revenue Black Swan", "0.00", "70,000.00", "- 70,000.00", "14.4 Months (Current Cash INR 10.1L)"]
    ]
    r_t = Table(runway_data, colWidths=[120, 90, 85, 100, 85])
    r_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(r_t)
    story.append(PageBreak())

    story.append(Paragraph("7. Cash Runway & Burn Scenario Analysis (Part 2)", h1_style))
    story.append(Paragraph("Capital Allocation Recommendations for FY 2026-27", h2_style))
    story.append(Paragraph(
        "Based on Monte Carlo simulations and isolation forest anomaly screening, Apex Global Technologies maintains "
        "a robust financial liquidity buffer. Net operating cash reserves of INR 10,10,000 provide 14.4 months of bare minimum "
        "operational runway even under complete operational shutdown.", body_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Key Recommendations:", h2_style))
    story.append(Paragraph("1. Accelerate invoice collection cycle from Kavach Security Solutions (INR 2,10,000) using statutory arbitration under Section 18 of MSMED Act.", body_style))
    story.append(Paragraph("2. Deploy surplus liquidity (INR 6,00,000) into short-term corporate treasury bills yielding 7.2% annualized.", body_style))
    story.append(Paragraph("3. Maintain vendor expenditure caps at INR 80,000/month for Q1 FY27.", body_style))
    story.append(PageBreak())

    # ================= PAGE 24: AUDITOR SIGN-OFF =================
    story.append(Paragraph("8. Statutory Independent Auditor Verification", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("To the Shareholders of Apex Global Technologies Private Limited:", h2_style))
    story.append(Paragraph(
        "We have audited the accompanying financial dossier and ledger records of Apex Global Technologies Pvt Ltd for the fiscal year ended "
        "31 March 2026. In our opinion, the accompanying statements give a true and fair view of the financial position of the company, "
        "confirming Total Invoiced Revenue of INR 24,80,000.00 and Total Collected Bank Deposits of INR 18,50,000.00.", body_style
    ))
    story.append(Spacer(1, 20))
    
    sign_data = [
        ["For S.R. Batliboi & Associates LLP", "For and on behalf of the Board of Directors"],
        ["Chartered Accountants (ICAI Reg No: 101049W)", "Apex Global Technologies Pvt Ltd"],
        ["\n\n___________________________\nRajesh V. Sharma, FCA\nPartner (Membership No: 049210)\nUDIN: 26049210AAAAAB1920\nPlace: Bengaluru\nDate: 15 April 2026",
         "\n\n___________________________\nVikramaditya Rao\nManaging Director (DIN: 08912344)\nPlace: Bengaluru\nDate: 15 April 2026"]
    ]
    s_t = Table(sign_data, colWidths=[240, 240])
    s_t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(s_t)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Built Apex Global PDF at {out_path}")


def build_kavach_security_pdf(out_path: str):
    """Builds a 25-page financial audit dossier for Kavach Security Solutions Pvt Ltd."""
    doc = SimpleDocTemplate(
        out_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=26, leading=32, textColor=colors.HexColor("#0f172a"), alignment=1)
    subtitle_style = ParagraphStyle("CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=13, leading=18, textColor=colors.HexColor("#0284c7"), alignment=1)
    h1_style = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=colors.HexColor("#0f172a"), spaceAfter=10)
    h2_style = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=colors.HexColor("#334155"), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#334155"))
    callout_style = ParagraphStyle("Callout", fontName="Helvetica-Oblique", fontSize=8.5, leading=12, textColor=colors.HexColor("#475569"))

    story = []

    # ================= PAGE 1: COVER =================
    story.append(Spacer(1, 120))
    story.append(Paragraph("KAVACH SECURITY SOLUTIONS PVT LTD", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Annual Operations & Cybersecurity Audit Report", subtitle_style))
    story.append(Paragraph("ISO 27001 & SOC 2 Type II Certified Financial Records", callout_style))
    story.append(Spacer(1, 40))
    
    meta_table = Table([
        ["Corporate Entity:", "Kavach Security Solutions Private Limited"],
        ["CIN / Reg No:", "U74999MH2020PTC339812"],
        ["GSTIN (Maharashtra):", "27AABCK5678B1Z2 (State Code 27)"],
        ["Registered Address:", "Bandra-Kurla Complex (BKC), Bandra East, Mumbai, Maharashtra 400051"],
        ["Fiscal Cycle:", "FY 2025 – 2026"],
        ["Total Invoiced Billings:", "INR 38,50,000.00 (38.50 Lakhs)"],
        ["Total Direct Collections:", "INR 29,00,000.00 (29.00 Lakhs)"],
        ["Net Cash Flow Realized:", "INR 14,80,000.00 (14.80 Lakhs)"]
    ], colWidths=[160, 320])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#0284c7")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # ================= PAGE 2: TABLE OF CONTENTS =================
    story.append(Paragraph("1. Executive Summary & Audit Table of Contents", h1_style))
    story.append(Paragraph("Kavach Security Solutions specializes in cryptographic defense, enterprise penetration testing, zero-trust cloud infrastructure, and 24/7 SOC operations. Total invoiced revenue reached INR 38,50,000 with net operating cash surplus of INR 14,80,000.", body_style))
    story.append(Spacer(1, 15))
    
    toc = [
        ["Section", "Contents", "Page Range"],
        ["1", "Executive Summary, Governance & Index", "2"],
        ["2", "Financial KPI Overview & ARR Metrics", "3"],
        ["3", "Multi-State GST Compliance Schedule (MH, DL, KA, TN)", "4"],
        ["4", "Itemized Cybersecurity Tax Invoices (KAV-2026-101 to 111)", "5 – 15"],
        ["5", "Enterprise Customer Ledgers & Statements", "16 – 19"],
        ["6", "R&D, SOC Data Center & Infrastructure Expenses", "20 – 22"],
        ["7", "12-Month Runway Forecast & Working Capital", "23 – 24"],
        ["8", "Independent Auditor Verification & Signature", "25"]
    ]
    t = Table(toc, colWidths=[60, 340, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0369a1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ================= PAGE 3: KPI SCORECARD =================
    story.append(Paragraph("2. Financial Performance & ARR Scorecard", h1_style))
    kpi_kavach = [
        ["Total Invoiced Amount", "INR 38,50,000.00", "Total Collected Deposits", "INR 29,00,000.00"],
        ["Outstanding Receivables", "INR 9,50,000.00", "Total Past-Due Overdue", "INR 4,20,000.00"],
        ["Operating & R&D Expenses", "INR 14,20,000.00", "Net Realized Cash Surplus", "+ INR 14,80,000.00"],
        ["Active Enterprise Retainers", "14 Contracts", "SOC Uptime SLA Achieved", "99.98%"]
    ]
    k_t = Table(kpi_kavach, colWidths=[120, 120, 120, 120])
    k_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f9ff")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f0f9ff")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bae6fd")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(k_t)
    story.append(PageBreak())

    # ================= PAGE 4: GST RECONCILIATION =================
    story.append(Paragraph("3. Multi-State Indian GST Breakdown (Origin MH · 27)", h1_style))
    story.append(Paragraph("Registered under GSTIN 27AABCK5678B1Z2. Intra-state sales within Maharashtra attract 9% CGST + 9% SGST. Inter-state clients in Karnataka, Delhi, and Tamil Nadu attract 18% IGST.", body_style))
    story.append(Spacer(1, 15))
    gst_kav = [
        ["Tax Bracket", "Taxable Base (INR)", "Rate", "Gross Tax (INR)", "ITC Adjustment", "Net Tax Paid (INR)"],
        ["CGST (Maharashtra)", "14,00,000.00", "9.0%", "1,26,000.00", "52,000.00", "74,000.00"],
        ["SGST (Maharashtra)", "14,00,000.00", "9.0%", "1,26,000.00", "52,000.00", "74,000.00"],
        ["IGST (Interstate KA, DL, TN)", "18,60,169.49", "18.0%", "3,34,830.51", "1,22,000.00", "2,12,830.51"],
        ["Total GST Liability", "32,60,169.49", "-", "5,86,830.51", "2,26,000.00", "3,60,830.51"]
    ]
    gt = Table(gst_kav, colWidths=[120, 85, 45, 80, 80, 70])
    gt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#075985")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(gt)
    story.append(PageBreak())

    # ================= PAGES 5 - 15: 11 INVOICES =================
    invs_kav = [
        ("KAV-2026-101", "HDFC Securities Ltd", "27AAACH1122K1Z3", "27 (MH)", "Annual Zero-Trust SOC SIEM Retainer", 450000, "paid", "2025-04-12", "2025-04-25"),
        ("KAV-2026-102", "Reliance Cloud Platforms", "27AAACR4411D1ZQ", "27 (MH)", "Penetration Testing & Red-Teaming Simulation", 380000, "paid", "2025-05-18", "2025-06-02"),
        ("KAV-2026-103", "Mahindra Defense Systems", "27AAACM8899F1ZV", "27 (MH)", "Cryptographic Key Management & HSM Integration", 520000, "paid", "2025-06-25", "2025-07-10"),
        ("KAV-2026-104", "Tata Communications Ltd", "27AAACT9901M1ZA", "27 (MH)", "Cloud Perimeter DDOS Threat Intelligence", 320000, "paid", "2025-08-14", "2025-08-30"),
        ("KAV-2026-105", "Apex Global Technologies", "29AAACA1234A1Z5", "29 (KA)", "ISO 27001 Re-Certification & Remediation", 290000, "paid", "2025-09-22", "2025-10-05"),
        ("KAV-2026-106", "PayFlow Payments Network", "07AABCP3312E1ZL", "07 (DL)", "PCI-DSS 4.0 Compliance Readiness Assessment", 410000, "paid", "2025-11-08", "2025-11-24"),
        ("KAV-2026-107", "Bajaj Finserv Digital", "27AAACB2299C1ZM", "27 (MH)", "Core Banking API Vulnerability Scanning", 360000, "paid", "2025-12-12", "2025-12-28"),
        ("KAV-2026-108", "CyberShield Asia Pacific", "33AABCC5544Q1ZP", "33 (TN)", "Managed Threat Hunting & Forensics Retainer", 280000, "overdue", "2026-01-05", "Pending (Overdue)"),
        ("KAV-2026-109", "SecureStack Global Pte", "07AAGFS9921T1Z4", "07 (DL)", "Enterprise Identity & MFA Hardening", 140000, "overdue", "2026-01-18", "Pending (Overdue)"),
        ("KAV-2026-110", "OmniGuard Telecom Labs", "29AABCO7711B1ZW", "29 (KA)", "5G Core Network Slicing Security Architecture", 420000, "issued", "2026-02-15", "Due in 20d"),
        ("KAV-2026-111", "Vanguard Health Systems", "27AABCV1199M1ZT", "27 (MH)", "Medical Device Firmware Encryption & Security", 280000, "issued", "2026-03-01", "Due in 30d")
    ]

    for inv_num, client, gstin, state, desc, base_amt, status, idate, pdate in invs_kav:
        story.append(Paragraph(f"Tax Invoice: {inv_num}", h1_style))
        tax_amt = round(base_amt * 0.18, 2)
        total = round(base_amt + tax_amt, 2)
        
        t_data = [
            ["Invoice Number:", inv_num, "Date of Issue:", idate],
            ["Client Name:", client, "GSTIN:", gstin],
            ["Issuer GSTIN:", "27AABCK5678B1Z2 (MH)", "Status:", status.upper()],
            ["Place of Supply:", f"State Code {state}", "Payment Ref:", pdate]
        ]
        t1 = Table(t_data, colWidths=[100, 150, 100, 130])
        t1.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t1)
        story.append(Spacer(1, 15))
        
        items = [
            ["Sl", "Service Description & Scope", "SAC", "Rate (INR)", "Qty", "Total (INR)"],
            ["1", desc, "998315", f"{base_amt:,.2f}", "1.00", f"{base_amt:,.2f}"],
            ["", "Subtotal", "", "", "", f"{base_amt:,.2f}"],
            ["", "GST (@ 18.0%)", "", "", "", f"{tax_amt:,.2f}"],
            ["", "Total Invoice Payable", "", "", "", f"{total:,.2f}"]
        ]
        t2 = Table(items, colWidths=[20, 240, 50, 60, 30, 80])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0369a1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0f2fe")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t2)
        story.append(PageBreak())

    # ================= PAGES 16 - 19: CUSTOMER LEDGERS =================
    kav_ledgers = [
        ("HDFC Securities Ltd (MH · 27)", "KAV-2026-101", 450000, 450000, 0),
        ("Reliance Cloud Platforms (MH · 27)", "KAV-2026-102", 380000, 380000, 0),
        ("CyberShield Asia Pacific (TN · 33)", "KAV-2026-108", 280000, 0, 280000),
        ("SecureStack Global (DL · 07)", "KAV-2026-109", 140000, 0, 140000)
    ]
    for cname, inv, bamt, camt, bal in kav_ledgers:
        story.append(Paragraph(f"Customer Ledger Statement: {cname}", h1_style))
        ldata = [
            ["Transaction Date", "Particulars & Invoice Number", "Debit (INR)", "Credit (INR)", "Balance (INR)"],
            ["2025-04-01", "Opening Balance", "0.00", "0.00", "0.00"],
            ["2025-05-15", f"Cybersecurity Services Invoiced ({inv})", f"{bamt:,.2f}", "0.00", f"{bamt:,.2f} Dr"],
            ["2025-06-10", "Wire Transfer Settlement", "0.00", f"{camt:,.2f}", f"{bal:,.2f} {'Overdue' if bal > 0 else 'Settled'}"],
            ["2026-03-31", "Closing Position", f"{bamt:,.2f}", f"{camt:,.2f}", f"{bal:,.2f}"]
        ]
        lt = Table(ldata, colWidths=[80, 180, 70, 70, 80])
        lt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0c4a6e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(lt)
        story.append(PageBreak())

    # ================= PAGES 20 - 22: R&D & EXPENSES =================
    kav_exps = [
        ("Tier-IV Data Center & Cloud Hardware Leases", 480000),
        ("Threat Intelligence Commercial Feeds & MITRE Telemetry", 320000),
        ("Hardware Security Modules (YubiKey & Thales HSM Procurement)", 290000),
        ("Senior Cryptographer & Security Analyst Payroll Disbursal", 330000)
    ]
    for i, (ename, eamt) in enumerate(kav_exps[:3]):
        story.append(Paragraph(f"Operational & R&D Expenditure (Part {i+1}): {ename}", h1_style))
        story.append(Paragraph(f"Disbursed Amount: INR {eamt:,.2f}. All payments verified via RTGS corporate banking.", body_style))
        story.append(Spacer(1, 15))
        story.append(Paragraph("Full audit documentation attached in corporate archives under Schedule 4.", callout_style))
        story.append(PageBreak())

    # ================= PAGES 23 - 24: RUNWAY MODELING =================
    story.append(Paragraph("7. Financial Runway & Capital Solvency (Part 1)", h1_style))
    story.append(Paragraph("Kavach Security Solutions holds net cash surplus of INR 14,80,000. Operational monthly burn stands at INR 1,18,000, representing 12.5 months of defensive liquidity reserves without additional billings.", body_style))
    story.append(PageBreak())

    story.append(Paragraph("7. Financial Runway & Capital Solvency (Part 2)", h1_style))
    story.append(Paragraph("Risk Assessment & Overdue Recovery Schedule: Total past-due receivables stand at INR 4,20,000 across CyberShield (TN) and SecureStack (DL). Legal notices dispatched with statutory interest applicable.", body_style))
    story.append(PageBreak())

    # ================= PAGE 25: AUDITOR SIGN-OFF =================
    story.append(Paragraph("8. Independent Auditor Certification", h1_style))
    story.append(Paragraph("Statutory Audit Opinion for Kavach Security Solutions Pvt Ltd (FY 2025-26):", h2_style))
    story.append(Paragraph("We confirm accurate recording of INR 38,50,000.00 Invoiced Revenue and INR 29,00,000.00 Collected Deposits.", body_style))
    story.append(Spacer(1, 30))
    s_t = Table([
        ["For Deloitte Haskins & Sells LLP", "For the Board of Kavach Security Solutions Pvt Ltd"],
        ["Chartered Accountants (FRN: 117366W)", "\n\n___________________________\nAditya Kulkarni, CISSP\nChief Executive Officer"],
    ], colWidths=[240, 240])
    s_t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 9), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(s_t)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Built Kavach Security PDF at {out_path}")


def build_zenith_digital_pdf(out_path: str):
    """Builds a 22-page financial review dossier for Zenith Digital Media & Design LLP."""
    doc = SimpleDocTemplate(
        out_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=26, leading=32, textColor=colors.HexColor("#4c0519"), alignment=1)
    subtitle_style = ParagraphStyle("CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=13, leading=18, textColor=colors.HexColor("#be123c"), alignment=1)
    h1_style = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=colors.HexColor("#0f172a"), spaceAfter=10)
    h2_style = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=colors.HexColor("#334155"), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#334155"))
    callout_style = ParagraphStyle("Callout", fontName="Helvetica-Oblique", fontSize=8.5, leading=12, textColor=colors.HexColor("#475569"))

    story = []

    # ================= PAGE 1: COVER =================
    story.append(Spacer(1, 120))
    story.append(Paragraph("ZENITH DIGITAL MEDIA & DESIGN LLP", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Q3 Financial Review & Retainer Performance Dossier", subtitle_style))
    story.append(Paragraph("Performance Marketing, Creative Production & Growth Engineering", callout_style))
    story.append(Spacer(1, 40))
    
    meta_table = Table([
        ["Entity Name:", "Zenith Digital Media & Design LLP"],
        ["LLPIN:", "AAB-4921 (Registered under LLP Act 2008)"],
        ["GSTIN (Delhi):", "07AAGFZ9012C1Z8 (State Code 07)"],
        ["Corporate Office:", "Connaught Place, Barakhamba Road, New Delhi 110001"],
        ["Reporting Period:", "Fiscal Year 2025 – 2026 Comprehensive Review"],
        ["Total Invoiced:", "INR 16,20,000.00 (16.20 Lakhs)"],
        ["Total Collected:", "INR 12,80,000.00 (12.80 Lakhs)"],
        ["Operational Expenses:", "INR 6,10,000.00 (6.10 Lakhs)"],
        ["Net Cash Flow:", "+ INR 6,70,000.00 (6.70 Lakhs)"]
    ], colWidths=[160, 320])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff1f2")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#be123c")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # ================= PAGE 2: TABLE OF CONTENTS =================
    story.append(Paragraph("1. Executive Summary & Table of Contents", h1_style))
    story.append(Paragraph("Zenith Digital Media & Design LLP delivers growth marketing, creative strategy, and digital brand transformation. Invoiced billings for FY 2025-26 reached INR 16,20,000 across 9 primary retainer and performance campaign accounts.", body_style))
    story.append(Spacer(1, 15))
    
    toc = [
        ["Section", "Scope", "Pages"],
        ["1", "Executive Summary & Corporate Identity", "2"],
        ["2", "Financial KPI Scorecard & Collections", "3"],
        ["3", "Delhi GST & IGST Tax Schedule", "4"],
        ["4", "Itemized Agency Tax Invoices (ZDM-2026-301 to 309)", "5 – 13"],
        ["5", "Retainer Client Ledgers & Balances", "14 – 16"],
        ["6", "Media Buying, Creator Payouts & Agency Costs", "17 – 19"],
        ["7", "Working Capital & Cash Flow Projections", "20 – 21"],
        ["8", "Designated Partners Sign-Off & Verification", "22"]
    ]
    t = Table(toc, colWidths=[60, 340, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#881337")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ================= PAGE 3: KPI SCORECARD =================
    story.append(Paragraph("2. Financial KPI Scorecard", h1_style))
    kpi_z = [
        ["Total Invoiced Amount", "INR 16,20,000.00", "Total Collected Deposits", "INR 12,80,000.00"],
        ["Outstanding Receivables", "INR 3,40,000.00", "Total Past-Due Overdue", "INR 90,000.00"],
        ["Operational Disbursements", "INR 6,10,000.00", "Net Realized Cash Surplus", "+ INR 6,70,000.00"],
        ["Average Retainer Size", "INR 1,80,000.00", "Client Retention Rate", "91.5%"]
    ]
    zt = Table(kpi_z, colWidths=[120, 120, 120, 120])
    zt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#fff1f2")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#fff1f2")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(zt)
    story.append(PageBreak())

    # ================= PAGE 4: GST RECONCILIATION =================
    story.append(Paragraph("3. Delhi GST & Inter-State Tax Reconciliation", h1_style))
    story.append(Paragraph("Zenith Digital Media operates under Delhi GSTIN 07AAGFZ9012C1Z8 (State Code 07). Intra-state billings within Delhi attract 9% CGST + 9% SGST. Interstate billings to Maharashtra, Karnataka, and Haryana attract 18% IGST.", body_style))
    story.append(PageBreak())

    # ================= PAGES 5 - 13: 9 INVOICES =================
    invs_z = [
        ("ZDM-2026-301", "Nykaa Fashion E-Commerce", "27AAACN5541L1Z9", "27 (MH)", "Festive Campaign Creative Direction & UGC Video Assets", 220000, "paid", "2025-05-10"),
        ("ZDM-2026-302", "Swiggy Instamart Media", "29AAACS1122D1ZQ", "29 (KA)", "Hyperlocal Performance Marketing & Ad Optimization", 260000, "paid", "2025-06-15"),
        ("ZDM-2026-303", "Urban Company Home Services", "07AAGFU9901M1ZA", "07 (DL)", "Brand Repositioning & Design System Guidelines", 180000, "paid", "2025-07-20"),
        ("ZDM-2026-304", "Cleartrip Travel Technologies", "29AAACC7788P1Z3", "29 (KA)", "Search Engine Optimization & Technical Content Strategy", 190000, "paid", "2025-08-25"),
        ("ZDM-2026-305", "Zomato Dining & Events", "07AAGFZ4455E1ZV", "07 (DL)", "Event Media Coverage, Aftermovies & Motion Graphics", 150000, "paid", "2025-10-12"),
        ("ZDM-2026-306", "Mamaearth Personal Care", "06AAACD3311K1Z9", "06 (HR)", "Influencer Marketing Campaign & Tier-1 Creator Management", 280000, "paid", "2025-11-18"),
        ("ZDM-2026-307", "Cult.fit Fitness & Wellness", "29AAACC8877B1ZN", "29 (KA)", "App Store Conversion Rate Optimization & Ad Creatives", 160000, "overdue", "2026-01-08"),
        ("ZDM-2026-308", "Boat Lifestyle Audio", "07AAGFB1199M1ZT", "07 (DL)", "Product Launch Video 3D CGI Animation Pipeline", 90000, "issued", "2026-02-10"),
        ("ZDM-2026-309", "Lenskart Solutions Ltd", "06AAACL5544Q1ZP", "06 (HR)", "Quarterly Brand Strategy & Retainer Direction", 90000, "issued", "2026-03-01")
    ]

    for inv_num, client, gstin, state, desc, base_amt, status, idate in invs_z:
        story.append(Paragraph(f"Tax Invoice: {inv_num}", h1_style))
        tax_amt = round(base_amt * 0.18, 2)
        total = round(base_amt + tax_amt, 2)
        
        t_data = [
            ["Invoice ID:", inv_num, "Date of Issue:", idate],
            ["Client Name:", client, "Client GSTIN:", gstin],
            ["Issuer GSTIN:", "07AAGFZ9012C1Z8 (DL)", "Status:", status.upper()],
            ["Place of Supply:", f"State Code {state}", "Payment:", "Net 30 Days"]
        ]
        t1 = Table(t_data, colWidths=[100, 150, 100, 130])
        t1.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff1f2")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t1)
        story.append(Spacer(1, 15))
        
        items = [
            ["Sl", "Creative / Growth Deliverable Description", "SAC", "Rate (INR)", "Qty", "Total (INR)"],
            ["1", desc, "998311", f"{base_amt:,.2f}", "1.00", f"{base_amt:,.2f}"],
            ["", "Subtotal", "", "", "", f"{base_amt:,.2f}"],
            ["", "GST (@ 18.0%)", "", "", "", f"{tax_amt:,.2f}"],
            ["", "Total Invoice Payable", "", "", "", f"{total:,.2f}"]
        ]
        t2 = Table(items, colWidths=[20, 240, 50, 60, 30, 80])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#881337")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ffe4e6")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t2)
        story.append(PageBreak())

    # ================= PAGES 14 - 16: CLIENT LEDGERS =================
    z_ledgers = [
        ("Nykaa Fashion E-Commerce (MH · 27)", "ZDM-2026-301", 220000, 220000, 0),
        ("Swiggy Instamart Media (KA · 29)", "ZDM-2026-302", 260000, 260000, 0),
        ("Cult.fit Fitness & Wellness (KA · 29)", "ZDM-2026-307", 160000, 70000, 90000)
    ]
    for cname, inv, bamt, camt, bal in z_ledgers:
        story.append(Paragraph(f"Retainer Ledger Account: {cname}", h1_style))
        ldata = [
            ["Date", "Description", "Debit (INR)", "Credit (INR)", "Balance (INR)"],
            ["2025-05-01", f"Campaign Retainer Fee ({inv})", f"{bamt:,.2f}", "0.00", f"{bamt:,.2f} Dr"],
            ["2025-06-15", "Settlement Received via RTGS", "0.00", f"{camt:,.2f}", f"{bal:,.2f} {'Overdue' if bal > 0 else 'Settled'}"],
            ["2026-03-31", "Year-End Account Status", f"{bamt:,.2f}", f"{camt:,.2f}", f"{bal:,.2f}"]
        ]
        lt = Table(ldata, colWidths=[80, 180, 70, 70, 80])
        lt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4c0519")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(lt)
        story.append(PageBreak())

    # ================= PAGES 17 - 19: AGENCY EXPENSES =================
    z_exps = [
        ("Digital Ad Network Spend (Meta Ads & Google Display Network)", 240000),
        ("Independent Creator & Influencer Remuneration", 190000),
        ("Creative Software Suite (Adobe Creative Cloud, Figma, Cinema4D)", 180000)
    ]
    for i, (ename, eamt) in enumerate(z_exps):
        story.append(Paragraph(f"Agency Operating Expenses (Schedule {i+1}): {ename}", h1_style))
        story.append(Paragraph(f"Total Disbursed: INR {eamt:,.2f}. Reconciled with vendor tax receipts.", body_style))
        story.append(PageBreak())

    # ================= PAGES 20 - 21: WORKING CAPITAL =================
    story.append(Paragraph("7. Working Capital & Liquidity Trajectory (Part 1)", h1_style))
    story.append(Paragraph("Zenith Digital Media maintains INR 6,70,000 in net liquid operational cash flow. Average monthly operational expenses of INR 50,833 provide an operational buffer exceeding 13.1 months.", body_style))
    story.append(PageBreak())

    story.append(Paragraph("7. Working Capital & Liquidity Trajectory (Part 2)", h1_style))
    story.append(Paragraph("Receivables Aging: Outstanding receivables total INR 3,40,000, of which INR 90,000 (Cult.fit) is currently in follow-up. Retainer churn remains below 8.5% annualized.", body_style))
    story.append(PageBreak())

    # ================= PAGE 22: PARTNERS SIGN-OFF =================
    story.append(Paragraph("8. Designated Partners Certification", h1_style))
    story.append(Paragraph("Statement of Truth and Accounts for Zenith Digital Media & Design LLP (FY 2025-26):", h2_style))
    story.append(Paragraph("The undersigned Designated Partners certify that the financial statements present a true and fair view of operating revenue (INR 16,20,000.00) and net cash flow (INR 6,70,000.00).", body_style))
    story.append(Spacer(1, 30))
    s_t = Table([
        ["For Zenith Digital Media & Design LLP", "For Zenith Digital Media & Design LLP"],
        ["\n\n___________________________\nKavita Singhal\nDesignated Partner (DPIN: 09182311)",
         "\n\n___________________________\nRohan Batra\nDesignated Partner (DPIN: 09182312)"],
    ], colWidths=[240, 240])
    s_t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 9), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(s_t)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Built Zenith Digital PDF at {out_path}")


if __name__ == "__main__":
    out_dir = os.path.join("frontend", "public", "dossiers")
    os.makedirs(out_dir, exist_ok=True)
    
    p1 = os.path.join(out_dir, "Apex_Global_Technologies_FY2025_26_Dossier.pdf")
    p2 = os.path.join(out_dir, "Kavach_Security_Solutions_Annual_Audit_2026.pdf")
    p3 = os.path.join(out_dir, "Zenith_Digital_Media_Q3_Financial_Review.pdf")
    
    build_apex_global_pdf(p1)
    build_kavach_security_pdf(p2)
    build_zenith_digital_pdf(p3)
    print("All 3 corporate dossiers generated successfully!")
