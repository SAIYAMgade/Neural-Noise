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
        self.drawString(54, letter[1] - 36, getattr(self, "header_title", "Corporate Financial Dossier & Statutory Audit"))
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
        
        # Footer
        self.line(54, 42, letter[0] - 54, 42)
        self.drawString(54, 30, "CONFIDENTIAL & STATUTORY FINANCIAL AUDIT — COMPLIANCE COPY")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 30, page_str)
        self.restoreState()


# =========================================================================
# HELPER STYLES & BUILDERS
# =========================================================================
def get_audit_styles(primary_hex="#1e1b4b", secondary_hex="#4338ca"):
    styles = getSampleStyleSheet()
    return {
        "CoverTitle": ParagraphStyle("CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=colors.HexColor(primary_hex), alignment=1),
        "CoverSub": ParagraphStyle("CoverSub", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=colors.HexColor(secondary_hex), alignment=1),
        "H1": ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=colors.HexColor(primary_hex), spaceAfter=4),
        "H2": ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#334155"), spaceBefore=4, spaceAfter=2),
        "Body": ParagraphStyle("Body", fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#334155")),
        "BodyBold": ParagraphStyle("BodyBold", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=colors.HexColor("#0f172a")),
        "Callout": ParagraphStyle("Callout", fontName="Helvetica-Oblique", fontSize=7.5, leading=10, textColor=colors.HexColor("#64748b")),
        "RedAlert": ParagraphStyle("RedAlert", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.HexColor("#b91c1c"), alignment=1),
        "Tag": ParagraphStyle("Tag", fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=colors.HexColor("#0f172a")),
    }


# =========================================================================
# 1. APEX GLOBAL TECHNOLOGIES (24 Pages)
# =========================================================================
def build_apex_global_pdf(out_path: str):
    """Builds a rich, completely populated 24-page financial dossier for Apex Global Technologies."""
    doc = SimpleDocTemplate(
        out_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    s = get_audit_styles(primary_hex="#1e1b4b", secondary_hex="#4338ca")
    story = []

    # PAGE 1: COVER
    story.append(Spacer(1, 40))
    story.append(Paragraph("APEX GLOBAL TECHNOLOGIES PRIVATE LIMITED", s["CoverTitle"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Annual Financial Operations Dossier & Statutory Audit", s["CoverSub"]))
    story.append(Paragraph("Fiscal Year 2025 – 2026 | Comprehensive Statutory Compliance Dossier", s["Callout"]))
    story.append(Spacer(1, 25))

    meta_table = Table([
        ["Corporate Entity:", "Apex Global Technologies Private Limited"],
        ["CIN / Corporate Identity No:", "U72200KA2021PTC148921 (Incorporated under Companies Act 2013)"],
        ["GSTIN (Karnataka Origin):", "29AAACA1234A1Z5 (State Code 29 — Karnataka)"],
        ["Permanent Account No (PAN):", "AAACA1234A (Direct Tax Jurisdiction, Ward 4(1), Bengaluru)"],
        ["Registered Corporate Office:", "Embassy TechVillage, Block 2B, Outer Ring Road, Bengaluru, Karnataka 560103"],
        ["Statutory Audit Period:", "01 April 2025 to 31 March 2026 (FY 2025-26)"],
        ["Audited Total Invoiced Revenue:", "INR 24,80,000.00 (Twenty-Four Lakh Eighty Thousand Rupees)"],
        ["Direct Bank Collections Realized:", "INR 18,50,000.00 (74.6% Realization Rate)"],
        ["Total Operational Disbursements:", "INR 8,40,000.00 (Cloud Infrastructure, Facilities, Payroll Retainers)"],
        ["Net Operating Cash Flow Surplus:", "+ INR 10,10,000.00 (Realized Liquid Surplus)"],
        ["Statutory Compliance Status:", "100% Tax Compliant | GSTR-1 & GSTR-3B Reconciled | Nil Penalties"],
        ["Statutory Independent Auditor:", "S.R. Batliboi & Associates LLP (ICAI Reg No: 101049W)"]
    ], colWidths=[170, 334])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 25))

    exec_notes = [
        ["Audit Scope:", "Comprehensive audit of all sales tax invoices (INV-2026-001 to 010), vendor disbursements, bank statements, GST reconciliations, and debt aging schedules."],
        ["Accounting Standard:", "Prepared in accordance with Indian Accounting Standards (Ind AS) notified under Section 133 of the Companies Act 2013."],
        ["Document Classification:", "PRIVILEGED & CONFIDENTIAL STATUTORY RECORD — FOR DIRECTORS & REGULATORS ONLY"]
    ]
    nt = Table(exec_notes, colWidths=[120, 384])
    nt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef2ff")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7d2fe")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e7ff")),
    ]))
    story.append(nt)
    story.append(PageBreak())

    # PAGE 2: EXECUTIVE LETTER & TABLE OF CONTENTS
    story.append(Paragraph("1. Executive Letter & Table of Contents", s["H1"]))
    story.append(Paragraph("To the Board of Directors, Shareholders, and Financial Regulators:", s["H2"]))
    story.append(Paragraph(
        "We hereby present the comprehensive Financial Operations Dossier for Apex Global Technologies Pvt Ltd for FY 2025-26. "
        "During this fiscal cycle, the organization consolidated its multi-cloud consulting, platform engineering, and AI automation operations, "
        "surpassing our invoiced milestone with INR 24,80,000 across domestic and export clients.", s["Body"]
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Our collections efficiency stood at 74.6%, yielding INR 18,50,000 in direct bank deposits via RTGS/NEFT. Outstanding receivables total "
        "INR 6,30,000, with INR 2,10,000 marked as past 45-day overdue under formal recovery. Operational disbursements and vendor expenditures "
        "were maintained strictly at INR 8,40,000, ensuring an overall net operational cash surplus of INR 10,10,000.", s["Body"]
    ))
    story.append(Spacer(1, 8))

    toc_data = [
        ["Section", "Audit Scope & Schedule Description", "Applicable Standards", "Pages"],
        ["Section 1", "Executive Letter, Corporate Governance & Statutory Overview", "Companies Act Sec 134", "2"],
        ["Section 2", "Executive Financial KPI Scorecard & Performance Metrics", "Ind AS 1 / Financial Ratios", "3"],
        ["Section 3", "State-wise Indian GST Schedule (CGST/SGST vs IGST Breakdown)", "CGST Act 2017 / GSTR-1/3B", "4"],
        ["Section 4", "Itemized Tax Invoices Dossier (INV-2026-001 to INV-2026-010)", "Rule 46 Tax Invoices", "5 – 14"],
        ["Section 5", "Enterprise Client Accounts & Double-Entry Ledgers", "Double-Entry Ledger Ind AS 18", "15 – 18"],
        ["Section 6", "Operational Expenditure, Leases & Contractor Payouts", "Schedule III Opex Audit", "19 – 21"],
        ["Section 7", "Working Capital, Debt Aging & Solvency Trajectory", "Working Capital / MSMED Act", "22 – 23"],
        ["Section 8", "Independent Statutory Auditor Opinion & Board Attestation", "SA 700 / CARO 2020", "24"]
    ]
    t = Table(toc_data, colWidths=[70, 234, 140, 60])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e1b4b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Statutory Corporate Governance Disclosure", s["H2"]))
    gov_table = Table([
        ["Board Meetings Held:", "4 Formal Sessions (Q1, Q2, Q3, Q4)", "Audit Committee Reviews:", "4 Statutory Sessions"],
        ["Internal Audit Status:", "Quarterly Internal Audits Cleared", "Related Party Transactions:", "Nil under Sec 188"],
        ["Directors Holding Office:", "Vikramaditya Rao (MD), Ananya Deshmukh (Director)", "Authorized Share Capital:", "INR 50,00,000.00 (50.0 Lakhs)"],
        ["Bankers to the Company:", "HDFC Bank Ltd (Richmond Road, Bengaluru)", "Paid-up Share Capital:", "INR 25,00,000.00 (25.0 Lakhs)"]
    ], colWidths=[120, 132, 120, 132])
    gov_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(gov_table)
    story.append(PageBreak())

    # PAGE 3: EXECUTIVE KPI SCORECARD
    story.append(Paragraph("2. Executive Financial KPI Scorecard", s["H1"]))
    story.append(Paragraph("Aggregated Operating Metrics & Financial Health Ratios (FY 2025-26)", s["H2"]))
    
    kpi_cards = [
        ["Total Invoiced Revenue", "INR 24,80,000.00", "Total Collected Deposits", "INR 18,50,000.00"],
        ["Outstanding Receivables", "INR 6,30,000.00", "Total Past-Due Overdue", "INR 2,10,000.00"],
        ["Operational Expenditures", "INR 8,40,000.00", "Net Realized Cash Surplus", "+ INR 10,10,000.00"],
        ["Gross Operating Margin", "66.13%", "Days Sales Outstanding (DSO)", "38.4 Days"]
    ]
    kpi_t = Table(kpi_cards, colWidths=[125, 127, 125, 127])
    kpi_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f1f5f9")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, 0), (1, 0), colors.HexColor("#1e1b4b")),
        ("TEXTCOLOR", (3, 0), (3, 0), colors.HexColor("#166534")),
        ("TEXTCOLOR", (1, 1), (1, 1), colors.HexColor("#b45309")),
        ("TEXTCOLOR", (3, 1), (3, 1), colors.HexColor("#b91c1c")),
        ("TEXTCOLOR", (3, 2), (3, 2), colors.HexColor("#15803d")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.append(kpi_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Quarterly Invoiced vs Collected Trajectory", s["H2"]))
    q_data = [
        ["Quarter Period", "Invoiced (INR)", "Collected (INR)", "Opex (INR)", "Net Flow (INR)", "Realization %", "Collection Status"],
        ["Q1 (Apr - Jun 2025)", "5,20,000.00", "4,50,000.00", "1,90,000.00", "+ 2,60,000.00", "86.5%", "High Realization"],
        ["Q2 (Jul - Sep 2025)", "6,80,000.00", "5,10,000.00", "2,10,000.00", "+ 3,00,000.00", "75.0%", "Target Realization"],
        ["Q3 (Oct - Dec 2025)", "5,90,000.00", "4,20,000.00", "2,05,000.00", "+ 2,15,000.00", "71.2%", "Within Threshold"],
        ["Q4 (Jan - Mar 2026)", "6,90,000.00", "4,70,000.00", "2,35,000.00", "+ 2,35,000.00", "68.1%", "Active Pipeline"],
        ["FY 2025-26 Total", "24,80,000.00", "18,50,000.00", "8,40,000.00", "+ 10,10,000.00", "74.6%", "Audited Balance"]
    ]
    q_t = Table(q_data, colWidths=[95, 75, 75, 70, 75, 60, 54])
    q_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#312e81")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8fafc")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0e7ff")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(q_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Core Statutory Financial Ratios & Liquidity Analysis", s["H2"]))
    ratio_data = [
        ["Financial Metric", "Value", "Benchmark", "Variance / Interpretation"],
        ["Current Ratio (CA / CL)", "2.84 : 1", "> 1.50 : 1", "Superior liquidity buffer against immediate payables"],
        ["Quick Ratio / Acid Test", "2.84 : 1", "> 1.00 : 1", "Zero inventory risk — 100% services business model"],
        ["Operating Profit Margin (OPM)", "66.13%", "> 40.00%", "Strong software margin economics across client portfolio"],
        ["Cash Flow to Revenue Ratio", "40.73%", "> 25.00%", "High cash conversion from billed contracts"],
        ["Days Sales Outstanding (DSO)", "38.4 Days", "< 45.0 Days", "Healthy working capital cycle within credit terms"],
        ["Debt-to-Equity Ratio", "0.00", "< 0.50", "Zero long-term bank borrowings; 100% equity capitalized"]
    ]
    rt = Table(ratio_data, colWidths=[140, 70, 80, 214])
    rt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(rt)
    story.append(PageBreak())

    # PAGE 4: GST RECONCILIATION SCHEDULE
    story.append(Paragraph("3. Statutory Indian GST Reconciliation Schedule", s["H1"]))
    story.append(Paragraph("Tax Liability Assessment & Monthly Filing Log (Karnataka Origin - State Code 29)", s["H2"]))
    story.append(Paragraph(
        "Apex Global Technologies operates under GSTIN 29AAACA1234A1Z5 registered in Bengaluru, Karnataka. "
        "Sales made to entities within Karnataka attract 9% Central GST (CGST) and 9% State GST (SGST). "
        "Inter-state transactions (Maharashtra, Delhi, Tamil Nadu, Telangana) attract 18% Integrated GST (IGST).", s["Body"]
    ))
    story.append(Spacer(1, 6))

    gst_data = [
        ["Tax Bracket", "Taxable Base (INR)", "Rate", "Tax Amount (INR)", "ITC Offset (INR)", "Net Cash Paid (INR)"],
        ["CGST (Intra-Karnataka)", "8,20,000.00", "9.0%", "73,800.00", "31,500.00", "42,300.00"],
        ["SGST (Intra-Karnataka)", "8,20,000.00", "9.0%", "73,800.00", "31,500.00", "42,300.00"],
        ["IGST (Inter-State MH, DL, TN, TS)", "12,81,694.92", "18.0%", "2,30,705.08", "82,400.00", "1,48,305.08"],
        ["RCM Inward Supplies (Reverse Charge)", "0.00", "18.0%", "0.00", "0.00", "0.00"],
        ["Consolidated GST Annual Total", "21,01,694.92", "-", "3,78,305.08", "1,45,400.00", "2,32,905.08"]
    ]
    gst_t = Table(gst_data, colWidths=[140, 85, 40, 75, 80, 84])
    gst_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065f46")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f0fdf4")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dcfce7")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(gst_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Statutory GSTR-1 & GSTR-3B Filing Compliance Ledger (FY 2025-26)", s["H2"]))
    filing_log = [
        ["Month", "Return Type", "ARN Reference Number", "Filing Date", "Tax Liability (INR)", "ITC Claimed", "Status"],
        ["Apr 2025", "GSTR-3B", "AA2904250198231", "2025-05-18", "28,400.00", "11,200.00", "Filed On-Time"],
        ["May 2025", "GSTR-3B", "AA2905250284729", "2025-06-19", "34,200.00", "12,400.00", "Filed On-Time"],
        ["Jun 2025", "GSTR-3B", "AA2906250391823", "2025-07-20", "29,800.00", "10,800.00", "Filed On-Time"],
        ["Jul 2025", "GSTR-3B", "AA2907250482910", "2025-08-17", "38,500.00", "14,200.00", "Filed On-Time"],
        ["Aug 2025", "GSTR-3B", "AA2908250571920", "2025-09-19", "31,200.00", "12,000.00", "Filed On-Time"],
        ["Sep 2025", "GSTR-3B", "AA2909250664821", "2025-10-18", "33,600.00", "13,100.00", "Filed On-Time"],
        ["Oct 2025", "GSTR-3B", "AA2910250752912", "2025-11-20", "27,900.00", "10,500.00", "Filed On-Time"],
        ["Nov 2025", "GSTR-3B", "AA2911250849201", "2025-12-19", "32,100.00", "12,800.00", "Filed On-Time"],
        ["Dec 2025", "GSTR-3B", "AA2912250938192", "2026-01-20", "29,400.00", "11,600.00", "Filed On-Time"],
        ["Jan 2026", "GSTR-3B", "AA2901261029103", "2026-02-18", "31,800.00", "12,200.00", "Filed On-Time"],
        ["Feb 2026", "GSTR-3B", "AA2902261118294", "2026-03-19", "30,500.00", "11,900.00", "Filed On-Time"],
        ["Mar 2026", "GSTR-3B", "AA2903261209185", "2026-04-19", "30,805.08", "12,700.00", "Filed On-Time"]
    ]
    fl_t = Table(filing_log, colWidths=[55, 60, 115, 65, 80, 65, 64])
    fl_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#064e3b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fdf4")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(fl_t)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Auditor Note: GSTR-2B vs GSTR-3B reconciliation indicates 100% matched input tax credit. No mismatched or inadmissible ITC claimed under Section 16(2) of the CGST Act.", s["Callout"]))
    story.append(PageBreak())

    # PAGES 5 - 14: 10 ITEMIZED INVOICES
    invoices_apex = [
        ("INV-2026-001", "Infosense Technologies Pvt Ltd", "29AABCI5541L1Z0", "29 (KA)", "Cloud Modernization & DevOps Architecture", 250000, "paid", "2025-05-15", "2025-05-28", "RTGS-ICICI-001928", "Bangalore Tech Park, KA"),
        ("INV-2026-002", "Titan Infrastructure Corp", "27AAACT9901M1ZA", "27 (MH)", "Enterprise Kubernetes Migration & Observability", 340000, "paid", "2025-06-20", "2025-07-02", "NEFT-HDFC-991823", "Bandra Kurla Complex, Mumbai"),
        ("INV-2026-003", "Wipro Digital Engineering Labs", "29AAACW1122D1ZQ", "29 (KA)", "Generative AI LangGraph Pipeline Implementation", 180000, "paid", "2025-07-10", "2025-07-22", "IMPS-HDFC-118290", "Sarjapur Road, Bengaluru"),
        ("INV-2026-004", "Zenith Media & Entertainment", "07AAGFZ9012C1Z8", "07 (DL)", "Automated Content Personalization Platform", 220000, "paid", "2025-08-18", "2025-09-01", "IMPS-AXIS-882190", "Connaught Place, New Delhi"),
        ("INV-2026-005", "Nexus Health Informatics Ltd", "33AABCN7788P1Z3", "33 (TN)", "HIPAA-Compliant Patient Telemetry Pipeline", 310000, "paid", "2025-09-25", "2025-10-12", "RTGS-KOTAK-441298", "Tidel Park, Chennai"),
        ("INV-2026-006", "Starlight Retail Solutions", "36AABCS4455E1ZV", "36 (TS)", "Omnichannel Real-Time Inventory Microservices", 270000, "paid", "2025-11-04", "2025-11-19", "NEFT-SBI-772190", "HITEC City, Hyderabad"),
        ("INV-2026-007", "Aura Cloud Analytics Pvt Ltd", "27AABCA3311K1Z9", "27 (MH)", "Data Lakehouse & DBT Pipeline Construction", 280000, "paid", "2025-12-15", "2026-01-05", "RTGS-HDFC-663819", "Cyber City, Magarpatta, Pune"),
        ("INV-2026-008", "Kavach Security Solutions", "27AABCK5678B1Z2", "27 (MH)", "SOC 2 Type II Remediation & Cryptographic Audit", 210000, "overdue", "2026-01-10", "Pending (Overdue > 45d)", "Pending Settlement", "BKC, Bandra, Mumbai"),
        ("INV-2026-009", "HyperScale SaaS Systems", "29AAACH8877B1ZN", "29 (KA)", "Multi-Tenant PostgreSQL Partitioning & Sharding", 240000, "issued", "2026-02-14", "Due in 15d", "Pending (Net 30)", "Koramangala, Bengaluru"),
        ("INV-2026-010", "Quantum Edge Robotics LLP", "07AAGFQ4412R1Z7", "07 (DL)", "Edge AI Firmware Integration & Stream Telemetry", 180000, "issued", "2026-03-02", "Due in 25d", "Pending (Net 30)", "Aerocity, New Delhi")
    ]

    for inv_num, client, gstin, state, desc, base_amt, status, inv_date, pay_date, bank_ref, addr in invoices_apex:
        story.append(Paragraph(f"Tax Invoice: {inv_num}", s["H1"]))
        is_interstate = "29" not in state
        tax_rate = 18.0
        tax_amt = round(base_amt * (tax_rate / 100.0), 2)
        total_amt = round(base_amt + tax_amt, 2)
        irn = f"4a9f8b2c1d0e{inv_num.replace('-', '').lower()}99a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1"

        # Invoice Header Info
        inv_head = [
            ["Invoice Number:", inv_num, "Invoice Date:", inv_date],
            ["IRN (e-Invoice Hash):", irn[:42] + "...", "Ack No & Date:", f"112610{inv_num[-3:]} · {inv_date}"],
            ["Client Legal Name:", client, "Client GSTIN:", gstin],
            ["Billing Address:", addr, "Place of Supply:", f"State Code {state}"],
            ["Issuer Legal Name:", "Apex Global Technologies Pvt Ltd", "Issuer GSTIN:", "29AAACA1234A1Z5 (Karnataka)"],
            ["Payment Terms:", "Net 30 Days", "Current Status:", status.upper()]
        ]
        head_t = Table(inv_head, colWidths=[95, 160, 95, 154])
        head_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(head_t)
        story.append(Spacer(1, 8))

        # Line Items
        item_table = [
            ["Sl", "Service Description & Deliverable Milestone", "SAC Code", "Rate (INR)", "Qty", "Amount (INR)"],
            ["1", desc, "998314", f"{base_amt:,.2f}", "1.00", f"{base_amt:,.2f}"],
            ["2", "Production Architecture Review & SLA Verification", "998314", "Included", "1.00", "0.00"],
            ["3", "Automated Regression Test Suite & Handover Manual", "998314", "Included", "1.00", "0.00"],
            ["", "Subtotal (Taxable Value)", "", "", "", f"{base_amt:,.2f}"]
        ]
        if is_interstate:
            item_table.append(["", "Integrated GST (IGST @ 18.0%)", "", "", "", f"{tax_amt:,.2f}"])
        else:
            cgst = tax_amt / 2.0
            item_table.append(["", "Central GST (CGST @ 9.0%)", "", "", "", f"{cgst:,.2f}"])
            item_table.append(["", "State GST (SGST @ 9.0%)", "", "", "", f"{cgst:,.2f}"])
        item_table.append(["", "Grand Total Payable (INR)", "", "", "", f"{total_amt:,.2f}"])

        it_t = Table(item_table, colWidths=[20, 240, 50, 60, 30, 104])
        it_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e1b4b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0e7ff")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(it_t)
        story.append(Spacer(1, 8))

        # Tax Breakdown Sub-Table
        if is_interstate:
            tax_sub = [
                ["SAC Code", "Taxable Value", "CGST Rate", "CGST Amt", "SGST Rate", "SGST Amt", "IGST Rate", "IGST Amt"],
                ["998314", f"{base_amt:,.2f}", "-", "0.00", "-", "0.00", "18.0%", f"{tax_amt:,.2f}"]
            ]
        else:
            cgst = tax_amt / 2.0
            tax_sub = [
                ["SAC Code", "Taxable Value", "CGST Rate", "CGST Amt", "SGST Rate", "SGST Amt", "IGST Rate", "IGST Amt"],
                ["998314", f"{base_amt:,.2f}", "9.0%", f"{cgst:,.2f}", "9.0%", f"{cgst:,.2f}", "-", "0.00"]
            ]
        ts_t = Table(tax_sub, colWidths=[54, 75, 55, 60, 55, 60, 65, 80])
        ts_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(ts_t)
        story.append(Spacer(1, 8))

        # Bank Remittance & Statutory Disclosures
        pay_info = [
            ["Beneficiary Name:", "Apex Global Technologies Pvt Ltd", "Bank Name:", "HDFC Bank Ltd"],
            ["Current Account No:", "50200088991122 (Current A/c)", "IFSC Code:", "HDFC0000123 (Richmond Rd)"],
            ["Payment Verification:", f"Status: {status.upper()} | Ref: {bank_ref}", "TDS Section:", "Section 194J @ 2% / 10%"],
            ["Interest Clause:", "18% p.a. charged on overdue invoices after 30 days under MSMED Act 2006.", "Jurisdiction:", "Bengaluru Courts Only"]
        ]
        p_t = Table(pay_info, colWidths=[100, 160, 90, 154])
        p_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(p_t)
        story.append(Spacer(1, 8))

        # Sign-off box
        sig_data = [
            ["Declaration: We declare that this invoice shows the actual price of the services described and that all particulars are true and correct.",
             "For Apex Global Technologies Pvt Ltd\n\n\n___________________________\nAuthorized Signatory (Digital Stamp)"]
        ]
        sig_t = Table(sig_data, colWidths=[310, 194])
        sig_t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(sig_t)
        story.append(PageBreak())

    # PAGES 15 - 18: CLIENT LEDGERS (4 Pages)
    client_ledgers = [
        ("Titan Infrastructure Corp", "27AAACT9901M1ZA", "27 (MH)", "INV-2026-002", 340000, 340000, 0, "NEFT-HDFC-991823", "2025-06-20", "2025-07-02", "Settled in Full"),
        ("Infosense Technologies Pvt Ltd", "29AABCI5541L1Z0", "29 (KA)", "INV-2026-001", 250000, 250000, 0, "RTGS-ICICI-001928", "2025-05-15", "2025-05-28", "Settled in Full"),
        ("Zenith Media & Entertainment", "07AAGFZ9012C1Z8", "07 (DL)", "INV-2026-004", 220000, 220000, 0, "IMPS-AXIS-882190", "2025-08-18", "2025-09-01", "Settled in Full"),
        ("Kavach Security Solutions", "27AABCK5678B1Z2", "27 (MH)", "INV-2026-008", 210000, 0, 210000, "Pending Escalation", "2026-01-10", "Overdue > 45d", "Overdue Escalation")
    ]

    for cname, cgstin, cstate, inv, b_amt, c_amt, bal, ref, idate, pdate, status_text in client_ledgers:
        story.append(Paragraph(f"Client Ledger Account: {cname}", s["H1"]))
        story.append(Paragraph("Statutory Double-Entry Ledger Statement & Aging Schedule (FY 2025-26)", s["H2"]))

        c_meta = [
            ["Client Legal Name:", cname, "Account Code:", f"CL-{cgstin[2:7]}-2026"],
            ["Client GSTIN:", cgstin, "Place of Supply:", f"State Code {cstate}"],
            ["Credit Limit (INR):", "INR 10,00,000.00", "Payment Terms:", "Net 30 Days (Direct RTGS/NEFT)"],
            ["Reconciliation Status:", status_text.upper(), "Audit Status:", "Confirmed via Statutory Letter"]
        ]
        cm_t = Table(c_meta, colWidths=[100, 160, 95, 149])
        cm_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(cm_t)
        story.append(Spacer(1, 8))

        # Ledger Entries
        tds_amt = round(b_amt * 0.02, 2) if c_amt > 0 else 0.0
        net_bank = c_amt - tds_amt if c_amt > 0 else 0.0
        
        ledg_data = [
            ["Date", "Transaction Particulars & Voucher Ref", "Voucher Type", "Debit (INR)", "Credit (INR)", "Running Balance (INR)"],
            ["2025-04-01", "Opening Balance Brought Forward", "OB-001", "0.00", "0.00", "0.00"],
            [idate, f"Service Billed under Tax Invoice {inv}", "Sales Inv", f"{b_amt:,.2f}", "0.00", f"{b_amt:,.2f} Dr"]
        ]
        if c_amt > 0:
            ledg_data.append([pdate, f"TDS Deduction by Client u/s 194J (2%)", "Journal (TDS)", "0.00", f"{tds_amt:,.2f}", f"{(b_amt - tds_amt):,.2f} Dr"])
            ledg_data.append([pdate, f"Direct Bank Deposit Realized ({ref})", "Bank Receipt", "0.00", f"{net_bank:,.2f}", "0.00 Cr"])
        ledg_data.append(["2026-03-31", "Closing Ledger Balance as on Year-End", "Balance C/F", f"{b_amt:,.2f}", f"{c_amt:,.2f}", f"{bal:,.2f} {'Dr (Overdue)' if bal > 0 else 'Settled'}"])

        l_t = Table(ledg_data, colWidths=[65, 175, 65, 65, 65, 69])
        l_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8fafc")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(l_t)
        story.append(Spacer(1, 8))

        # Aging Schedule Table
        story.append(Paragraph("Trade Receivables Aging Analysis", s["H2"]))
        if bal > 0:
            aging_data = [
                ["Current (0-30d)", "31-60 Days", "61-90 Days", "> 90 Days", "Total Outstanding", "Recovery Action Status"],
                ["0.00", f"{bal:,.2f}", "0.00", "0.00", f"{bal:,.2f}", "Section 18 MSMED Legal Notice Dispatched"]
            ]
        else:
            aging_data = [
                ["Current (0-30d)", "31-60 Days", "61-90 Days", "> 90 Days", "Total Outstanding", "Recovery Action Status"],
                ["0.00", "0.00", "0.00", "0.00", "0.00", "Account Fully Settled | No Dues Certificate Issued"]
            ]
        ag_t = Table(aging_data, colWidths=[75, 75, 70, 70, 85, 129])
        ag_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(ag_t)
        story.append(Spacer(1, 8))

        # Form 26AS TDS Certificate Cross-Check
        story.append(Paragraph("Statutory Form 26AS TDS & Tax Credit Reconciliation", s["H2"]))
        tds_check = [
            ["Financial Year", "Section", "Gross Amount Billed", "TDS Deducted (INR)", "Challan / BSR Code", "26AS Match Status"],
            ["2025-26", "194J", f"{b_amt:,.2f}", f"{tds_amt:,.2f}", f"BSR-0291029 · CH-1928" if tds_amt > 0 else "N/A", "100% Matched" if tds_amt > 0 else "Pending Deposit"]
        ]
        tc_t = Table(tds_check, colWidths=[70, 60, 95, 90, 115, 74])
        tc_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#475569")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(tc_t)
        story.append(Spacer(1, 6))
        story.append(Paragraph("Audit Verification: External ledger balance confirmation letter dispatched and cross-referenced with bank scroll records.", s["Callout"]))
        story.append(PageBreak())

    # PAGES 19 - 21: EXPENSES & OPEX (3 Pages)
    exp_sections = [
        ("Cloud Infrastructure, Compute & Hosting Disbursements", 350000, [
            ("AWS EMEA SARL (EC2, S3, RDS, EKS Production Clusters)", "PO-AWS-2025-01", "INV-EU-991823", "2025-06-30", "Direct Debit", 240000, 43200, 283200),
            ("Datadog Ireland Observability & APM Infrastructure Monitoring", "PO-DD-2025-04", "DD-9928190", "2025-09-15", "Credit Card", 65000, 11700, 76700),
            ("Cloudflare Inc Enterprise CDN, WAF & Zero-Trust Access Gateway", "PO-CF-2025-08", "CF-3391820", "2025-12-10", "Credit Card", 45000, 8100, 53100),
        ]),
        ("Office Lease, Managed Facilities & Operations Overhead", 320000, [
            ("Embassy TechVillage Managed Enterprise Office Leased Space", "PO-ETV-2025-01", "ETV-2025-99", "2025-05-05", "Bank Transfer", 220000, 39600, 259600),
            ("Tata Communications Leased Fiber Bandwidth (1 Gbps Redundant)", "PO-TATA-2025-02", "TCL-118290", "2025-08-12", "Direct Debit", 35000, 6300, 41300),
            ("Dell Technologies Developer Hardware, 4K Displays & Workstations", "PO-DELL-2025-06", "DEL-449182", "2025-11-20", "Vendor Inv", 65000, 11700, 76700),
        ]),
        ("Professional Contractor Retainers & Advisory Payouts", 170000, [
            ("DevOps & SRE Specialist Contractors (2 Senior Fractional Engineers)", "PO-CON-2025-01", "CON-882190", "2025-07-28", "Bank Transfer", 110000, 19800, 129800),
            ("KPMG India Statutory Legal Counsel & Direct Tax Advisory", "PO-KPMG-2025-03", "KPMG-77192", "2025-10-15", "Vendor Inv", 40000, 7200, 47200),
            ("HDFC ERGO Group Comprehensive Health & Accidental Insurance", "PO-INS-2025-09", "HE-1192830", "2026-01-05", "Annual Prem", 20000, 3600, 23600),
        ])
    ]

    for title, total_sub, rows in exp_sections:
        story.append(Paragraph(f"Operational Expenses: {title}", s["H1"]))
        story.append(Paragraph("Schedule 14 Statutory Voucher Disbursals & ITC Verification", s["H2"]))

        exp_table = [["Vendor Name & Service Scope", "PO Number", "Invoice Ref", "Date", "Mode", "Base (INR)", "ITC 18%", "Gross (INR)"]]
        for vname, po, vref, vdate, mode, bamt, itc, gross in rows:
            exp_table.append([vname, po, vref, vdate, mode, f"{bamt:,.2f}", f"{itc:,.2f}", f"{gross:,.2f}"])
        exp_table.append(["Subtotal Budget Head Disbursed", "", "", "", "", f"{total_sub:,.2f}", f"{(total_sub*0.18):,.2f}", f"{(total_sub*1.18):,.2f}"])

        e_t = Table(exp_table, colWidths=[150, 60, 55, 45, 50, 48, 44, 52])
        e_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c2d12")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 6.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff7ed")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fed7aa")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(e_t)
        story.append(Spacer(1, 8))

        # Monthly Budget vs Actual Variance Table
        story.append(Paragraph("Quarterly Budget Allocation vs Actual Utilization", s["H2"]))
        b_q = total_sub / 4.0
        b_data = [
            ["Quarter Period", "Approved Budget (INR)", "Actual Disbursal (INR)", "Variance (INR)", "Variance %", "Audit Status"],
            ["Q1 (Apr - Jun 2025)", f"{b_q:,.2f}", f"{(b_q * 0.95):,.2f}", f"+ {(b_q * 0.05):,.2f}", "+ 5.0% Favorable", "Within Budget"],
            ["Q2 (Jul - Sep 2025)", f"{b_q:,.2f}", f"{(b_q * 1.02):,.2f}", f"- {(b_q * 0.02):,.2f}", "- 2.0% Unfavorable", "Board Approved"],
            ["Q3 (Oct - Dec 2025)", f"{b_q:,.2f}", f"{(b_q * 0.98):,.2f}", f"+ {(b_q * 0.02):,.2f}", "+ 2.0% Favorable", "Within Budget"],
            ["Q4 (Jan - Mar 2026)", f"{b_q:,.2f}", f"{(b_q * 1.05):,.2f}", f"- {(b_q * 0.05):,.2f}", "- 5.0% Unfavorable", "Year-end Accrual"],
            ["Consolidated Annual Total", f"{total_sub:,.2f}", f"{total_sub:,.2f}", "0.00", "0.0% On Target", "Reconciled"]
        ]
        b_t = Table(b_data, colWidths=[105, 85, 85, 75, 75, 79])
        b_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#431407")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff7ed")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ffedd5")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(b_t)
        story.append(Spacer(1, 8))

        # Statutory Withholding Tax (TDS Section 194C / 194J)
        story.append(Paragraph("Statutory Tax Deducted at Source (TDS Compliance)", s["H2"]))
        tds_exp = [
            ["Tax Section", "Category Description", "Gross Base Disbursed", "Applicable Rate", "TDS Deducted", "Deposit Challan Ref"],
            ["Section 194J", "Professional Technical & Cloud Fees", f"{total_sub:,.2f}", "2.0% / 10.0%", f"{(total_sub * 0.02):,.2f}", "CH-CENTRAL-009182"],
        ]
        te_t = Table(tds_exp, colWidths=[70, 150, 95, 65, 60, 64])
        te_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#57534e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(te_t)
        story.append(Spacer(1, 6))
        story.append(Paragraph("Audit Attestation: All vendor expense vouchers have been cross-checked with corresponding GST input tax credit (ITC) entries in GSTR-2B. Total eligible ITC verified: INR 1,45,400.00.", s["Callout"]))
        story.append(PageBreak())

    # PAGES 22 - 23: WORKING CAPITAL & RUNWAY (2 Pages)
    # Page 22: Part 1 - Working Capital Balance Sheet & 12-Month Trajectory
    story.append(Paragraph("7. Working Capital & Liquidity Trajectory (Part 1)", s["H1"]))
    story.append(Paragraph("Balance Sheet Liquidity Position & 12-Month Operating Cash Flows", s["H2"]))
    
    wc_snapshot = [
        ["Balance Sheet Head", "Classification", "Audited As On 31-Mar-2026 (INR)", "Liquidity Status"],
        ["Trade Receivables (Debtors)", "Current Asset", "6,30,000.00", "High Realizability (< 45 Days)"],
        ["Cash & Bank Balances (HDFC Bank)", "Liquid Current Asset", "10,10,000.00", "Immediately Available Liquid Reserves"],
        ["GST Input Tax Credit Ledger", "Current Asset", "1,45,400.00", "Eligible for Future Output Tax Offset"],
        ["Total Current Assets (A)", "Gross Current Assets", "17,85,400.00", "Unencumbered Liquid Portfolio"],
        ["Trade Payables (Vendor Dues)", "Current Liability", "2,35,000.00", "Within 30-Day Vendor Payment Terms"],
        ["Statutory Tax Payables (GST & TDS)", "Current Liability", "82,400.00", "Cleared on Subsequent Due Dates"],
        ["Total Current Liabilities (B)", "Gross Current Liabilities", "3,17,400.00", "Manageable Short-term Commitments"],
        ["Net Working Capital (A - B)", "Net Operating Capital", "+ 14,68,000.00", "Current Ratio = 5.62 : 1 (Robust Buffer)"]
    ]
    wcs_t = Table(wc_snapshot, colWidths=[140, 110, 120, 134])
    wcs_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e1b4b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8fafc")]),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#e0e7ff")),
        ("FONTNAME", (0, 4), (-1, 4), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dcfce7")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(wcs_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("12-Month Operating Cash Inflow vs Outflow Ledger (FY 2025-26)", s["H2"]))
    months_flow = [
        ["Month", "Inflows (INR)", "Outflows (INR)", "Net Flow (INR)", "Closing Cash Buffer", "Burn Coverage"],
        ["Apr 2025", "1,50,000.00", "60,000.00", "+ 90,000.00", "1,90,000.00", "3.17 Months"],
        ["May 2025", "1,80,000.00", "65,000.00", "+ 1,15,000.00", "3,05,000.00", "4.69 Months"],
        ["Jun 2025", "1,20,000.00", "65,000.00", "+ 55,000.00", "3,60,000.00", "5.53 Months"],
        ["Jul 2025", "2,10,000.00", "70,000.00", "+ 1,40,000.00", "5,00,000.00", "7.14 Months"],
        ["Aug 2025", "1,60,000.00", "70,000.00", "+ 90,000.00", "5,90,000.00", "8.42 Months"],
        ["Sep 2025", "1,40,000.00", "70,000.00", "+ 70,000.00", "6,60,000.00", "9.43 Months"],
        ["Oct 2025", "1,50,000.00", "68,000.00", "+ 82,000.00", "7,42,000.00", "10.91 Months"],
        ["Nov 2025", "1,30,000.00", "68,000.00", "+ 62,000.00", "8,04,000.00", "11.82 Months"],
        ["Dec 2025", "1,40,000.00", "69,000.00", "+ 71,000.00", "8,75,000.00", "12.68 Months"],
        ["Jan 2026", "1,60,000.00", "78,000.00", "+ 82,000.00", "9,57,000.00", "12.26 Months"],
        ["Feb 2026", "1,50,000.00", "78,000.00", "+ 72,000.00", "10,29,000.00", "13.19 Months"],
        ["Mar 2026", "1,60,000.00", "79,000.00", "+ 81,000.00", "10,10,000.00", "12.78 Months"]
    ]
    mf_t = Table(months_flow, colWidths=[70, 85, 85, 85, 95, 84])
    mf_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(mf_t)
    story.append(PageBreak())

    # Page 23: Part 2 - Stress Testing, Debt Recovery & Capital Allocation
    story.append(Paragraph("7. Working Capital & Liquidity Trajectory (Part 2)", s["H1"]))
    story.append(Paragraph("Stress Scenario Modeling, Overdue Recovery & Capital Allocation Policy", s["H2"]))

    runway_data = [
        ["Simulation Scenario", "Monthly Inflows", "Monthly Burn", "Net Monthly Burn", "Calculated Runway", "Risk Rating"],
        ["Base Case (Current Trajectory)", "INR 2,06,666.00", "INR 70,000.00", "+ INR 1,36,666.00", "Infinite (Self-Sustaining)", "Low Risk"],
        ["Stressed (30% Billing Drop)", "INR 1,44,666.00", "INR 70,000.00", "+ INR 74,666.00", "Infinite (Positive Cash)", "Moderate Risk"],
        ["Severe Contraction (50% Drop)", "INR 1,03,333.00", "INR 70,000.00", "+ INR 33,333.00", "Self-Sustaining", "Elevated Risk"],
        ["Zero Revenue Black Swan", "INR 0.00", "INR 70,000.00", "- INR 70,000.00", "14.4 Months (INR 10.1L)", "Severe Stress"]
    ]
    r_t = Table(runway_data, colWidths=[125, 75, 75, 80, 85, 64])
    r_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(r_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Debtor Recovery Schedule & Legal Remediation (MSMED Act 2006)", s["H2"]))
    debt_recovery = [
        ["Debtor Entity", "Invoice Ref", "Due Date", "Overdue Days", "Amount Due", "Remediation Action & Stage"],
        ["Kavach Security Solutions", "INV-2026-008", "2026-02-10", "50 Days", "INR 2,10,000.00", "Statutory Demand Notice Issued u/s 15 MSMED"],
        ["HyperScale SaaS Systems", "INV-2026-009", "2026-03-16", "15 Days", "INR 2,40,000.00", "Routine Corporate Follow-up / Net 30 Term"],
        ["Quantum Edge Robotics", "INV-2026-010", "2026-04-01", "0 Days", "INR 1,80,000.00", "Fresh Milestone Invoice / Under Grace Period"],
        ["Total Pending Collections", "-", "-", "-", "INR 6,30,000.00", "Active Recovery Pipeline"]
    ]
    dr_t = Table(debt_recovery, colWidths=[120, 65, 55, 55, 80, 129])
    dr_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#831843")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fdf2f8")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fce7f3")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(dr_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Capital Allocation Recommendations for Board of Directors (FY 2026-27)", s["H2"]))
    story.append(Paragraph(
        "1. Treasury Deployment: Deploy INR 6,00,000 of surplus liquidity into AAA-rated corporate overnight treasury funds yielding 7.2% annualized.\n"
        "2. MSMED Act Invocation: Enforce compound interest claims at three times the RBI bank rate under Section 16 of the MSMED Act 2006 for accounts exceeding 45 days.\n"
        "3. Operating Expenditure Cap: Mandate a strict ceiling of INR 80,000 per month for operational vendor commitments in Q1 FY 2026-27.", s["Body"]
    ))
    story.append(PageBreak())

    # PAGE 24: STATUTORY INDEPENDENT AUDITOR VERIFICATION & CARO 2020
    story.append(Paragraph("8. Statutory Independent Auditor Verification", s["H1"]))
    story.append(Paragraph("Independent Auditor's Report Under Section 143 of Companies Act 2013", s["H2"]))
    story.append(Paragraph(
        "To the Members of Apex Global Technologies Private Limited:\n"
        "We have audited the accompanying financial statements of Apex Global Technologies Pvt Ltd ('the Company'), which comprise the Balance Sheet "
        "as at 31 March 2026, the Statement of Profit and Loss, and the Cash Flow Statement for the year then ended. In our opinion and to the best of our "
        "information, the aforesaid financial statements give the information required by the Companies Act 2013 in the manner so required and give a true "
        "and fair view in conformity with the accounting principles generally accepted in India, of the state of affairs of the Company as at 31 March 2026.", s["Body"]
    ))
    story.append(Spacer(1, 6))

    # CARO 2020 Checklist Table
    story.append(Paragraph("Companies (Auditor's Report) Order, 2020 (CARO 2020) Checklist", s["H2"]))
    caro_data = [
        ["Clause", "CARO 2020 Reporting Requirement", "Auditor Finding & Verification", "Compliance Status"],
        ["(i)", "Maintenance of proper records of Property, Plant and Equipment", "Full asset register maintained; physical verification complete", "Compliant"],
        ["(ii)", "Physical verification of inventory & working capital limits", "Software services entity; no inventory holding required", "Not Applicable"],
        ["(iii)", "Investments, guarantees, security, loans or advances granted", "Zero loans or guarantees extended to related entities", "Compliant"],
        ["(vii)", "Undisputed statutory dues including GST, PF, ESI, Income Tax", "All monthly GST and TDS dues deposited within statutory timelines", "100% Compliant"],
        ["(ix)", "Default in repayment of loans or other borrowings", "Company has zero long-term debt or bank borrowings", "Compliant"],
        ["(xi)", "Reporting of fraud by the company or on the company", "Zero instances of fraud noticed or reported during the audit year", "Nil Fraud"],
        ["(xxi)", "Qualifications or adverse remarks in CARO reports", "Unqualified Clean Opinion issued; nil adverse remarks", "Clean Opinion"]
    ]
    c_t = Table(caro_data, colWidths=[35, 185, 214, 70])
    c_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e1b4b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(c_t)
    story.append(Spacer(1, 8))

    # Dual Signature Table
    sign_data = [
        ["For S.R. Batliboi & Associates LLP", "For and on behalf of the Board of Directors"],
        ["Chartered Accountants (ICAI Reg No: 101049W)", "Apex Global Technologies Pvt Ltd"],
        ["\n___________________________\nRajesh V. Sharma, FCA\nPartner (Membership No: 049210)\nUDIN: 26049210AAAAAB1920\nPlace: Bengaluru | Date: 15 April 2026",
         "\n___________________________\nVikramaditya Rao\nManaging Director (DIN: 08912344)\nPlace: Bengaluru | Date: 15 April 2026"]
    ]
    s_t = Table(sign_data, colWidths=[250, 254])
    s_t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(s_t)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Built Apex Global PDF at {out_path}")


# =========================================================================
# 2. KAVACH SECURITY SOLUTIONS (25 Pages)
# =========================================================================
def build_kavach_security_pdf(out_path: str):
    """Builds a rich, completely populated 25-page financial audit dossier for Kavach Security Solutions."""
    doc = SimpleDocTemplate(
        out_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    s = get_audit_styles(primary_hex="#0c4a6e", secondary_hex="#0284c7")
    story = []

    # PAGE 1: COVER
    story.append(Spacer(1, 40))
    story.append(Paragraph("KAVACH SECURITY SOLUTIONS PVT LTD", s["CoverTitle"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Annual Operations & Cybersecurity Audit Report", s["CoverSub"]))
    story.append(Paragraph("ISO 27001:2022 & SOC 2 Type II Certified Financial & Infrastructure Records", s["Callout"]))
    story.append(Spacer(1, 25))

    meta_table = Table([
        ["Corporate Entity:", "Kavach Security Solutions Private Limited"],
        ["CIN / Corporate Identity No:", "U74999MH2020PTC339812 (Registered in Maharashtra)"],
        ["GSTIN (Maharashtra Origin):", "27AABCK5678B1Z2 (State Code 27 — Maharashtra)"],
        ["Permanent Account No (PAN):", "AABCK5678B (Corporate Tax Ward 3(2), Mumbai)"],
        ["Registered Corporate Office:", "Bandra-Kurla Complex (BKC), Bandra East, Mumbai, Maharashtra 400051"],
        ["Reporting Fiscal Cycle:", "FY 2025 – 2026 (01 April 2025 to 31 March 2026)"],
        ["Total Invoiced Revenue Billings:", "INR 38,50,000.00 (Thirty-Eight Lakh Fifty Thousand Rupees)"],
        ["Direct Direct Collections Realized:", "INR 29,00,000.00 (75.3% Direct Realization Rate)"],
        ["Operational & R&D Disbursements:", "INR 14,20,000.00 (Tier-IV DC, Cryptographic Hardware, SecOps Payroll)"],
        ["Net Cash Flow Surplus Realized:", "+ INR 14,80,000.00 (Fourteen Lakh Eighty Thousand Rupees)"],
        ["Security Accreditations:", "ISO/IEC 27001:2022, SOC 2 Type II, PCI-DSS Qualified Security Assessor"],
        ["Statutory Independent Auditor:", "Deloitte Haskins & Sells LLP (ICAI Reg No: 117366W)"]
    ], colWidths=[170, 334])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f9ff")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#0284c7")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bae6fd")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 25))

    exec_notes = [
        ["Audit Scope:", "Comprehensive audit of 11 itemized enterprise cybersecurity invoices (KAV-2026-101 to 111), customer ledgers, infrastructure leases, and multi-state GST schedules."],
        ["Compliance Framework:", "Adheres to Companies Act 2013 statutory audit guidelines and CERT-In cyber resilience frameworks."],
        ["Document Classification:", "RESTRICTED AUDIT DOSSIER — STATUTORY REGULATORY & STAKEHOLDER ARCHIVE"]
    ]
    nt = Table(exec_notes, colWidths=[120, 384])
    nt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e0f2fe")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#7dd3fc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bae6fd")),
    ]))
    story.append(nt)
    story.append(PageBreak())

    # PAGE 2: TABLE OF CONTENTS & GOVERNANCE
    story.append(Paragraph("1. Executive Summary & Audit Table of Contents", s["H1"]))
    story.append(Paragraph("To the Board of Directors, Enterprise Clients, and Statutory Auditors:", s["H2"]))
    story.append(Paragraph(
        "Kavach Security Solutions delivers mission-critical cyber defense, enterprise zero-trust infrastructure, and continuous SOC telemetry "
        "to leading banks, defense organizations, and technology conglomerates. For FY 2025-26, the company generated INR 38,50,000 in invoiced "
        "billings with direct cash collections of INR 29,00,000, establishing a net operating cash flow surplus of INR 14,80,000.", s["Body"]
    ))
    story.append(Spacer(1, 8))

    toc = [
        ["Section", "Contents & Statutory Disclosures", "Compliance Reference", "Pages"],
        ["Section 1", "Executive Summary, Corporate Governance & Index", "Sec 134 Companies Act", "2"],
        ["Section 2", "Financial KPI Overview & Annual Recurring Revenue (ARR)", "Ind AS 1 / Core Metrics", "3"],
        ["Section 3", "Multi-State GST Compliance Schedule (MH, DL, KA, TN)", "CGST / IGST Act 2017", "4"],
        ["Section 4", "Itemized Cybersecurity Tax Invoices (KAV-2026-101 to 111)", "Rule 46 Tax Invoices", "5 – 15"],
        ["Section 5", "Enterprise Customer Ledgers & Statements", "Double-Entry Ledger Ind AS 18", "16 – 19"],
        ["Section 6", "R&D, SOC Data Center & Infrastructure Expenses", "Schedule III Opex Breakdown", "20 – 22"],
        ["Section 7", "12-Month Runway Forecast & Working Capital Modeling", "Working Capital / MSMED Act", "23 – 24"],
        ["Section 8", "Independent Statutory Auditor Opinion & Signature", "SA 700 / CARO 2020", "25"]
    ]
    t = Table(toc, colWidths=[70, 234, 140, 60])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0369a1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f9ff")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Security Governance & Board Oversight Matrix", s["H2"]))
    gov_table = Table([
        ["Board Meetings Conducted:", "6 Sessions (Bi-monthly)", "Information Security Council:", "Quarterly Reviews"],
        ["CERT-In Incident Logging:", "Zero Critical Vulnerabilities", "Data Protection Officer:", "Aditya Kulkarni, CISSP"],
        ["Active Enterprise Retainers:", "14 Strategic Accounts", "Data Center Tier:", "Tier-IV Uptime Certified"],
        ["Primary Statutory Banker:", "Kotak Mahindra Bank (Nariman Point)", "SOC Operations:", "24/7/365 Continuous Watch"]
    ], colWidths=[120, 132, 120, 132])
    gov_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f9ff")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bae6fd")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(gov_table)
    story.append(PageBreak())

    # PAGE 3: KPI SCORECARD
    story.append(Paragraph("2. Financial Performance & ARR Scorecard", s["H1"]))
    story.append(Paragraph("Consolidated Financial Health Indicators (FY 2025-26)", s["H2"]))

    kpi_kavach = [
        ["Total Invoiced Revenue", "INR 38,50,000.00", "Total Collected Deposits", "INR 29,00,000.00"],
        ["Outstanding Receivables", "INR 9,50,000.00", "Total Past-Due Overdue", "INR 4,20,000.00"],
        ["Operating & R&D Expenses", "INR 14,20,000.00", "Net Realized Cash Surplus", "+ INR 14,80,000.00"],
        ["Active Enterprise Retainers", "14 Managed Accounts", "SOC Uptime SLA Achieved", "99.98%"]
    ]
    k_t = Table(kpi_kavach, colWidths=[125, 127, 125, 127])
    k_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f9ff")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f0f9ff")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bae6fd")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(k_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Cybersecurity Revenue Streams Breakdown (FY 2025-26)", s["H2"]))
    stream_data = [
        ["Service Practice Line", "Invoiced (INR)", "Share %", "Client Count", "Average Contract Value", "Growth YoY"],
        ["Managed Zero-Trust SOC & SIEM", "16,40,000.00", "42.6%", "5 Accounts", "INR 3,28,000.00", "+ 34.5%"],
        ["Penetration Testing & Red Teaming", "11,80,000.00", "30.6%", "4 Accounts", "INR 2,95,000.00", "+ 22.0%"],
        ["Hardware HSM & Encryption Setup", "6,10,000.00", "15.8%", "3 Accounts", "INR 2,03,333.00", "+ 18.2%"],
        ["Regulatory Compliance Audits (PCI/SOC)", "4,20,000.00", "10.9%", "2 Accounts", "INR 2,10,000.00", "+ 45.0%"],
        ["Total Billed Cybersecurity Portfolio", "38,50,000.00", "100.0%", "14 Contracts", "INR 2,75,000.00", "+ 28.4%"]
    ]
    st_t = Table(stream_data, colWidths=[140, 75, 50, 65, 110, 64])
    st_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#075985")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f0f9ff")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#bae6fd")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(st_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Key Solvency & Working Capital Metrics", s["H2"]))
    ratio_kav = [
        ["Financial KPI", "Reported Value", "Target Threshold", "Interpretation"],
        ["Operating Profit Margin (OPM)", "63.12%", "> 45.00%", "Substantial operating margin after R&D expenditures"],
        ["Cash Flow Realization Ratio", "75.32%", "> 70.00%", "Strong direct cash collections across banking clients"],
        ["Monthly Defensive Burn Rate", "INR 1,18,333.00", "< INR 1,50,000", "Defensive posture maintained across AWS & SOC infrastructure"],
        ["Cash Runway Coverage", "12.5 Months", "> 9.0 Months", "Net surplus INR 14.8L ensures comfortable self-sustainability"],
        ["Bad Debt Provisioning Ratio", "0.00%", "< 5.00%", "Zero unrecoverable write-offs; statutory recovery pending"]
    ]
    rk_t = Table(ratio_kav, colWidths=[130, 80, 85, 209])
    rk_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(rk_t)
    story.append(PageBreak())

    # PAGE 4: GST RECONCILIATION
    story.append(Paragraph("3. Multi-State Indian GST Breakdown (Origin MH · 27)", s["H1"]))
    story.append(Paragraph("Tax Liability Assessment & Input Tax Credit Offsets", s["H2"]))
    story.append(Paragraph(
        "Registered under Maharashtra GSTIN 27AABCK5678B1Z2. Intra-state sales within Maharashtra attract 9% CGST + 9% SGST. "
        "Inter-state clients in Karnataka, Delhi, and Tamil Nadu attract 18% IGST. Input tax credit is generated from data center leases and hardware.", s["Body"]
    ))
    story.append(Spacer(1, 6))

    gst_kav = [
        ["Tax Bracket", "Taxable Base (INR)", "Rate", "Gross Tax (INR)", "ITC Adjustment (INR)", "Net Cash Paid (INR)"],
        ["CGST (Maharashtra Intra-State)", "14,00,000.00", "9.0%", "1,26,000.00", "52,000.00", "74,000.00"],
        ["SGST (Maharashtra Intra-State)", "14,00,000.00", "9.0%", "1,26,000.00", "52,000.00", "74,000.00"],
        ["IGST (Interstate KA, DL, TN)", "18,60,169.49", "18.0%", "3,34,830.51", "1,22,000.00", "2,12,830.51"],
        ["Total Statutory GST Liability", "32,60,169.49", "-", "5,86,830.51", "2,26,000.00", "3,60,830.51"]
    ]
    gt = Table(gst_kav, colWidths=[140, 85, 40, 75, 80, 84])
    gt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#075985")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f0f9ff")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#bae6fd")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(gt)
    story.append(Spacer(1, 8))

    story.append(Paragraph("State-wise Place of Supply Distribution", s["H2"]))
    pos_data = [
        ["State of Supply", "State Code", "Customer Count", "Taxable Value (INR)", "Tax Component", "Total Invoiced (INR)"],
        ["Maharashtra (Intra-state)", "27", "6 Entities", "14,00,000.00", "CGST + SGST (18%)", "16,52,000.00"],
        ["Karnataka (Inter-state)", "29", "3 Entities", "8,90,000.00", "IGST (18%)", "10,50,200.00"],
        ["Delhi NCR (Inter-state)", "07", "3 Entities", "6,20,000.00", "IGST (18%)", "7,31,600.00"],
        ["Tamil Nadu (Inter-state)", "33", "2 Entities", "3,50,169.49", "IGST (18%)", "4,16,200.00"],
        ["Consolidated National Totals", "-", "14 Accounts", "32,60,169.49", "-", "38,50,000.00"]
    ]
    pos_t = Table(pos_data, colWidths=[120, 50, 75, 85, 90, 84])
    pos_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0c4a6e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f0f9ff")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0f2fe")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(pos_t)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Statutory Note: GSTR-3B filings executed on or before the 20th of each succeeding month. Total ITC claimed of INR 2,26,000 matches with Form GSTR-2B with zero variance.", s["Callout"]))
    story.append(PageBreak())

    # PAGES 5 - 15: 11 INVOICES
    invs_kav = [
        ("KAV-2026-101", "HDFC Securities Ltd", "27AAACH1122K1Z3", "27 (MH)", "Annual Zero-Trust SOC SIEM Retainer", 450000, "paid", "2025-04-12", "2025-04-25", "RTGS-HDFC-991823", "Nariman Point, Mumbai"),
        ("KAV-2026-102", "Reliance Cloud Platforms", "27AAACR4411D1ZQ", "27 (MH)", "Penetration Testing & Red-Teaming Simulation", 380000, "paid", "2025-05-18", "2025-06-02", "NEFT-SBI-4482910", "Navi Mumbai, MH"),
        ("KAV-2026-103", "Mahindra Defense Systems", "27AAACM8899F1ZV", "27 (MH)", "Cryptographic Key Management & HSM Integration", 520000, "paid", "2025-06-25", "2025-07-10", "RTGS-AXIS-009182", "Worli, Mumbai"),
        ("KAV-2026-104", "Tata Communications Ltd", "27AAACT9901M1ZA", "27 (MH)", "Cloud Perimeter DDOS Threat Intelligence", 320000, "paid", "2025-08-14", "2025-08-30", "IMPS-HDFC-119283", "BKC, Bandra, Mumbai"),
        ("KAV-2026-105", "Apex Global Technologies", "29AAACA1234A1Z5", "29 (KA)", "ISO 27001 Re-Certification & Remediation", 290000, "paid", "2025-09-22", "2025-10-05", "NEFT-HDFC-772819", "Outer Ring Rd, Bengaluru"),
        ("KAV-2026-106", "PayFlow Payments Network", "07AABCP3312E1ZL", "07 (DL)", "PCI-DSS 4.0 Compliance Readiness Assessment", 410000, "paid", "2025-11-08", "2025-11-24", "RTGS-ICICI-662819", "Barakhamba Rd, New Delhi"),
        ("KAV-2026-107", "Bajaj Finserv Digital", "27AAACB2299C1ZM", "27 (MH)", "Core Banking API Vulnerability Scanning", 360000, "paid", "2025-12-12", "2025-12-28", "RTGS-KOTAK-339182", "Viman Nagar, Pune"),
        ("KAV-2026-108", "CyberShield Asia Pacific", "33AABCC5544Q1ZP", "33 (TN)", "Managed Threat Hunting & Forensics Retainer", 280000, "overdue", "2026-01-05", "Pending (Overdue > 45d)", "Pending Dispute Settlement", "OMR, Chennai"),
        ("KAV-2026-109", "SecureStack Global Pte", "07AAGFS9921T1Z4", "07 (DL)", "Enterprise Identity & MFA Hardening", 140000, "overdue", "2026-01-18", "Pending (Overdue > 45d)", "Pending Escalation", "Cyber City, Gurugram"),
        ("KAV-2026-110", "OmniGuard Telecom Labs", "29AABCO7711B1ZW", "29 (KA)", "5G Core Network Slicing Security Architecture", 420000, "issued", "2026-02-15", "Due in 20d", "Pending (Net 30)", "Whitefield, Bengaluru"),
        ("KAV-2026-111", "Vanguard Health Systems", "27AABCV1199M1ZT", "27 (MH)", "Medical Device Firmware Encryption & Security", 280000, "issued", "2026-03-01", "Due in 30d", "Pending (Net 30)", "Andheri East, Mumbai")
    ]

    for inv_num, client, gstin, state, desc, base_amt, status, idate, pdate, bank_ref, addr in invs_kav:
        story.append(Paragraph(f"Tax Invoice: {inv_num}", s["H1"]))
        is_interstate = "27" not in state
        tax_amt = round(base_amt * 0.18, 2)
        total = round(base_amt + tax_amt, 2)
        irn = f"7b8c9d0e1f2a{inv_num.replace('-', '').lower()}88b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0"

        t_data = [
            ["Invoice Number:", inv_num, "Date of Issue:", idate],
            ["IRN (e-Invoice Hash):", irn[:42] + "...", "Ack No & Date:", f"272610{inv_num[-3:]} · {idate}"],
            ["Client Name:", client, "Client GSTIN:", gstin],
            ["Billing Address:", addr, "Place of Supply:", f"State Code {state}"],
            ["Issuer GSTIN:", "27AABCK5678B1Z2 (MH)", "Current Status:", status.upper()],
            ["Payment Terms:", "Net 30 Days", "Bank Ref:", pdate]
        ]
        t1 = Table(t_data, colWidths=[95, 160, 95, 154])
        t1.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t1)
        story.append(Spacer(1, 8))

        items = [
            ["Sl", "Service Description & Security Scope", "SAC", "Rate (INR)", "Qty", "Total (INR)"],
            ["1", desc, "998315", f"{base_amt:,.2f}", "1.00", f"{base_amt:,.2f}"],
            ["2", "Automated Threat Surface Mapping & CVSS Scoring", "998315", "Included", "1.00", "0.00"],
            ["3", "Attestation Report & CISO Advisory Sign-Off", "998315", "Included", "1.00", "0.00"],
            ["", "Subtotal (Taxable Value)", "", "", "", f"{base_amt:,.2f}"]
        ]
        if is_interstate:
            items.append(["", "Integrated GST (IGST @ 18.0%)", "", "", "", f"{tax_amt:,.2f}"])
        else:
            cgst = tax_amt / 2.0
            items.append(["", "Central GST (CGST @ 9.0%)", "", "", "", f"{cgst:,.2f}"])
            items.append(["", "State GST (SGST @ 9.0%)", "", "", "", f"{cgst:,.2f}"])
        items.append(["", "Total Invoice Payable", "", "", "", f"{total:,.2f}"])

        t2 = Table(items, colWidths=[20, 240, 50, 60, 30, 104])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0369a1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0f2fe")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(t2)
        story.append(Spacer(1, 8))

        # Tax Breakdown Sub-Table
        if is_interstate:
            tax_sub = [
                ["SAC Code", "Taxable Value", "CGST Rate", "CGST Amt", "SGST Rate", "SGST Amt", "IGST Rate", "IGST Amt"],
                ["998315", f"{base_amt:,.2f}", "-", "0.00", "-", "0.00", "18.0%", f"{tax_amt:,.2f}"]
            ]
        else:
            cgst = tax_amt / 2.0
            tax_sub = [
                ["SAC Code", "Taxable Value", "CGST Rate", "CGST Amt", "SGST Rate", "SGST Amt", "IGST Rate", "IGST Amt"],
                ["998315", f"{base_amt:,.2f}", "9.0%", f"{cgst:,.2f}", "9.0%", f"{cgst:,.2f}", "-", "0.00"]
            ]
        ts_t = Table(tax_sub, colWidths=[54, 75, 55, 60, 55, 60, 65, 80])
        ts_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(ts_t)
        story.append(Spacer(1, 8))

        # Settlement Info
        pay_info = [
            ["Beneficiary Name:", "Kavach Security Solutions Pvt Ltd", "Bank Name:", "Kotak Mahindra Bank"],
            ["Current Account No:", "901233881122 (Current A/c)", "IFSC Code:", "KKBK0000958 (BKC Branch)"],
            ["Payment Verification:", f"Status: {status.upper()} | Bank Ref: {bank_ref}", "TDS Section:", "Section 194J @ 2% / 10%"],
            ["Interest Clause:", "18% p.a. charged on overdue invoices after 30 days under MSMED Act 2006.", "Jurisdiction:", "Mumbai Courts Only"]
        ]
        p_t = Table(pay_info, colWidths=[100, 160, 90, 154])
        p_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(p_t)
        story.append(Spacer(1, 8))

        sig_data = [
            ["Declaration: Certified that all details, SAC classifications, and tax charges comply with Section 31 of CGST Act.",
             "For Kavach Security Solutions Pvt Ltd\n\n\n___________________________\nAuthorized Signatory (Digital Seal)"]
        ]
        sig_t = Table(sig_data, colWidths=[310, 194])
        sig_t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(sig_t)
        story.append(PageBreak())

    # PAGES 16 - 19: CUSTOMER LEDGERS (4 Pages)
    kav_ledgers = [
        ("HDFC Securities Ltd", "27AAACH1122K1Z3", "27 (MH)", "KAV-2026-101", 450000, 450000, 0, "RTGS-HDFC-991823", "2025-04-12", "2025-04-25", "Settled in Full"),
        ("Reliance Cloud Platforms", "27AAACR4411D1ZQ", "27 (MH)", "KAV-2026-102", 380000, 380000, 0, "NEFT-SBI-4482910", "2025-05-18", "2025-06-02", "Settled in Full"),
        ("CyberShield Asia Pacific", "33AABCC5544Q1ZP", "33 (TN)", "KAV-2026-108", 280000, 0, 280000, "Pending Formal Notice", "2026-01-05", "Overdue > 45d", "Overdue Escalation"),
        ("SecureStack Global Pte", "07AAGFS9921T1Z4", "07 (DL)", "KAV-2026-109", 140000, 0, 140000, "Pending Formal Notice", "2026-01-18", "Overdue > 45d", "Overdue Escalation")
    ]
    for cname, cgstin, cstate, inv, bamt, camt, bal, ref, idate, pdate, status_text in kav_ledgers:
        story.append(Paragraph(f"Customer Ledger Statement: {cname}", s["H1"]))
        story.append(Paragraph("Statutory Double-Entry Ledger Statement & Aging Schedule (FY 2025-26)", s["H2"]))

        c_meta = [
            ["Customer Legal Name:", cname, "Account Code:", f"CUST-{cgstin[2:7]}-2026"],
            ["Customer GSTIN:", cgstin, "Place of Supply:", f"State Code {cstate}"],
            ["Credit Limit (INR):", "INR 15,00,000.00", "Payment Terms:", "Net 30 Days (Direct RTGS/NEFT)"],
            ["Reconciliation Status:", status_text.upper(), "Audit Status:", "Confirmed via Statutory Balance Letter"]
        ]
        cm_t = Table(c_meta, colWidths=[100, 160, 95, 149])
        cm_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(cm_t)
        story.append(Spacer(1, 8))

        tds_amt = round(bamt * 0.02, 2) if camt > 0 else 0.0
        net_bank = camt - tds_amt if camt > 0 else 0.0
        
        ldata = [
            ["Date", "Transaction Particulars & Voucher Ref", "Voucher Type", "Debit (INR)", "Credit (INR)", "Running Balance (INR)"],
            ["2025-04-01", "Opening Balance Brought Forward", "OB-001", "0.00", "0.00", "0.00"],
            [idate, f"Cybersecurity Services Invoiced ({inv})", "Sales Inv", f"{bamt:,.2f}", "0.00", f"{bamt:,.2f} Dr"]
        ]
        if camt > 0:
            ldata.append([pdate, f"TDS Deduction by Customer u/s 194J (2%)", "Journal (TDS)", "0.00", f"{tds_amt:,.2f}", f"{(bamt - tds_amt):,.2f} Dr"])
            ldata.append([pdate, f"Direct Bank Deposit Realized ({ref})", "Bank Receipt", "0.00", f"{net_bank:,.2f}", "0.00 Cr"])
        ldata.append(["2026-03-31", "Period Closing Position as on Year-End", "Balance C/F", f"{bamt:,.2f}", f"{camt:,.2f}", f"{bal:,.2f} {'Dr (Overdue)' if bal > 0 else 'Settled'}"])

        lt = Table(ldata, colWidths=[65, 175, 65, 65, 65, 69])
        lt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0c4a6e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f0f9ff")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0f2fe")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(lt)
        story.append(Spacer(1, 8))

        # Aging Analysis
        story.append(Paragraph("Trade Receivables Aging Analysis", s["H2"]))
        if bal > 0:
            aging_data = [
                ["Current (0-30d)", "31-60 Days", "61-90 Days", "> 90 Days", "Total Outstanding", "Recovery Action Status"],
                ["0.00", f"{bal:,.2f}", "0.00", "0.00", f"{bal:,.2f}", "Formal Statutory Reminder Dispatched u/s 15 MSMED"]
            ]
        else:
            aging_data = [
                ["Current (0-30d)", "31-60 Days", "61-90 Days", "> 90 Days", "Total Outstanding", "Recovery Action Status"],
                ["0.00", "0.00", "0.00", "0.00", "0.00", "Account Reconciled & Fully Settled"]
            ]
        ag_t = Table(aging_data, colWidths=[75, 75, 70, 70, 85, 129])
        ag_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(ag_t)
        story.append(Spacer(1, 8))

        # Statutory TDS Verification
        story.append(Paragraph("Statutory Form 26AS TDS & Tax Credit Reconciliation", s["H2"]))
        tds_check = [
            ["Financial Year", "Section", "Gross Amount Billed", "TDS Deducted (INR)", "Challan / BSR Code", "26AS Match Status"],
            ["2025-26", "194J", f"{bamt:,.2f}", f"{tds_amt:,.2f}", f"BSR-0271920 · CH-9918" if tds_amt > 0 else "N/A", "100% Matched" if tds_amt > 0 else "Pending Deposit"]
        ]
        tc_t = Table(tds_check, colWidths=[70, 60, 95, 90, 115, 74])
        tc_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#475569")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(tc_t)
        story.append(Spacer(1, 6))
        story.append(Paragraph("Audit Verification: External ledger balance confirmation letter dispatched and cross-referenced with bank scroll records.", s["Callout"]))
        story.append(PageBreak())

    # PAGES 20 - 22: R&D & EXPENSES (3 Pages)
    kav_exps = [
        ("Tier-IV Data Center & Cloud Hardware Leases", 480000, [
            ("NTT Data Center Tier-IV Colocation Facility (BKC Mumbai)", "PO-NTT-2025-01", "NTT-2025-991", "2025-05-10", "Direct Debit", 280000, 50400, 330400),
            ("AWS GovCloud Dedicated Cryptographic Compute Enclaves", "PO-AWS-2025-03", "AWS-882190", "2025-08-15", "Credit Card", 120000, 21600, 141600),
            ("Tata Communications Redundant Dark Fiber Ring Connectivity", "PO-TCL-2025-07", "TCL-551920", "2025-11-25", "Bank Transfer", 80000, 14400, 94400),
        ]),
        ("Threat Intelligence Commercial Feeds & MITRE Telemetry", 320000, [
            ("CrowdStrike Falcon Cyber Threat Intelligence Enterprise Feed", "PO-CS-2025-02", "CS-9918230", "2025-06-18", "Wire Transfer", 180000, 32400, 212400),
            ("Recorded Future Dark Web Monitoring & Attack Surface Telemetry", "PO-RF-2025-05", "RF-441920", "2025-09-20", "Credit Card", 90000, 16200, 106200),
            ("VirusTotal Commercial API & YARA Real-time Malware Feed", "PO-VT-2025-09", "VT-118290", "2025-12-15", "Credit Card", 50000, 9000, 59000),
        ]),
        ("Hardware Security Modules & Dedicated Lab Procurement", 290000, [
            ("Thales Luna PCIe Hardware Security Modules (FIPS 140-2 Level 3)", "PO-TH-2025-01", "TH-772910", "2025-07-12", "Vendor Inv", 160000, 28800, 188800),
            ("Yubico Enterprise Security Keys (YubiKey 5 FIPS Tokens x 200)", "PO-YB-2025-04", "YB-229102", "2025-10-08", "Bank Transfer", 80000, 14400, 94400),
            ("Keysight Network Packet Broker & TAP Hardware Appliances", "PO-KS-2025-08", "KS-882190", "2026-01-22", "Vendor Inv", 50000, 9000, 59000),
        ])
    ]

    for title, total_sub, rows in kav_exps:
        story.append(Paragraph(f"Operational & R&D Expenditure: {title}", s["H1"]))
        story.append(Paragraph("Schedule 14 Infrastructure Disbursals & Technical Verification", s["H2"]))

        exp_table = [["Vendor Name & Equipment Scope", "PO Number", "Invoice Ref", "Date", "Mode", "Base (INR)", "ITC 18%", "Gross (INR)"]]
        for vname, po, vref, vdate, mode, bamt, itc, gross in rows:
            exp_table.append([vname, po, vref, vdate, mode, f"{bamt:,.2f}", f"{itc:,.2f}", f"{gross:,.2f}"])
        exp_table.append(["Subtotal Disbursed Under Head", "", "", "", "", f"{total_sub:,.2f}", f"{(total_sub*0.18):,.2f}", f"{(total_sub*1.18):,.2f}"])

        e_t = Table(exp_table, colWidths=[150, 60, 55, 45, 50, 48, 44, 52])
        e_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#075985")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 6.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f0f9ff")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#bae6fd")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(e_t)
        story.append(Spacer(1, 8))

        # Monthly Budget vs Actual Variance Table
        story.append(Paragraph("Quarterly Budget Allocation vs Actual Utilization", s["H2"]))
        b_q = total_sub / 4.0
        b_data = [
            ["Quarter Period", "Approved Budget (INR)", "Actual Disbursal (INR)", "Variance (INR)", "Variance %", "Audit Status"],
            ["Q1 (Apr - Jun 2025)", f"{b_q:,.2f}", f"{(b_q * 0.96):,.2f}", f"+ {(b_q * 0.04):,.2f}", "+ 4.0% Favorable", "Within Budget"],
            ["Q2 (Jul - Sep 2025)", f"{b_q:,.2f}", f"{(b_q * 1.03):,.2f}", f"- {(b_q * 0.03):,.2f}", "- 3.0% Unfavorable", "Board Approved"],
            ["Q3 (Oct - Dec 2025)", f"{b_q:,.2f}", f"{(b_q * 0.97):,.2f}", f"+ {(b_q * 0.03):,.2f}", "+ 3.0% Favorable", "Within Budget"],
            ["Q4 (Jan - Mar 2026)", f"{b_q:,.2f}", f"{(b_q * 1.04):,.2f}", f"- {(b_q * 0.04):,.2f}", "- 4.0% Unfavorable", "Hardware Capex"],
            ["Consolidated Annual Total", f"{total_sub:,.2f}", f"{total_sub:,.2f}", "0.00", "0.0% On Target", "Reconciled"]
        ]
        b_t = Table(b_data, colWidths=[105, 85, 85, 75, 75, 79])
        b_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0c4a6e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f0f9ff")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e0f2fe")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(b_t)
        story.append(Spacer(1, 8))

        # Statutory TDS
        story.append(Paragraph("Statutory Tax Deducted at Source (TDS Compliance)", s["H2"]))
        tds_exp = [
            ["Tax Section", "Category Description", "Gross Base Disbursed", "Applicable Rate", "TDS Deducted", "Deposit Challan Ref"],
            ["Section 194C / 194J", "Hardware & Telecom Infrastructure Leases", f"{total_sub:,.2f}", "2.0%", f"{(total_sub * 0.02):,.2f}", "CH-MUMBAI-004481"],
        ]
        te_t = Table(tds_exp, colWidths=[75, 150, 95, 60, 60, 64])
        te_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(te_t)
        story.append(Spacer(1, 6))
        story.append(Paragraph("Audit Attestation: Hardware asset tags verified against physical data center racks. Eligible ITC of INR 2,26,000 claimed in full.", s["Callout"]))
        story.append(PageBreak())

    # PAGES 23 - 24: RUNWAY & SOLVENCY MODELING (2 Pages)
    # Page 23: Part 1 - Working Capital Balance Sheet & 12-Month Flow
    story.append(Paragraph("7. Financial Runway & Capital Solvency (Part 1)", s["H1"]))
    story.append(Paragraph("Working Capital Position & 12-Month Defensive Cash Trajectory", s["H2"]))

    wc_kav = [
        ["Balance Sheet Head", "Category", "Audited Position (INR)", "Liquidity Assessment"],
        ["Trade Receivables (Enterprise Debtors)", "Current Asset", "9,50,000.00", "Secured under Enterprise Master Service Agreements"],
        ["Cash & Bank Balances (Kotak Bank BKC)", "Liquid Cash", "14,80,000.00", "Direct Liquid Capital in Current Account"],
        ["Hardware Security Asset Inventory", "Fixed Asset", "4,80,000.00", "Depreciated under Ind AS 16 @ 33.33% p.a."],
        ["GST ITC Credit Balance", "Statutory Asset", "2,26,000.00", "Available for Offset Against FY27 Output Dues"],
        ["Total Liquid & Current Assets (A)", "Gross Current Assets", "26,56,000.00", "Substantial Unencumbered Capital"],
        ["Trade Creditors & Hardware Payables", "Current Liability", "3,40,000.00", "Settled on 30-Day Vendor Cycles"],
        ["Statutory Tax Payables (GST & TDS)", "Current Liability", "1,20,000.00", "Cleared on Subsequent Due Dates"],
        ["Total Current Liabilities (B)", "Gross Current Liabilities", "4,60,000.00", "Low Leverage; Zero Bank Overdraft"],
        ["Net Working Capital (A - B)", "Net Operating Capital", "+ 21,96,000.00", "Current Ratio = 5.77 : 1 (Exceptional Solvency)"]
    ]
    wck_t = Table(wc_kav, colWidths=[140, 110, 120, 134])
    wck_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0c4a6e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f0f9ff")]),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#bae6fd")),
        ("FONTNAME", (0, 4), (-1, 4), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dcfce7")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(wck_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("12-Month Operating Cash Inflow vs Outflow Ledger (FY 2025-26)", s["H2"]))
    months_flow_kav = [
        ["Month", "Inflows (INR)", "Outflows (INR)", "Net Flow (INR)", "Closing Cash Buffer", "Burn Coverage"],
        ["Apr 2025", "2,40,000.00", "1,10,000.00", "+ 1,30,000.00", "3,30,000.00", "3.00 Months"],
        ["May 2025", "2,80,000.00", "1,15,000.00", "+ 1,65,000.00", "4,95,000.00", "4.30 Months"],
        ["Jun 2025", "2,10,000.00", "1,15,000.00", "+ 95,000.00", "5,90,000.00", "5.13 Months"],
        ["Jul 2025", "3,10,000.00", "1,20,000.00", "+ 1,90,000.00", "7,80,000.00", "6.50 Months"],
        ["Aug 2025", "2,50,000.00", "1,20,000.00", "+ 1,30,000.00", "9,10,000.00", "7.58 Months"],
        ["Sep 2025", "2,30,000.00", "1,18,000.00", "+ 1,12,000.00", "10,22,000.00", "8.66 Months"],
        ["Oct 2025", "2,20,000.00", "1,18,000.00", "+ 1,02,000.00", "11,24,000.00", "9.52 Months"],
        ["Nov 2025", "2,10,000.00", "1,22,000.00", "+ 88,000.00", "12,12,000.00", "9.93 Months"],
        ["Dec 2025", "2,40,000.00", "1,22,000.00", "+ 1,18,000.00", "13,30,000.00", "10.90 Months"],
        ["Jan 2026", "2,60,000.00", "1,20,000.00", "+ 1,40,000.00", "14,70,000.00", "12.25 Months"],
        ["Feb 2026", "2,10,000.00", "1,20,000.00", "+ 90,000.00", "15,60,000.00", "13.00 Months"],
        ["Mar 2026", "2,40,000.00", "1,20,000.00", "+ 1,20,000.00", "14,80,000.00", "12.50 Months"]
    ]
    mfk_t = Table(months_flow_kav, colWidths=[70, 85, 85, 85, 95, 84])
    mfk_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f9ff")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(mfk_t)
    story.append(PageBreak())

    # Page 24: Part 2 - Stress Testing & Overdue Recovery Schedule
    story.append(Paragraph("7. Financial Runway & Capital Solvency (Part 2)", s["H1"]))
    story.append(Paragraph("Stress Scenario Modeling, Overdue Recovery & Capital Allocation Policy", s["H2"]))

    runway_kav = [
        ["Scenario Modeling", "Monthly Billings", "Monthly Burn", "Net Monthly Cash Flow", "Defensive Runway", "Risk Profile"],
        ["Base Case (Current ARR)", "INR 3,20,833.00", "INR 1,18,333.00", "+ INR 2,02,500.00", "Self-Sustaining", "Low Risk"],
        ["Stressed (30% Revenue Drop)", "INR 2,24,583.00", "INR 1,18,333.00", "+ INR 1,06,250.00", "Self-Sustaining", "Moderate"],
        ["Severe Contraction (50% Drop)", "INR 1,60,416.00", "INR 1,18,333.00", "+ INR 42,083.00", "Self-Sustaining", "Elevated"],
        ["Zero Revenue Black Swan", "INR 0.00", "INR 1,18,333.00", "- INR 1,18,333.00", "12.5 Months (INR 14.8L)", "Defensive Buffer"]
    ]
    rk_t2 = Table(runway_kav, colWidths=[125, 75, 75, 80, 85, 64])
    rk_t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(rk_t2)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Overdue Debt Recovery Action Matrix (Past 45-Day Overdue)", s["H2"]))
    debt_kav = [
        ["Debtor Entity", "Invoice Ref", "Due Date", "Days Overdue", "Outstanding (INR)", "Statutory Action Stage"],
        ["CyberShield Asia Pacific", "KAV-2026-108", "2026-02-05", "54 Days", "2,80,000.00", "Section 18 MSMED Arbitration Notice Served"],
        ["SecureStack Global Pte", "KAV-2026-109", "2026-02-18", "41 Days", "1,40,000.00", "Executive Escrow Escalation / Final Notice"],
        ["OmniGuard Telecom Labs", "KAV-2026-110", "2026-03-17", "14 Days", "4,20,000.00", "Standard Billing Cycle Follow-up"],
        ["Vanguard Health Systems", "KAV-2026-111", "2026-03-31", "0 Days", "2,80,000.00", "Current Invoice / Due in Normal Course"],
        ["Total Trade Receivables", "-", "-", "-", "11,20,000.00", "Gross Ledger Book Value"]
    ]
    dk_t = Table(debt_kav, colWidths=[120, 65, 55, 55, 80, 129])
    dk_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#831843")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fdf2f8")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fce7f3")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(dk_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Strategic Capital Allocation Directives (FY 2026-27)", s["H2"]))
    story.append(Paragraph(
        "1. Defensive Treasury Reserve: Retain INR 8,00,000 in immediate liquid bank deposits to guarantee 6+ months operational burn.\n"
        "2. R&D CAPEX Deployment: Allocate INR 4,00,000 toward next-generation post-quantum cryptographic HSM hardware accelerators.\n"
        "3. Legal Recovery Enforcement: Pursue arbitration under MSMED Act Section 18 for full recovery of INR 4,20,000 past-due debt plus statutory interest.", s["Body"]
    ))
    story.append(PageBreak())

    # PAGE 25: AUDITOR CERTIFICATION & CARO 2020
    story.append(Paragraph("8. Independent Statutory Auditor Certification", s["H1"]))
    story.append(Paragraph("Statutory Audit Opinion Under Section 143 of Companies Act 2013", s["H2"]))
    story.append(Paragraph(
        "To the Shareholders of Kavach Security Solutions Private Limited:\n"
        "We have audited the accompanying financial statements of Kavach Security Solutions Pvt Ltd, which comprise the Balance Sheet as at "
        "31 March 2026, the Statement of Profit and Loss, and the Cash Flow Statement for the fiscal year then ended. In our opinion, the accompanying "
        "statements give a true and fair view of the financial affairs of the company, confirming Total Invoiced Revenue of INR 38,50,000.00 and "
        "Total Collected Bank Deposits of INR 29,00,000.00.", s["Body"]
    ))
    story.append(Spacer(1, 6))

    # CARO Checklist
    story.append(Paragraph("CARO 2020 Statutory Verification Matrix", s["H2"]))
    caro_kav = [
        ["Clause", "Statutory CARO 2020 Parameter", "Auditor Verification Findings", "Audit Conclusion"],
        ["(i)", "Title deeds of immovable properties & Fixed Assets", "Hardware registers & HSM asset serials 100% verified", "Fully Verified"],
        ["(iii)", "Compliance with Sec 185 and 186 in respect of loans", "No loans, guarantees, or investments granted to related parties", "Compliant"],
        ["(vii)", "Undisputed statutory dues (GST, PF, ESIC, Tax)", "All monthly GST and withholding tax dues deposited on time", "100% Compliant"],
        ["(ix)", "Default in payment of interest or loan installments", "Company is completely debt-free with zero borrowings", "Compliant"],
        ["(xi)", "Reporting of material fraud or security falsification", "Zero fraud or cryptographic security anomalies detected", "Clean Record"],
        ["(xxi)", "Qualifications or adverse auditor remarks", "Standard Unqualified Audit Opinion issued; clean record", "Unqualified"]
    ]
    ck_t = Table(caro_kav, colWidths=[35, 185, 214, 70])
    ck_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0c4a6e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f9ff")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(ck_t)
    story.append(Spacer(1, 8))

    # Dual Signature Table
    sign_data_kav = [
        ["For Deloitte Haskins & Sells LLP", "For and on behalf of the Board of Directors"],
        ["Chartered Accountants (FRN: 117366W)", "Kavach Security Solutions Pvt Ltd"],
        ["\n___________________________\nAditi Sengupta, FCA\nPartner (Membership No: 058912)\nUDIN: 26058912AAAAAC8812\nPlace: Mumbai | Date: 18 April 2026",
         "\n___________________________\nAditya Kulkarni, CISSP\nChief Executive Officer (DIN: 08821901)\nPlace: Mumbai | Date: 18 April 2026"]
    ]
    s_tk = Table(sign_data_kav, colWidths=[250, 254])
    s_tk.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(s_tk)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Built Kavach Security PDF at {out_path}")


# =========================================================================
# 3. ZENITH DIGITAL MEDIA & DESIGN LLP (22 Pages)
# =========================================================================
def build_zenith_digital_pdf(out_path: str):
    """Builds a rich, completely populated 22-page financial review dossier for Zenith Digital Media & Design LLP."""
    doc = SimpleDocTemplate(
        out_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    s = get_audit_styles(primary_hex="#4c0519", secondary_hex="#be123c")
    story = []

    # PAGE 1: COVER
    story.append(Spacer(1, 40))
    story.append(Paragraph("ZENITH DIGITAL MEDIA & DESIGN LLP", s["CoverTitle"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Annual Financial Operations Review & Retainer Performance Dossier", s["CoverSub"]))
    story.append(Paragraph("Performance Marketing, Creative Production & Growth Engineering Retainer Records", s["Callout"]))
    story.append(Spacer(1, 25))

    meta_table = Table([
        ["Entity Name:", "Zenith Digital Media & Design LLP"],
        ["LLPIN (Limited Liability Partnership):", "AAB-4921 (Incorporated under the Limited Liability Partnership Act 2008)"],
        ["GSTIN (Delhi State Code 07):", "07AAGFZ9012C1Z8 (State Code 07 — National Capital Territory of Delhi)"],
        ["Permanent Account No (PAN):", "AAGFZ9012C (Ward 1(1), New Delhi Corporate Circle)"],
        ["Registered Corporate Office:", "Statesman House, Barakhamba Road, Connaught Place, New Delhi 110001"],
        ["Statutory Reporting Cycle:", "Fiscal Year 2025 – 2026 (01 April 2025 to 31 March 2026)"],
        ["Audited Total Invoiced Revenue:", "INR 16,20,000.00 (Sixteen Lakh Twenty Thousand Rupees)"],
        ["Direct Bank Collections Realized:", "INR 12,80,000.00 (79.0% Realization Efficiency)"],
        ["Operational Agency Disbursements:", "INR 6,10,000.00 (Ad Network Spend, Creator Payouts, Software Licenses)"],
        ["Net Cash Flow Realized:", "+ INR 6,70,000.00 (Six Lakh Seventy Thousand Rupees Net Surplus)"],
        ["Compliance Verification:", "100% Tax Compliant | Form 11 Annual Return & Form 8 Statement Reconciled"],
        ["Statutory Accounting Advisor:", "Singhal & Batra Associates (Chartered Accountants, Reg No: 014892N)"]
    ], colWidths=[170, 334])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff1f2")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#be123c")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 25))

    exec_notes = [
        ["Audit Scope:", "Comprehensive audit of 9 itemized agency invoices (ZDM-2026-301 to 309), media buying ledgers, influencer disbursals, and Delhi GST schedules."],
        ["Statutory Law:", "Prepared in accordance with Rule 24 of LLP Rules 2009 and Section 34 of the LLP Act 2008."],
        ["Classification:", "CONFIDENTIAL STATUTORY STATEMENT — FOR DESIGNATED PARTNERS & TAX AUTHORITIES"]
    ]
    nt = Table(exec_notes, colWidths=[120, 384])
    nt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffe4e6")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#f43f5e")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
    ]))
    story.append(nt)
    story.append(PageBreak())

    # PAGE 2: TABLE OF CONTENTS & GOVERNANCE
    story.append(Paragraph("1. Executive Summary & Table of Contents", s["H1"]))
    story.append(Paragraph("To the Designated Partners, Institutional Clients, and Reviewers:", s["H2"]))
    story.append(Paragraph(
        "Zenith Digital Media & Design LLP delivers growth marketing, creative strategy, and digital brand transformation for top consumer tech brands. "
        "During FY 2025-26, the firm billed INR 16,20,000 across 9 primary retainer campaigns. Direct collections reached INR 12,80,000 with "
        "disbursements managed tightly at INR 6,10,000, leaving a net liquid cash surplus of INR 6,70,000.", s["Body"]
    ))
    story.append(Spacer(1, 8))

    toc = [
        ["Section", "Contents & Operational Scope", "Statutory Rule", "Pages"],
        ["Section 1", "Executive Summary, Corporate Identity & Governance", "LLP Act 2008 Sec 34", "2"],
        ["Section 2", "Financial KPI Scorecard & Retainer Collections Metrics", "Ind AS / LLP Standards", "3"],
        ["Section 3", "Delhi GST & Multi-State Inter-State Tax Schedule", "CGST / IGST Act 2017", "4"],
        ["Section 4", "Itemized Agency Tax Invoices (ZDM-2026-301 to 309)", "Rule 46 Tax Invoices", "5 – 13"],
        ["Section 5", "Retainer Client Ledgers & Reconciliation Statements", "Double-Entry Bookkeeping", "14 – 16"],
        ["Section 6", "Media Buying, Creator Payouts & Agency Costs", "Schedule 14 Opex Audit", "17 – 19"],
        ["Section 7", "Working Capital, Debt Aging & Cash Flow Projections", "Working Capital / MSMED Act", "20 – 21"],
        ["Section 8", "Designated Partners Statement of Truth & Sign-Off", "LLP Form 8 Certification", "22"]
    ]
    t = Table(toc, colWidths=[70, 234, 140, 60])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#881337")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff1f2")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("LLP Partnership Governance & Operational Oversight", s["H2"]))
    gov_table = Table([
        ["Designated Partners:", "Kavita Singhal (50%), Rohan Batra (50%)", "Capital Contribution:", "INR 10,00,000.00 (Fully Paid)"],
        ["Statutory Form 11 Filed:", "Filed with MCA on 28 May 2025", "Statutory Form 8 Filed:", "Filed with MCA on 15 Oct 2025"],
        ["Average Retainer Value:", "INR 1,80,000.00 per Campaign", "Client Retention Rate:", "91.5% Annual Retention"],
        ["Statutory Current Account:", "Axis Bank Ltd (Barakhamba Rd, Delhi)", "Accounting Standard:", "Cash Basis / Mercantile Hybrid"]
    ], colWidths=[120, 132, 120, 132])
    gov_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff1f2")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(gov_table)
    story.append(PageBreak())

    # PAGE 3: KPI SCORECARD
    story.append(Paragraph("2. Financial KPI Scorecard", s["H1"]))
    story.append(Paragraph("Aggregated Retainer Billings & Performance Economics (FY 2025-26)", s["H2"]))

    kpi_z = [
        ["Total Invoiced Amount", "INR 16,20,000.00", "Total Collected Deposits", "INR 12,80,000.00"],
        ["Outstanding Receivables", "INR 3,40,000.00", "Total Past-Due Overdue", "INR 90,000.00"],
        ["Operational Disbursements", "INR 6,10,000.00", "Net Realized Cash Surplus", "+ INR 6,70,000.00"],
        ["Average Retainer Size", "INR 1,80,000.00", "Client Retention Rate", "91.5%"]
    ]
    zt = Table(kpi_z, colWidths=[125, 127, 125, 127])
    zt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#fff1f2")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#fff1f2")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(zt)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Campaign Retainer Performance & RoAS Multipliers", s["H2"]))
    cam_data = [
        ["Brand Account", "Campaign Focus", "Invoiced (INR)", "Ad Spend (INR)", "Attributed RoAS", "Payment Status"],
        ["Nykaa Fashion", "Festive Creative Direction & UGC", "2,20,000.00", "80,000.00", "4.8x RoAS", "Settled in Full"],
        ["Swiggy Instamart", "Hyperlocal Paid User Acquisition", "2,60,000.00", "1,00,000.00", "3.9x RoAS", "Settled in Full"],
        ["Urban Company", "Brand Identity & Design Guidelines", "1,80,000.00", "Included", "Organic Growth", "Settled in Full"],
        ["Cleartrip Travel", "Technical SEO & Growth Sprints", "1,90,000.00", "Included", "+ 62% Traffic", "Settled in Full"],
        ["Mamaearth", "Influencer & Tier-1 Creator Program", "2,80,000.00", "1,10,000.00", "5.2x RoAS", "Settled in Full"],
        ["Cult.fit", "App Store Conversion Optimization", "1,60,000.00", "Included", "+ 24% Installs", "Partial (INR 90K Overdue)"],
        ["Total Major Accounts", "-", "12,90,000.00", "2,90,000.00", "4.6x Average", "86% Realized"]
    ]
    ct = Table(cam_data, colWidths=[95, 135, 75, 65, 65, 69])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#9f1239")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff1f2")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ffe4e6")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(ct)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Core Liquidity & Agency Margin Indicators", s["H2"]))
    ratio_z = [
        ["Operating Metric", "Reported Value", "Benchmark", "Variance Analysis"],
        ["Gross Operating Margin", "62.35%", "> 40.00%", "High profitability driven by low capital intensity"],
        ["Cash Realization Efficiency", "79.01%", "> 75.00%", "Superior cash velocity across enterprise retail clients"],
        ["Monthly Operational Burn", "INR 50,833.00", "< INR 70,000", "Extremely lean agency overhead structure"],
        ["Cash Runway Coverage", "13.1 Months", "> 6.0 Months", "Net surplus INR 6.7L guarantees prolonged solvency"],
        ["Partner Return on Equity", "67.00%", "> 30.00%", "Substantial return generated on INR 10L base capital"]
    ]
    rz_t = Table(ratio_z, colWidths=[130, 80, 85, 209])
    rz_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4c0519")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff1f2")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(rz_t)
    story.append(PageBreak())

    # PAGE 4: GST RECONCILIATION
    story.append(Paragraph("3. Delhi GST & Inter-State Tax Reconciliation", s["H1"]))
    story.append(Paragraph("Tax Liability Assessment & Monthly GSTR Filing Schedule", s["H2"]))
    story.append(Paragraph(
        "Zenith Digital Media operates under Delhi GSTIN 07AAGFZ9012C1Z8 (State Code 07). "
        "Intra-state billings within Delhi attract 9% CGST + 9% SGST. Interstate billings to Maharashtra, Karnataka, and Haryana attract 18% IGST. "
        "All input tax credits from Meta Ads, Google Ads, and Adobe software subscriptions have been matched via GSTR-2B.", s["Body"]
    ))
    story.append(Spacer(1, 6))

    gst_z = [
        ["Tax Bracket", "Taxable Base (INR)", "Rate", "Gross Tax (INR)", "ITC Adjustment (INR)", "Net Cash Paid (INR)"],
        ["CGST (Delhi Intra-State)", "4,20,000.00", "9.0%", "37,800.00", "14,500.00", "23,300.00"],
        ["SGST (Delhi Intra-State)", "4,20,000.00", "9.0%", "37,800.00", "14,500.00", "23,300.00"],
        ["IGST (Interstate MH, KA, HR)", "9,53,050.85", "18.0%", "1,71,549.15", "65,200.00", "1,06,349.15"],
        ["Total Statutory GST Liability", "13,73,050.85", "-", "2,47,149.15", "94,200.00", "1,52,949.15"]
    ]
    gzt = Table(gst_z, colWidths=[140, 85, 40, 75, 80, 84])
    gzt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#881337")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff1f2")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fecdd3")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(gzt)
    story.append(Spacer(1, 8))

    story.append(Paragraph("State-wise Client Billing Breakdown", s["H2"]))
    pos_z = [
        ["Client Location", "State Code", "Retainer Count", "Taxable Value (INR)", "Tax Type", "Total Invoiced (INR)"],
        ["Delhi NCT (Intra-state)", "07", "3 Clients", "4,20,000.00", "CGST + SGST (18%)", "4,95,600.00"],
        ["Karnataka (Inter-state)", "29", "3 Clients", "5,17,000.00", "IGST (18%)", "6,10,060.00"],
        ["Maharashtra (Inter-state)", "27", "1 Client", "2,20,000.00", "IGST (18%)", "2,59,600.00"],
        ["Haryana (Inter-state)", "06", "2 Clients", "2,16,050.85", "IGST (18%)", "2,54,740.00"],
        ["National Aggregate Total", "-", "9 Accounts", "13,73,050.85", "-", "16,20,000.00"]
    ]
    pos_zt = Table(pos_z, colWidths=[120, 50, 75, 85, 90, 84])
    pos_zt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4c0519")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff1f2")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ffe4e6")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(pos_zt)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Statutory Filing Attestation: Monthly returns filed timely under Rule 61(5) of CGST Rules 2017. Input tax credit of INR 94,200 verified with nil disputed credit.", s["Callout"]))
    story.append(PageBreak())

    # PAGES 5 - 13: 9 INVOICES
    invs_z = [
        ("ZDM-2026-301", "Nykaa Fashion E-Commerce", "27AAACN5541L1Z9", "27 (MH)", "Festive Campaign Creative Direction & UGC Video Assets", 220000, "paid", "2025-05-10", "2025-05-24", "RTGS-HDFC-882190", "Lower Parel, Mumbai"),
        ("ZDM-2026-302", "Swiggy Instamart Media", "29AAACS1122D1ZQ", "29 (KA)", "Hyperlocal Performance Marketing & Ad Optimization", 260000, "paid", "2025-06-15", "2025-06-29", "NEFT-ICICI-449182", "Koramangala, Bengaluru"),
        ("ZDM-2026-303", "Urban Company Home Services", "07AAGFU9901M1ZA", "07 (DL)", "Brand Repositioning & Design System Guidelines", 180000, "paid", "2025-07-20", "2025-08-04", "IMPS-AXIS-991823", "Connaught Place, New Delhi"),
        ("ZDM-2026-304", "Cleartrip Travel Technologies", "29AAACC7788P1Z3", "29 (KA)", "Search Engine Optimization & Technical Content Strategy", 190000, "paid", "2025-08-25", "2025-09-10", "RTGS-KOTAK-119283", "Indiranagar, Bengaluru"),
        ("ZDM-2026-305", "Zomato Dining & Events", "07AAGFZ4455E1ZV", "07 (DL)", "Event Media Coverage, Aftermovies & Motion Graphics", 150000, "paid", "2025-10-12", "2025-10-26", "NEFT-HDFC-339182", "Golf Course Rd, Gurugram"),
        ("ZDM-2026-306", "Mamaearth Personal Care", "06AAACD3311K1Z9", "06 (HR)", "Influencer Marketing Campaign & Tier-1 Creator Management", 280000, "paid", "2025-11-18", "2025-12-02", "RTGS-SBI-772819", "Sector 44, Gurugram"),
        ("ZDM-2026-307", "Cult.fit Fitness & Wellness", "29AAACC8877B1ZN", "29 (KA)", "App Store Conversion Rate Optimization & Ad Creatives", 160000, "overdue", "2026-01-08", "Pending (Overdue > 45d)", "Partial Settlement Pending", "HSR Layout, Bengaluru"),
        ("ZDM-2026-308", "Boat Lifestyle Audio", "07AAGFB1199M1ZT", "07 (DL)", "Product Launch Video 3D CGI Animation Pipeline", 90000, "issued", "2026-02-10", "Due in 15d", "Pending (Net 30)", "Hauz Khas, New Delhi"),
        ("ZDM-2026-309", "Lenskart Solutions Ltd", "06AAACL5544Q1ZP", "06 (HR)", "Quarterly Brand Strategy & Retainer Direction", 90000, "issued", "2026-03-01", "Due in 25d", "Pending (Net 30)", "Manesar, Gurugram")
    ]

    for inv_num, client, gstin, state, desc, base_amt, status, idate, pdate, bank_ref, addr in invs_z:
        story.append(Paragraph(f"Tax Invoice: {inv_num}", s["H1"]))
        is_interstate = "07" not in state
        tax_amt = round(base_amt * 0.18, 2)
        total = round(base_amt + tax_amt, 2)
        irn = f"9c8b7a6d5e4f{inv_num.replace('-', '').lower()}11a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9"

        t_data = [
            ["Invoice ID:", inv_num, "Date of Issue:", idate],
            ["IRN (e-Invoice Hash):", irn[:42] + "...", "Ack No & Date:", f"072610{inv_num[-3:]} · {idate}"],
            ["Client Legal Name:", client, "Client GSTIN:", gstin],
            ["Billing Address:", addr, "Place of Supply:", f"State Code {state}"],
            ["Issuer GSTIN:", "07AAGFZ9012C1Z8 (Delhi)", "Current Status:", status.upper()],
            ["Payment Terms:", "Net 30 Days", "Bank Ref:", pdate]
        ]
        t1 = Table(t_data, colWidths=[95, 160, 95, 154])
        t1.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff1f2")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t1)
        story.append(Spacer(1, 8))

        items = [
            ["Sl", "Creative / Growth Deliverable Description", "SAC", "Rate (INR)", "Qty", "Total (INR)"],
            ["1", desc, "998311", f"{base_amt:,.2f}", "1.00", f"{base_amt:,.2f}"],
            ["2", "Creative Production Assets & Omnichannel Delivery", "998311", "Included", "1.00", "0.00"],
            ["3", "Performance Attribution & RoAS Analytics Report", "998311", "Included", "1.00", "0.00"],
            ["", "Subtotal (Taxable Value)", "", "", "", f"{base_amt:,.2f}"]
        ]
        if is_interstate:
            items.append(["", "Integrated GST (IGST @ 18.0%)", "", "", "", f"{tax_amt:,.2f}"])
        else:
            cgst = tax_amt / 2.0
            items.append(["", "Central GST (CGST @ 9.0%)", "", "", "", f"{cgst:,.2f}"])
            items.append(["", "State GST (SGST @ 9.0%)", "", "", "", f"{cgst:,.2f}"])
        items.append(["", "Total Invoice Payable", "", "", "", f"{total:,.2f}"])

        t2 = Table(items, colWidths=[20, 240, 50, 60, 30, 104])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#881337")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ffe4e6")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(t2)
        story.append(Spacer(1, 8))

        # Tax Breakdown Sub-Table
        if is_interstate:
            tax_sub = [
                ["SAC Code", "Taxable Value", "CGST Rate", "CGST Amt", "SGST Rate", "SGST Amt", "IGST Rate", "IGST Amt"],
                ["998311", f"{base_amt:,.2f}", "-", "0.00", "-", "0.00", "18.0%", f"{tax_amt:,.2f}"]
            ]
        else:
            cgst = tax_amt / 2.0
            tax_sub = [
                ["SAC Code", "Taxable Value", "CGST Rate", "CGST Amt", "SGST Rate", "SGST Amt", "IGST Rate", "IGST Amt"],
                ["998311", f"{base_amt:,.2f}", "9.0%", f"{cgst:,.2f}", "9.0%", f"{cgst:,.2f}", "-", "0.00"]
            ]
        ts_t = Table(tax_sub, colWidths=[54, 75, 55, 60, 55, 60, 65, 80])
        ts_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(ts_t)
        story.append(Spacer(1, 8))

        # Settlement Info
        pay_info = [
            ["Beneficiary Name:", "Zenith Digital Media & Design LLP", "Bank Name:", "Axis Bank Ltd"],
            ["Current Account No:", "91802008819231 (Current A/c)", "IFSC Code:", "UTIB0000007 (Barakhamba Rd)"],
            ["Payment Verification:", f"Status: {status.upper()} | Bank Ref: {bank_ref}", "TDS Section:", "Section 194J @ 2% / 10%"],
            ["Interest Clause:", "18% p.a. charged on overdue invoices after 30 days under MSMED Act 2006.", "Jurisdiction:", "New Delhi Courts Only"]
        ]
        p_t = Table(pay_info, colWidths=[100, 160, 90, 154])
        p_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff1f2")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(p_t)
        story.append(Spacer(1, 8))

        sig_data = [
            ["Declaration: We declare that this invoice shows the actual price of the media services described and is true and correct.",
             "For Zenith Digital Media & Design LLP\n\n\n___________________________\nDesignated Partner (Digital Signature)"]
        ]
        sig_t = Table(sig_data, colWidths=[310, 194])
        sig_t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(sig_t)
        story.append(PageBreak())

    # PAGES 14 - 16: CLIENT LEDGERS (3 Pages)
    z_ledgers = [
        ("Nykaa Fashion E-Commerce", "27AAACN5541L1Z9", "27 (MH)", "ZDM-2026-301", 220000, 220000, 0, "RTGS-HDFC-882190", "2025-05-10", "2025-05-24", "Settled in Full"),
        ("Swiggy Instamart Media", "29AAACS1122D1ZQ", "29 (KA)", "ZDM-2026-302", 260000, 260000, 0, "NEFT-ICICI-449182", "2025-06-15", "2025-06-29", "Settled in Full"),
        ("Cult.fit Fitness & Wellness", "29AAACC8877B1ZN", "29 (KA)", "ZDM-2026-307", 160000, 70000, 90000, "Partial RTGS Received", "2026-01-08", "Overdue > 45d", "Overdue Balance")
    ]
    for cname, cgstin, cstate, inv, bamt, camt, bal, ref, idate, pdate, status_text in z_ledgers:
        story.append(Paragraph(f"Retainer Ledger Account: {cname}", s["H1"]))
        story.append(Paragraph("Statutory Double-Entry Ledger Statement & Aging Schedule (FY 2025-26)", s["H2"]))

        c_meta = [
            ["Client Legal Name:", cname, "Account Code:", f"RET-{cgstin[2:7]}-2026"],
            ["Client GSTIN:", cgstin, "Place of Supply:", f"State Code {cstate}"],
            ["Retainer Terms:", "Monthly Retainer + Performance Bonus", "Payment Mode:", "Direct Bank RTGS/NEFT"],
            ["Reconciliation Status:", status_text.upper(), "Audit Status:", "Verified via Statutory Bank Reconciliation"]
        ]
        cm_t = Table(c_meta, colWidths=[100, 160, 95, 149])
        cm_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff1f2")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(cm_t)
        story.append(Spacer(1, 8))

        tds_amt = round(camt * 0.02, 2) if camt > 0 else 0.0
        net_bank = camt - tds_amt if camt > 0 else 0.0
        
        ldata = [
            ["Date", "Transaction Particulars & Voucher Ref", "Voucher Type", "Debit (INR)", "Credit (INR)", "Running Balance (INR)"],
            ["2025-04-01", "Opening Balance Brought Forward", "OB-001", "0.00", "0.00", "0.00"],
            [idate, f"Campaign Retainer Fee Invoiced ({inv})", "Sales Inv", f"{bamt:,.2f}", "0.00", f"{bamt:,.2f} Dr"]
        ]
        if camt > 0:
            ldata.append([pdate, f"TDS Deduction by Client u/s 194J (2%)", "Journal (TDS)", "0.00", f"{tds_amt:,.2f}", f"{(bamt - tds_amt):,.2f} Dr"])
            ldata.append([pdate, f"Direct Bank Deposit Realized ({ref})", "Bank Receipt", "0.00", f"{net_bank:,.2f}", f"{bal:,.2f} {'Dr' if bal > 0 else 'Cr'}"])
        ldata.append(["2026-03-31", "Closing Position as on Year-End", "Balance C/F", f"{bamt:,.2f}", f"{camt:,.2f}", f"{bal:,.2f} {'Dr (Overdue)' if bal > 0 else 'Settled'}"])

        lt = Table(ldata, colWidths=[65, 175, 65, 65, 65, 69])
        lt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4c0519")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff1f2")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ffe4e6")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(lt)
        story.append(Spacer(1, 8))

        # Aging Analysis
        story.append(Paragraph("Trade Receivables Aging Analysis", s["H2"]))
        if bal > 0:
            aging_data = [
                ["Current (0-30d)", "31-60 Days", "61-90 Days", "> 90 Days", "Total Outstanding", "Recovery Action Status"],
                ["0.00", f"{bal:,.2f}", "0.00", "0.00", f"{bal:,.2f}", "Follow-up Reminder Dispatched / Balance Due"]
            ]
        else:
            aging_data = [
                ["Current (0-30d)", "31-60 Days", "61-90 Days", "> 90 Days", "Total Outstanding", "Recovery Action Status"],
                ["0.00", "0.00", "0.00", "0.00", "0.00", "Retainer Account Fully Reconciled"]
            ]
        ag_t = Table(aging_data, colWidths=[75, 75, 70, 70, 85, 129])
        ag_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(ag_t)
        story.append(Spacer(1, 8))

        # Form 26AS TDS Verification
        story.append(Paragraph("Statutory Form 26AS TDS & Tax Credit Reconciliation", s["H2"]))
        tds_check = [
            ["Financial Year", "Section", "Gross Retainer Billed", "TDS Deducted (INR)", "Challan / BSR Code", "26AS Match Status"],
            ["2025-26", "194J", f"{bamt:,.2f}", f"{tds_amt:,.2f}", f"BSR-0071920 · CH-8812" if tds_amt > 0 else "N/A", "100% Matched" if tds_amt > 0 else "Pending Deposit"]
        ]
        tc_t = Table(tds_check, colWidths=[70, 60, 95, 90, 115, 74])
        tc_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#475569")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(tc_t)
        story.append(Spacer(1, 6))
        story.append(Paragraph("Audit Verification: External ledger balance confirmation letter dispatched and cross-referenced with bank scroll records.", s["Callout"]))
        story.append(PageBreak())

    # PAGES 17 - 19: AGENCY EXPENSES (3 Pages)
    z_exps = [
        ("Digital Ad Network Spend (Meta Ads & Google Display Network)", 240000, [
            ("Meta Platforms Ireland Ltd (Facebook & Instagram Performance Ads)", "PO-FB-2025-01", "META-99182", "2025-06-15", "Credit Card", 140000, 25200, 165200),
            ("Google Asia Pacific Pte Ltd (Search Ads, YouTube & Display)", "PO-GOOG-2025-04", "GOOG-44918", "2025-09-10", "Credit Card", 70000, 12600, 82600),
            ("LinkedIn Ireland Unlimited Company (B2B Sponsored Campaigns)", "PO-LI-2025-08", "LI-882190", "2025-12-05", "Credit Card", 30000, 5400, 35400),
        ]),
        ("Independent Creator Remuneration & Production Disbursements", 190000, [
            ("Apex Creator Collective (10 Tier-1 UGC Lifestyle Creators)", "PO-CR-2025-02", "CR-551920", "2025-07-22", "Bank Transfer", 100000, 18000, 118000),
            ("Motion Magic Studios LLP (3D CGI Product Visualizations)", "PO-MM-2025-06", "MM-229102", "2025-10-18", "Vendor Inv", 50000, 9000, 59000),
            ("SoundWave Audio Productions (Original Sonic Branding & Mixes)", "PO-SW-2025-09", "SW-772910", "2026-01-14", "Bank Transfer", 40000, 7200, 47200),
        ]),
        ("Creative Software Suite, Design Licenses & Studio Lease", 180000, [
            ("Adobe Systems Enterprise All Apps Creative Cloud (10 Seats)", "PO-ADBE-2025-01", "ADBE-33918", "2025-05-18", "Credit Card", 80000, 14400, 94400),
            ("Figma Inc Enterprise Design & Prototyping Organization Plan", "PO-FIG-2025-05", "FIG-118290", "2025-08-20", "Credit Card", 40000, 7200, 47200),
            ("Statesman House Connaught Place Creative Coworking Studio", "PO-SH-2025-10", "SH-992810", "2025-11-12", "Bank Transfer", 60000, 10800, 70800),
        ])
    ]

    for title, total_sub, rows in z_exps:
        story.append(Paragraph(f"Agency Operating Expenses: {title}", s["H1"]))
        story.append(Paragraph("Schedule 14 Statutory Voucher Disbursals & ITC Verification", s["H2"]))

        exp_table = [["Vendor Name & Purpose", "PO Number", "Invoice Ref", "Date", "Mode", "Base (INR)", "ITC 18%", "Gross (INR)"]]
        for vname, po, vref, vdate, mode, bamt, itc, gross in rows:
            exp_table.append([vname, po, vref, vdate, mode, f"{bamt:,.2f}", f"{itc:,.2f}", f"{gross:,.2f}"])
        exp_table.append(["Subtotal Budget Head Disbursed", "", "", "", "", f"{total_sub:,.2f}", f"{(total_sub*0.18):,.2f}", f"{(total_sub*1.18):,.2f}"])

        e_t = Table(exp_table, colWidths=[150, 60, 55, 45, 50, 48, 44, 52])
        e_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#881337")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 6.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff1f2")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fecdd3")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(e_t)
        story.append(Spacer(1, 8))

        # Monthly Budget vs Actual Variance Table
        story.append(Paragraph("Quarterly Budget Allocation vs Actual Utilization", s["H2"]))
        b_q = total_sub / 4.0
        b_data = [
            ["Quarter Period", "Approved Budget (INR)", "Actual Disbursal (INR)", "Variance (INR)", "Variance %", "Audit Status"],
            ["Q1 (Apr - Jun 2025)", f"{b_q:,.2f}", f"{(b_q * 0.94):,.2f}", f"+ {(b_q * 0.06):,.2f}", "+ 6.0% Favorable", "Within Budget"],
            ["Q2 (Jul - Sep 2025)", f"{b_q:,.2f}", f"{(b_q * 1.04):,.2f}", f"- {(b_q * 0.04):,.2f}", "- 4.0% Unfavorable", "Partners Approved"],
            ["Q3 (Oct - Dec 2025)", f"{b_q:,.2f}", f"{(b_q * 0.98):,.2f}", f"+ {(b_q * 0.02):,.2f}", "+ 2.0% Favorable", "Within Budget"],
            ["Q4 (Jan - Mar 2026)", f"{b_q:,.2f}", f"{(b_q * 1.04):,.2f}", f"- {(b_q * 0.04):,.2f}", "- 4.0% Unfavorable", "Campaign Expansion"],
            ["Consolidated Annual Total", f"{total_sub:,.2f}", f"{total_sub:,.2f}", "0.00", "0.0% On Target", "Reconciled"]
        ]
        b_t = Table(b_data, colWidths=[105, 85, 85, 75, 75, 79])
        b_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4c0519")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff1f2")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ffe4e6")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(b_t)
        story.append(Spacer(1, 8))

        # Statutory Withholding Tax
        story.append(Paragraph("Statutory Tax Deducted at Source (TDS Section 194C / 194J)", s["H2"]))
        tds_exp = [
            ["Tax Section", "Category Description", "Gross Base Disbursed", "Applicable Rate", "TDS Deducted", "Deposit Challan Ref"],
            ["Section 194C / 194J", "Ad Network Spend & Creator Retainers", f"{total_sub:,.2f}", "1.0% / 2.0%", f"{(total_sub * 0.02):,.2f}", "CH-DELHI-008192"],
        ]
        te_t = Table(tds_exp, colWidths=[75, 150, 95, 60, 60, 64])
        te_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#57534e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(te_t)
        story.append(Spacer(1, 6))
        story.append(Paragraph("Audit Attestation: Reconciled with vendor tax receipts. Eligible ITC of INR 94,200 verified with nil disputed credit.", s["Callout"]))
        story.append(PageBreak())

    # PAGES 20 - 21: WORKING CAPITAL & LIQUIDITY (2 Pages)
    # Page 20: Part 1 - Working Capital Balance Sheet & 12-Month Flow
    story.append(Paragraph("7. Working Capital & Liquidity Trajectory (Part 1)", s["H1"]))
    story.append(Paragraph("Working Capital Position & 12-Month Cash Flow Statement", s["H2"]))

    wc_z = [
        ["Balance Sheet Head", "Category Head", "Audited Position (INR)", "Liquidity Assessment"],
        ["Trade Receivables (Retainer Clients)", "Current Asset", "3,40,000.00", "High Realizability (< 30-45 Days)"],
        ["Cash & Bank Balances (Axis Bank)", "Liquid Current Asset", "6,70,000.00", "Liquid Operating Capital in Current A/c"],
        ["GST ITC Balance (Delhi & IGST)", "Statutory Asset", "94,200.00", "Available for Offset Against FY27 Dues"],
        ["Prepaid Software Subscriptions", "Current Asset", "45,000.00", "Adobe & Figma Unamortized Prepaid Licences"],
        ["Total Liquid & Current Assets (A)", "Gross Current Assets", "11,49,200.00", "Healthy Asset Coverage"],
        ["Trade Creditors & Ad Network Dues", "Current Liability", "1,20,000.00", "Within 30-Day Vendor Payment Terms"],
        ["Statutory Tax Payables (GST & TDS)", "Current Liability", "45,000.00", "Cleared on Subsequent Due Dates"],
        ["Total Current Liabilities (B)", "Gross Current Liabilities", "1,65,000.00", "Extremely Low Short-Term Liabilities"],
        ["Net Working Capital (A - B)", "Net Operating Capital", "+ 9,84,200.00", "Current Ratio = 6.96 : 1 (Robust Buffer)"]
    ]
    wcz_t = Table(wc_z, colWidths=[140, 110, 120, 134])
    wcz_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4c0519")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fff1f2")]),
        ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#fecdd3")),
        ("FONTNAME", (0, 5), (-1, 5), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dcfce7")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(wcz_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("12-Month Operating Cash Inflow vs Outflow Ledger (FY 2025-26)", s["H2"]))
    months_flow_z = [
        ["Month", "Inflows (INR)", "Outflows (INR)", "Net Flow (INR)", "Closing Cash Buffer", "Burn Coverage"],
        ["Apr 2025", "1,00,000.00", "45,000.00", "+ 55,000.00", "1,55,000.00", "3.44 Months"],
        ["May 2025", "1,20,000.00", "48,000.00", "+ 72,000.00", "2,27,000.00", "4.73 Months"],
        ["Jun 2025", "1,10,000.00", "48,000.00", "+ 62,000.00", "2,89,000.00", "6.02 Months"],
        ["Jul 2025", "1,40,000.00", "52,000.00", "+ 88,000.00", "3,77,000.00", "7.25 Months"],
        ["Aug 2025", "1,10,000.00", "52,000.00", "+ 58,000.00", "4,35,000.00", "8.37 Months"],
        ["Sep 2025", "1,00,000.00", "50,000.00", "+ 50,000.00", "4,85,000.00", "9.70 Months"],
        ["Oct 2025", "1,20,000.00", "52,000.00", "+ 68,000.00", "5,53,000.00", "10.63 Months"],
        ["Nov 2025", "1,10,000.00", "52,000.00", "+ 58,000.00", "6,11,000.00", "11.75 Months"],
        ["Dec 2025", "90,000.00", "51,000.00", "+ 39,000.00", "6,50,000.00", "12.75 Months"],
        ["Jan 2026", "1,10,000.00", "55,000.00", "+ 55,000.00", "7,05,000.00", "12.82 Months"],
        ["Feb 2026", "80,000.00", "52,000.00", "+ 28,000.00", "7,33,000.00", "14.10 Months"],
        ["Mar 2026", "90,000.00", "53,000.00", "+ 37,000.00", "6,70,000.00", "13.14 Months"]
    ]
    mfz_t = Table(months_flow_z, colWidths=[70, 85, 85, 85, 95, 84])
    mfz_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff1f2")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(mfz_t)
    story.append(PageBreak())

    # Page 21: Part 2 - Stress Testing & Overdue Receivables Schedule
    story.append(Paragraph("7. Working Capital & Liquidity Trajectory (Part 2)", s["H1"]))
    story.append(Paragraph("Burn Sensitivity Modeling, Overdue Recovery & Retainer Churn Policy", s["H2"]))

    runway_z = [
        ["Scenario Modeling", "Monthly Billings", "Monthly Burn", "Net Monthly Flow", "Defensive Runway", "Risk Rating"],
        ["Base Case (Current Performance)", "INR 1,35,000.00", "INR 50,833.00", "+ INR 84,167.00", "Self-Sustaining", "Low Risk"],
        ["Stressed (30% Retainer Drop)", "INR 94,500.00", "INR 50,833.00", "+ INR 43,667.00", "Self-Sustaining", "Moderate"],
        ["Severe Contraction (50% Drop)", "INR 67,500.00", "INR 50,833.00", "+ INR 16,667.00", "Self-Sustaining", "Elevated"],
        ["Zero Revenue Black Swan", "INR 0.00", "INR 50,833.00", "- INR 50,833.00", "13.1 Months (INR 6.7L)", "Defensive Buffer"]
    ]
    rz_t2 = Table(runway_z, colWidths=[125, 75, 75, 80, 85, 64])
    rz_t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(rz_t2)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Trade Receivables Aging & Follow-up Matrix", s["H2"]))
    debt_z = [
        ["Client Entity", "Invoice Ref", "Due Date", "Days Overdue", "Outstanding (INR)", "Action Status"],
        ["Cult.fit Fitness & Wellness", "ZDM-2026-307", "2026-02-08", "51 Days", "90,000.00", "Formal Demand Notice Issued under MSMED"],
        ["Boat Lifestyle Audio", "ZDM-2026-308", "2026-03-12", "19 Days", "90,000.00", "Under Routine Net 30 Term / Due for Clearing"],
        ["Lenskart Solutions Ltd", "ZDM-2026-309", "2026-03-31", "0 Days", "90,000.00", "Fresh Invoice / Payment Due in April"],
        ["Miscellaneous Retainers", "ZDM-2026-GEN", "2026-03-15", "16 Days", "70,000.00", "Routine Corporate Follow-up"],
        ["Total Pending Receivables", "-", "-", "-", "3,40,000.00", "Active Billing Pipeline"]
    ]
    dz_t = Table(debt_z, colWidths=[120, 65, 55, 55, 80, 129])
    dz_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#831843")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fdf2f8")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fce7f3")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(dz_t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Partner Capital Allocation & Distribution Directives", s["H2"]))
    story.append(Paragraph(
        "1. Liquid Capital Reserve: Maintain INR 4,00,000 in immediate liquid reserves to safeguard 8+ months agency overhead.\n"
        "2. Creator Pool Expansion: Allocate INR 1,50,000 to onboard specialized AI generative video production talent in Q1 FY27.\n"
        "3. MSMED Act Enforcement: Enforce Section 16 interest penalty claims for overdue balances exceeding 45 days against institutional accounts.", s["Body"]
    ))
    story.append(PageBreak())

    # PAGE 22: DESIGNATED PARTNERS CERTIFICATION
    story.append(Paragraph("8. Designated Partners Certification & Statement of Truth", s["H1"]))
    story.append(Paragraph("Statement of Account & Solvency Under Section 34(2) of LLP Act 2008", s["H2"]))
    story.append(Paragraph(
        "We, the undersigned Designated Partners of Zenith Digital Media & Design LLP, hereby certify and confirm that the financial statements "
        "and accounts set forth in this dossier present a true and fair view of the state of affairs of the LLP as of 31 March 2026, and of the results of its "
        "operations for the year ended on that date. We confirm Total Invoiced Revenue of INR 16,20,000.00 and Total Collected Bank Deposits of "
        "INR 12,80,000.00, yielding a Net Realized Cash Flow surplus of INR 6,70,000.00.", s["Body"]
    ))
    story.append(Spacer(1, 6))

    # LLP Statutory Compliance Checklist
    story.append(Paragraph("LLP Statutory Compliance Checklist (FY 2025-26)", s["H2"]))
    llp_comp = [
        ["Statutory Head", "Statutory Provision", "Compliance Finding & Declaration", "Status"],
        ["Form 8 Statement of Account", "Rule 24 LLP Rules 2009", "Statement of Account and Solvency prepared and verified", "100% Compliant"],
        ["Form 11 Annual Return", "Rule 25 LLP Rules 2009", "Annual Return filed within 60 days of fiscal year close", "Filed On-Time"],
        ["Partner Capital Accounts", "LLP Agreement Schedule", "Profit sharing split strictly 50:50 between partners", "Reconciled"],
        ["GST Returns (Delhi State)", "Section 39 CGST Act", "All monthly GSTR-1 and GSTR-3B filed with nil arrears", "Compliant"],
        ["TDS Deductions & Returns", "Section 200 Income Tax Act", "Quarterly 26Q TDS returns filed and Form 16A certificates collected", "Compliant"],
        ["Debts & Liabilities Solvency", "Section 34(2) LLP Act", "Partners confirm LLP is capable of paying debts as they fall due", "Solvent"]
    ]
    lc_t = Table(llp_comp, colWidths=[100, 110, 224, 70])
    lc_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#881337")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff1f2")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(lc_t)
    story.append(Spacer(1, 8))

    # Dual Signature Table
    sign_data_z = [
        ["For Zenith Digital Media & Design LLP", "For Zenith Digital Media & Design LLP"],
        ["\n___________________________\nKavita Singhal\nDesignated Partner (DPIN: 09182311)\nPlace: New Delhi | Date: 12 April 2026",
         "\n___________________________\nRohan Batra\nDesignated Partner (DPIN: 09182312)\nPlace: New Delhi | Date: 12 April 2026"]
    ]
    s_tz = Table(sign_data_z, colWidths=[250, 254])
    s_tz.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(s_tz)

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
