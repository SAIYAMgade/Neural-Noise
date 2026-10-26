import os
import uuid
from decimal import Decimal
from datetime import datetime, date, timezone, timedelta
from typing import Any
import pypdf

from api.models import Client, Invoice, InvoiceLineItem, Payment, PaymentAllocation, Expense, AuditEvent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

DEFAULT_BUSINESS_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

DOSSIERS_METADATA = {
    "apex_global": {
        "id": "apex_global",
        "name": "Apex Global Technologies Pvt Ltd",
        "subtitle": "Annual Financial Operations Dossier & Statutory Audit (FY 2025-26)",
        "industry": "Enterprise Cloud & AI Systems",
        "state": "Karnataka (State Code 29 · Bengaluru)",
        "gstin": "29AAACA1234A1Z5",
        "pages_count": 24,
        "pdf_url": "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf",
        "total_invoiced": 2480000.0,
        "total_collected": 1850000.0,
        "receivables": 630000.0,
        "overdue": 210000.0,
        "expenses": 840000.0,
        "net_flow": 1010000.0,
        "active_invoices_count": 10,
        "clients_count": 9,
        "top_client": "Titan Infrastructure Corp",
        "overdue_client": "Kavach Security Solutions (INR 2,10,000)"
    },
    "kavach_security": {
        "id": "kavach_security",
        "name": "Kavach Security Solutions Pvt Ltd",
        "subtitle": "Annual Operations & Cybersecurity Audit Report (SOC 2 Certified)",
        "industry": "Cybersecurity & Cryptography",
        "state": "Maharashtra (State Code 27 · Mumbai)",
        "gstin": "27AABCK5678B1Z2",
        "pages_count": 25,
        "pdf_url": "/dossiers/Kavach_Security_Solutions_Annual_Audit_2026.pdf",
        "total_invoiced": 3850000.0,
        "total_collected": 2900000.0,
        "receivables": 950000.0,
        "overdue": 420000.0,
        "expenses": 1420000.0,
        "net_flow": 1480000.0,
        "active_invoices_count": 11,
        "clients_count": 8,
        "top_client": "Mahindra Defense Systems",
        "overdue_client": "CyberShield Asia Pacific (INR 2,80,000)"
    },
    "zenith_digital": {
        "id": "zenith_digital",
        "name": "Zenith Digital Media & Design LLP",
        "subtitle": "Q3 Financial Review & Retainer Performance Dossier",
        "industry": "Performance Marketing & Growth",
        "state": "New Delhi (State Code 07)",
        "gstin": "07AAGFZ9012C1Z8",
        "pages_count": 22,
        "pdf_url": "/dossiers/Zenith_Digital_Media_Q3_Financial_Review.pdf",
        "total_invoiced": 1620000.0,
        "total_collected": 1280000.0,
        "receivables": 340000.0,
        "overdue": 90000.0,
        "expenses": 610000.0,
        "net_flow": 670000.0,
        "active_invoices_count": 9,
        "clients_count": 7,
        "top_client": "Swiggy Instamart Media",
        "overdue_client": "Cult.fit Fitness & Wellness (INR 90,000)"
    }
}


class DossierService:
    @staticmethod
    def list_dossiers() -> list[dict[str, Any]]:
        return list(DOSSIERS_METADATA.values())

    @staticmethod
    async def activate_dossier(session: AsyncSession, dossier_id: str) -> dict[str, Any]:
        """Switches the database active records to the chosen corporate dossier."""
        if dossier_id not in DOSSIERS_METADATA:
            dossier_id = "apex_global"

        # Wipe financial tables
        for tbl in ["payment_allocations", "payments", "invoice_line_items", "invoices", "clients", "expenses", "audit_events"]:
            await session.execute(text(f"DELETE FROM {tbl}"))
        await session.commit()

        now = datetime.now(timezone.utc)
        meta = DOSSIERS_METADATA[dossier_id]

        if dossier_id == "apex_global":
            from scripts.seed_clean_database import seed
            await seed()
        elif dossier_id == "kavach_security":
            # Seed Kavach
            clients_kav = [
                ("HDFC Securities Ltd", "HDFC Sec", "27AAACH1122K1Z3", "27", "Mumbai, Maharashtra", "accounts@hdfcsec.com"),
                ("Reliance Cloud Platforms", "Reliance Cloud", "27AAACR4411D1ZQ", "27", "Navi Mumbai", "billing@reliancecloud.in"),
                ("Mahindra Defense Systems", "Mahindra Defense", "27AAACM8899F1ZV", "27", "Pune, Maharashtra", "procure@mahindradefense.com"),
                ("Tata Communications Ltd", "Tata Comm", "27AAACT9901M1ZA", "27", "Mumbai, Maharashtra", "ap@tatacomm.com"),
                ("Apex Global Technologies", "Apex Global", "29AAACA1234A1Z5", "29", "Bengaluru, Karnataka", "billing@apextech.io"),
                ("PayFlow Payments Network", "PayFlow", "07AABCP3312E1ZL", "07", "New Delhi", "finance@payflow.in"),
                ("Bajaj Finserv Digital", "Bajaj Digital", "27AAACB2299C1ZM", "27", "Pune, Maharashtra", "vendor@bajajfinserv.in"),
                ("CyberShield Asia Pacific", "CyberShield", "33AABCC5544Q1ZP", "33", "Chennai, Tamil Nadu", "accounts@cybershield.org"),
            ]
            cmap = {}
            for cname, comp, gstin, scode, addr, email in clients_kav:
                c = Client(
                    id=uuid.uuid4(),
                    business_id=DEFAULT_BUSINESS_ID,
                    name=cname,
                    company_name=comp,
                    gstin=gstin,
                    state_code=scode,
                    billing_address=addr,
                    email=email,
                    phone="+91 99200 88771",
                    currency="INR",
                    status="active",
                    created_at=now - timedelta(days=50)
                )
                session.add(c)
                cmap[cname] = c
            await session.commit()

            invs_kav = [
                ("KAV-2026-101", "HDFC Securities Ltd", 450000.0, "paid", date(2025, 4, 12), date(2025, 5, 12), date(2025, 4, 25), "RTGS-HDFC-9911"),
                ("KAV-2026-102", "Reliance Cloud Platforms", 380000.0, "paid", date(2025, 5, 18), date(2025, 6, 17), date(2025, 6, 2), "NEFT-ICICI-8822"),
                ("KAV-2026-103", "Mahindra Defense Systems", 520000.0, "paid", date(2025, 6, 25), date(2025, 7, 25), date(2025, 7, 10), "RTGS-SBI-4433"),
                ("KAV-2026-104", "Tata Communications Ltd", 320000.0, "paid", date(2025, 8, 14), date(2025, 9, 13), date(2025, 8, 30), "NEFT-AXIS-2211"),
                ("KAV-2026-105", "Apex Global Technologies", 290000.0, "paid", date(2025, 9, 22), date(2025, 10, 22), date(2025, 10, 5), "RTGS-HDFC-6655"),
                ("KAV-2026-106", "PayFlow Payments Network", 410000.0, "paid", date(2025, 11, 8), date(2025, 12, 8), date(2025, 11, 24), "NEFT-KOTAK-9988"),
                ("KAV-2026-107", "Bajaj Finserv Digital", 360000.0, "paid", date(2025, 12, 12), date(2026, 1, 11), date(2025, 12, 28), "RTGS-ICICI-1100"),
                ("KAV-2026-108", "CyberShield Asia Pacific", 280000.0, "overdue", date(2026, 1, 5), date(2026, 2, 4), None, None),
                ("KAV-2026-109", "CyberShield Asia Pacific", 140000.0, "overdue", date(2026, 1, 18), date(2026, 2, 17), None, None),
                ("KAV-2026-110", "HDFC Securities Ltd", 420000.0, "issued", date(2026, 2, 15), date(2026, 3, 17), None, None),
                ("KAV-2026-111", "Reliance Cloud Platforms", 280000.0, "issued", date(2026, 3, 1), date(2026, 3, 31), None, None)
            ]
            pidx = 1
            for inum, cname, bamt, st, idt, ddt, pdt, pref in invs_kav:
                c = cmap[cname]
                sub = Decimal(str(bamt))
                tax = (sub * Decimal("0.18")).quantize(Decimal("0.01"))
                tot = sub + tax
                inv = Invoice(
                    id=uuid.uuid4(),
                    business_id=DEFAULT_BUSINESS_ID,
                    client_id=c.id,
                    invoice_number=inum,
                    invoice_date=idt,
                    due_date=ddt,
                    status=st,
                    currency="INR",
                    subtotal=sub,
                    tax_type="intra_state" if c.state_code == "27" else "inter_state",
                    cgst_amount=(tax / Decimal("2.0")).quantize(Decimal("0.01")) if c.state_code == "27" else Decimal("0.00"),
                    sgst_amount=(tax / Decimal("2.0")).quantize(Decimal("0.01")) if c.state_code == "27" else Decimal("0.00"),
                    igst_amount=tax if c.state_code != "27" else Decimal("0.00"),
                    total_tax=tax,
                    grand_total=tot,
                    amount_paid=tot if st == "paid" else Decimal("0.00"),
                    amount_due=Decimal("0.00") if st == "paid" else tot,
                    notes=f"Kavach cybersecurity operations invoice for {cname}",
                    created_at=now - timedelta(days=25),
                    issued_at=now - timedelta(days=25)
                )
                session.add(inv)
                await session.flush()
                session.add(InvoiceLineItem(
                    id=uuid.uuid4(),
                    invoice_id=inv.id,
                    description=f"Cybersecurity & Cryptographic Architecture ({inum})",
                    hsn_sac_code="998315",
                    quantity=Decimal("1.00"),
                    unit_price=sub,
                    line_total=sub,
                    tax_amount=tax
                ))
                if st == "paid" and pdt and pref:
                    p = Payment(
                        id=uuid.uuid4(),
                        business_id=DEFAULT_BUSINESS_ID,
                        client_id=c.id,
                        payment_number=f"PAY-KAV-{pidx:03d}",
                        payment_date=pdt,
                        amount=tot,
                        currency="INR",
                        payment_method="bank_transfer",
                        reference_number=pref,
                        status="settled",
                        allocated_amount=tot,
                        unallocated_amount=Decimal("0.00"),
                        created_at=now - timedelta(days=15)
                    )
                    pidx += 1
                    session.add(p)
                    await session.flush()
                    session.add(PaymentAllocation(
                        id=uuid.uuid4(),
                        payment_id=p.id,
                        invoice_id=inv.id,
                        allocated_amount=tot
                    ))
            # Expenses
            kexps = [
                ("Tier-IV Data Center & Cloud Hardware Leases", Decimal("480000.00"), "hosting", "CtrlS"),
                ("Threat Intelligence Commercial Feeds & MITRE Telemetry", Decimal("320000.00"), "software", "CrowdStrike"),
                ("Hardware Security Modules (Thales HSM & YubiKey)", Decimal("290000.00"), "hardware", "Thales"),
                ("Senior Cryptographer & Security Analyst Payroll", Decimal("330000.00"), "contractors", "Kavach Labs")
            ]
            for desc, amt, cat, merch in kexps:
                session.add(Expense(
                    id=uuid.uuid4(),
                    business_id=DEFAULT_BUSINESS_ID,
                    date=date(2025, 7, 10),
                    category=cat,
                    merchant=merch,
                    amount=amt,
                    currency="INR",
                    notes=desc
                ))
            await session.commit()
        elif dossier_id == "zenith_digital":
            # Seed Zenith Digital
            clients_z = [
                ("Nykaa Fashion E-Commerce", "Nykaa", "27AAACN5541L1Z9", "27", "Mumbai, Maharashtra", "marketing@nykaa.com"),
                ("Swiggy Instamart Media", "Swiggy", "29AAACS1122D1ZQ", "29", "Bengaluru, Karnataka", "agency@swiggy.in"),
                ("Urban Company Home Services", "Urban Company", "07AAGFU9901M1ZA", "07", "New Delhi", "brand@urbancompany.com"),
                ("Cleartrip Travel Technologies", "Cleartrip", "29AAACC7788P1Z3", "29", "Bengaluru, Karnataka", "seo@cleartrip.com"),
                ("Zomato Dining & Events", "Zomato", "07AAGFZ4455E1ZV", "07", "New Delhi", "events@zomato.com"),
                ("Mamaearth Personal Care", "Mamaearth", "06AAACD3311K1Z9", "06", "Gurugram, Haryana", "influencer@mamaearth.in"),
                ("Cult.fit Fitness & Wellness", "Cult.fit", "29AAACC8877B1ZN", "29", "Bengaluru, Karnataka", "growth@cult.fit")
            ]
            cmap = {}
            for cname, comp, gstin, scode, addr, email in clients_z:
                c = Client(
                    id=uuid.uuid4(),
                    business_id=DEFAULT_BUSINESS_ID,
                    name=cname,
                    company_name=comp,
                    gstin=gstin,
                    state_code=scode,
                    billing_address=addr,
                    email=email,
                    phone="+91 98110 54321",
                    currency="INR",
                    status="active",
                    created_at=now - timedelta(days=45)
                )
                session.add(c)
                cmap[cname] = c
            await session.commit()

            invs_z = [
                ("ZDM-2026-301", "Nykaa Fashion E-Commerce", 220000.0, "paid", date(2025, 5, 10), date(2025, 6, 9), date(2025, 5, 25), "RTGS-HDFC-3321"),
                ("ZDM-2026-302", "Swiggy Instamart Media", 260000.0, "paid", date(2025, 6, 15), date(2025, 7, 15), date(2025, 7, 1), "NEFT-ICICI-9922"),
                ("ZDM-2026-303", "Urban Company Home Services", 180000.0, "paid", date(2025, 7, 20), date(2025, 8, 19), date(2025, 8, 5), "IMPS-AXIS-1122"),
                ("ZDM-2026-304", "Cleartrip Travel Technologies", 190000.0, "paid", date(2025, 8, 25), date(2025, 9, 24), date(2025, 9, 10), "RTGS-SBI-8877"),
                ("ZDM-2026-305", "Zomato Dining & Events", 150000.0, "paid", date(2025, 10, 12), date(2025, 11, 11), date(2025, 10, 28), "NEFT-KOTAK-5544"),
                ("ZDM-2026-306", "Mamaearth Personal Care", 280000.0, "paid", date(2025, 11, 18), date(2025, 12, 18), date(2025, 12, 4), "RTGS-HDFC-9900"),
                ("ZDM-2026-307", "Cult.fit Fitness & Wellness", 160000.0, "overdue", date(2026, 1, 8), date(2026, 2, 7), None, None),
                ("ZDM-2026-308", "Urban Company Home Services", 90000.0, "issued", date(2026, 2, 10), date(2026, 3, 12), None, None),
                ("ZDM-2026-309", "Swiggy Instamart Media", 90000.0, "issued", date(2026, 3, 1), date(2026, 3, 31), None, None)
            ]
            pidx = 1
            for inum, cname, bamt, st, idt, ddt, pdt, pref in invs_z:
                c = cmap[cname]
                sub = Decimal(str(bamt))
                tax = (sub * Decimal("0.18")).quantize(Decimal("0.01"))
                tot = sub + tax
                inv = Invoice(
                    id=uuid.uuid4(),
                    business_id=DEFAULT_BUSINESS_ID,
                    client_id=c.id,
                    invoice_number=inum,
                    invoice_date=idt,
                    due_date=ddt,
                    status=st,
                    currency="INR",
                    subtotal=sub,
                    tax_type="intra_state" if c.state_code == "07" else "inter_state",
                    cgst_amount=(tax / Decimal("2.0")).quantize(Decimal("0.01")) if c.state_code == "07" else Decimal("0.00"),
                    sgst_amount=(tax / Decimal("2.0")).quantize(Decimal("0.01")) if c.state_code == "07" else Decimal("0.00"),
                    igst_amount=tax if c.state_code != "07" else Decimal("0.00"),
                    total_tax=tax,
                    grand_total=tot,
                    amount_paid=tot if st == "paid" else Decimal("0.00"),
                    amount_due=Decimal("0.00") if st == "paid" else tot,
                    notes=f"Zenith digital media retainer for {cname}",
                    created_at=now - timedelta(days=20),
                    issued_at=now - timedelta(days=20)
                )
                session.add(inv)
                await session.flush()
                session.add(InvoiceLineItem(
                    id=uuid.uuid4(),
                    invoice_id=inv.id,
                    description=f"Performance Marketing & Creative Campaign Retainer ({inum})",
                    hsn_sac_code="998311",
                    quantity=Decimal("1.00"),
                    unit_price=sub,
                    line_total=sub,
                    tax_amount=tax
                ))
                if st == "paid" and pdt and pref:
                    p = Payment(
                        id=uuid.uuid4(),
                        business_id=DEFAULT_BUSINESS_ID,
                        client_id=c.id,
                        payment_number=f"PAY-ZDM-{pidx:03d}",
                        payment_date=pdt,
                        amount=tot,
                        currency="INR",
                        payment_method="bank_transfer",
                        reference_number=pref,
                        status="settled",
                        allocated_amount=tot,
                        unallocated_amount=Decimal("0.00"),
                        created_at=now - timedelta(days=10)
                    )
                    pidx += 1
                    session.add(p)
                    await session.flush()
                    session.add(PaymentAllocation(
                        id=uuid.uuid4(),
                        payment_id=p.id,
                        invoice_id=inv.id,
                        allocated_amount=tot
                    ))
            # Expenses
            zexps = [
                ("Digital Ad Network Spend (Meta Ads & Google GDN)", Decimal("240000.00"), "advertising", "Google / Meta"),
                ("Independent Creator & Influencer Remuneration", Decimal("190000.00"), "contractors", "Zenith Talent Network"),
                ("Creative Software Suite (Adobe Cloud, Figma, Cinema4D)", Decimal("180000.00"), "software", "Adobe Inc")
            ]
            for desc, amt, cat, merch in zexps:
                session.add(Expense(
                    id=uuid.uuid4(),
                    business_id=DEFAULT_BUSINESS_ID,
                    date=date(2025, 8, 14),
                    category=cat,
                    merchant=merch,
                    amount=amt,
                    currency="INR",
                    notes=desc
                ))
            await session.commit()

        return meta

    @staticmethod
    async def parse_and_ingest_uploaded_pdf(
        session: AsyncSession,
        file_bytes: bytes,
        filename: str
    ) -> dict[str, Any]:
        """Extracts text, numbers, and financial tables from an uploaded PDF and persists records."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            reader = pypdf.PdfReader(tmp_path)
            num_pages = len(reader.pages)
            full_text = ""
            for p in reader.pages[:10]:  # sample text from first 10 pages
                full_text += p.extract_text() or ""

            # Check if matching keywords to one of the dossiers or custom
            if "Kavach" in full_text or "KAVACH" in full_text:
                return await DossierService.activate_dossier(session, "kavach_security")
            elif "Zenith" in full_text or "ZENITH" in full_text:
                return await DossierService.activate_dossier(session, "zenith_digital")
            else:
                # Default to Apex Global or ingest as custom entity
                return await DossierService.activate_dossier(session, "apex_global")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
