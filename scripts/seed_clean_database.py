import asyncio
import os
import sys
import uuid
from decimal import Decimal
from datetime import datetime, date, timezone, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from api.database import get_db_manager
from api.models import (
    WebsiteProject, PageSnapshot, AudienceSegment, ExperienceVariant,
    Experiment, ExperimentAssignment, ExperimentEvent, AgentExecutionTrace,
    EvaluationRun, Client, Invoice, InvoiceLineItem, Payment, PaymentAllocation,
    Expense, AuditEvent
)
from sqlalchemy import text

DEFAULT_BUSINESS_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

async def seed():
    mgr = get_db_manager()
    async with mgr.session() as s:
        print("Cleaning duplicate and stale records...")
        for tbl in [
            "payment_allocations", "payments", "invoice_line_items", "invoices", "clients",
            "expenses", "audit_events", "experiment_events", "experiment_assignments",
            "experiments", "experience_variants", "audience_segments", "page_snapshots",
            "agent_execution_traces", "website_projects"
        ]:
            await s.execute(text(f"DELETE FROM {tbl}"))
        await s.commit()
        print("Cleaned all tables.")

        now = datetime.now(timezone.utc)

        # 1. Seed 6 Distinct Website Projects
        projects_data = [
            ("SaaS Metrics Hero Optimization", "saasmetrics.io", "SaaS / B2B Software", "Data-driven, precise, enterprise-ready"),
            ("Fintech Checkout Funnel", "payflow.in", "Fintech & Payments", "Trustworthy, compliant, seamless"),
            ("CloudScale Enterprise AI", "cloudscale.ai", "Enterprise Cloud & AI", "Authoritative, scalable, high-performance"),
            ("DevTools Growth Engine", "codepulse.dev", "Developer Tooling", "Concise, technical, developer-centric"),
            ("HealthTech Portal", "carepulse.org", "Digital Health & Telemedicine", "Empathetic, clinical, secure"),
            ("EduLearn Global Academy", "edulearn.com", "EdTech & Upskilling", "Inspirational, clear, outcomes-driven"),
        ]

        proj_objs = []
        for name, domain, industry, voice in projects_data:
            p = WebsiteProject(
                id=uuid.uuid4(),
                name=name,
                url=f"https://{domain}",
                business_objective=f"Maximize conversion rates for {name} with targeted messaging",
                target_audience=voice,
                brand_guidelines={
                    "tone": voice,
                    "prohibited_terms": ["100% guaranteed roi", "risk-free guarantee", "guaranteed 10x"],
                    "required_phrases": [],
                    "headline_max_chars": 85,
                    "cta_max_chars": 35,
                },
                created_at=now - timedelta(days=5)
            )
            s.add(p)
            proj_objs.append(p)
        await s.commit()
        print(f"Seeded {len(proj_objs)} distinct projects.")

        # Seed page snapshots & variants for primary project
        primary_proj = proj_objs[0]  # SaaS Metrics
        snap = PageSnapshot(
            id=uuid.uuid4(),
            project_id=primary_proj.id,
            url=f"{primary_proj.url}/pricing",
            content_hash="hash_saasmetrics_2026",
            title="SaaSMetrics — Revenue Analytics & Growth Engine",
            meta_description="Real-time SaaS recurring revenue metrics, churn prevention, and subscription billing analytics.",
            headings=[{"tag": "h1", "text": "Turn Subscription Data Into Predictable Growth"}],
            value_prop="Automate MRR, churn, and LTV telemetry with zero latency across your billing stack.",
            benefits=["Real-time Stripe & Paddle sync", "AI-driven churn early warnings", "Automated executive board decks"],
            calls_to_action=[{"text": "Start Free 14-Day Trial"}],
            trust_badges=["SOC 2 Type II Certified", "ISO 27001", "GDPR Compliant"],
            raw_text="Complete revenue analytics platform for modern recurring-revenue businesses.",
            created_at=now - timedelta(days=4)
        )
        s.add(snap)
        await s.commit()

        # Seed Audience
        aud = AudienceSegment(
            id=uuid.uuid4(),
            project_id=primary_proj.id,
            name="Series A-B SaaS Founders",
            source="LinkedIn Ads / Product Hunt",
            persona_description="Growth-focused founders seeking revenue clarity and churn reduction without engineering overhead.",
            intent_hypotheses=["Prioritizes automated churn prevention and rapid Stripe setup over manual spreadsheet reporting."],
            created_at=now - timedelta(days=4)
        )
        s.add(aud)
        await s.commit()

        # Seed 3 Distinct Variants
        variants_data = [
            ("Variant A (Outcome Led)", "Turn Subscription Data Into Predictable Cash Flow", "Zero-setup revenue telemetry for high-velocity software teams.", "Start Free 14-Day Trial"),
            ("Variant B (Security Led)", "Enterprise Revenue Intelligence with SOC 2 Precision", "Real-time billing analytics engineered for security-conscious software leaders.", "Schedule Architecture Review"),
            ("Variant C (ROI Led)", "Stop Churn Before It Hits Your P&L", "Predictive revenue signals and automated cohort retention analysis.", "Explore Interactive Demo")
        ]
        var_objs = []
        for vname, h1, sub, cta in variants_data:
            v = ExperienceVariant(
                id=uuid.uuid4(),
                project_id=primary_proj.id,
                page_snapshot_id=snap.id,
                audience_segment_id=aud.id,
                variant_name=vname,
                headline=h1,
                subheading=sub,
                main_copy=sub,
                benefits=snap.benefits,
                cta_text=cta,
                status="approved",
                approved_by="Lead Growth Engineer",
                approved_at=now - timedelta(days=3),
                validation_results={
                    "is_valid": True,
                    "brand_score": 0.98,
                    "issues": [],
                    "prohibited_detected": []
                },
                created_at=now - timedelta(days=4),
                updated_at=now - timedelta(days=3)
            )
            s.add(v)
            var_objs.append(v)
        await s.commit()
        print(f"Seeded {len(var_objs)} variants.")

        # 2. Seed 6 Distinct Live Experiments
        experiments_data = [
            ("Pricing Page: Annual vs Monthly Pitch", primary_proj.id, snap.id, {str(var_objs[0].id): 0.5, str(var_objs[1].id): 0.5}, "conversion_rate", 840, 72),
            ("Hero Section: 'Book Live Demo' vs 'Start Free Trial'", primary_proj.id, snap.id, {str(var_objs[0].id): 0.5, str(var_objs[2].id): 0.5}, "cta_click", 620, 58),
            ("Checkout Social Proof: Client Logos vs Case Study Badges", proj_objs[1].id, snap.id, {str(var_objs[1].id): 0.5, str(var_objs[2].id): 0.5}, "cta_click", 510, 44),
            ("Enterprise Security Tier: SOC2 Emphasis vs Speed", proj_objs[2].id, snap.id, {str(var_objs[0].id): 0.5, str(var_objs[1].id): 0.5}, "conversion_rate", 730, 68),
            ("Mobile Navigation: Bottom Sticky CTA vs Floating Pill", proj_objs[3].id, snap.id, {str(var_objs[1].id): 0.5, str(var_objs[2].id): 0.5}, "cta_click", 430, 39),
            ("Feature Grid: Benefit-Led vs Capability-Led Icons", proj_objs[4].id, snap.id, {str(var_objs[0].id): 0.5, str(var_objs[2].id): 0.5}, "conversion_rate", 380, 32),
        ]

        for exp_name, pid, sid, alloc, metric, vis_cnt, conv_cnt in experiments_data:
            exp = Experiment(
                id=uuid.uuid4(),
                project_id=pid,
                page_snapshot_id=sid,
                name=exp_name,
                status="running",
                primary_metric=metric,
                traffic_allocation=alloc,
                start_time=now - timedelta(days=2),
                created_at=now - timedelta(days=2)
            )
            s.add(exp)
            await s.flush()

            var_ids = list(alloc.keys())
            for i in range(vis_cnt):
                vid = uuid.UUID(var_ids[i % len(var_ids)])
                vis_id = f"vis_{exp.id.hex[:6]}_{i:04d}"
                s.add(ExperimentAssignment(
                    id=uuid.uuid4(),
                    experiment_id=exp.id,
                    visitor_id=vis_id,
                    variant_id=vid,
                    assigned_at=now - timedelta(hours=i % 48)
                ))
                s.add(ExperimentEvent(
                    id=uuid.uuid4(),
                    experiment_id=exp.id,
                    visitor_id=vis_id,
                    variant_id=vid,
                    event_type="exposure",
                    properties={"viewport": "desktop" if i % 2 == 0 else "mobile"},
                    created_at=now - timedelta(hours=i % 48)
                ))
                if i < conv_cnt:
                    s.add(ExperimentEvent(
                        id=uuid.uuid4(),
                        experiment_id=exp.id,
                        visitor_id=vis_id,
                        variant_id=vid,
                        event_type="cta_click" if metric == "cta_click" else "conversion",
                        properties={"amount": 49.0},
                        created_at=now - timedelta(hours=(i % 48) - 1)
                    ))
        await s.commit()
        print("Seeded 6 distinct experiments with traffic events.")

        # 3. Seed 6 Distinct LangGraph Execution Traces
        traces_data = [
            ("Hero CTA Optimization Graph", 5, 1420, 1240),
            ("Pricing Funnel Personalization Pipeline", 6, 1890, 1850),
            ("B2B Audience Persona Synthesis", 4, 980, 920),
            ("Security Claims Brand Guardrail Pass", 5, 1150, 1120),
            ("Checkout Friction Reduction Workflow", 6, 1730, 1640),
            ("Mobile Viewport Responsive Alignment", 4, 890, 880),
        ]
        for tname, step_cnt, dur, tok in traces_data:
            steps = [
                {"node": "validate_request", "latency_ms": dur * 0.1, "output_summary": "Validated project schema & parameters"},
                {"node": "ingest_page_context", "latency_ms": dur * 0.2, "output_summary": "Parsed DOM elements (H1, CTA, Badges)"},
                {"node": "analyze_audience_intent", "latency_ms": dur * 0.25, "output_summary": "Extracted persona intent vectors"},
                {"node": "generate_variants", "latency_ms": dur * 0.3, "output_summary": "Synthesized 2 candidate variants"},
                {"node": "validate_guardrails", "latency_ms": dur * 0.15, "output_summary": "Verified brand safety & character bounds"},
            ]
            s.add(AgentExecutionTrace(
                id=uuid.uuid4(),
                workflow_type=tname,
                status="completed",
                input_data={"project": primary_proj.name, "target_url": primary_proj.url},
                output_data={"variants_generated": 2, "brand_score": 0.98},
                steps=steps,
                total_latency_ms=dur,
                created_at=now - timedelta(minutes=int(dur * 0.1))
            ))
        await s.commit()
        print("Seeded 6 distinct LangGraph traces.")

        # 4. Seed Distinct Clients, Invoices, Payments, Expenses (Matching Apex Global Dossier)
        clients_data = [
            ("Infosense Technologies Pvt Ltd", "Infosense Tech", "29AABCI5541L1Z0", "29", "Bengaluru, Karnataka", "billing@infosense.io"),
            ("Titan Infrastructure Corp", "Titan Infra", "27AAACT9901M1ZA", "27", "Mumbai, Maharashtra", "finance@titaninfra.com"),
            ("Wipro Digital Engineering Labs", "Wipro Digital", "29AAACW1122D1ZQ", "29", "Bengaluru, Karnataka", "vendor@wiproengineering.com"),
            ("Zenith Media & Entertainment", "Zenith Media", "07AAGFZ9012C1Z8", "07", "New Delhi", "accounts@zenithmedia.in"),
            ("Nexus Health Informatics Ltd", "Nexus Health", "33AABCN7788P1Z3", "33", "Chennai, Tamil Nadu", "payables@nexushealth.org"),
            ("Starlight Retail Solutions", "Starlight Retail", "36AABCS4455E1ZV", "36", "Hyderabad, Telangana", "finance@starlightretail.in"),
            ("Aura Cloud Analytics Pvt Ltd", "Aura Cloud", "27AABCA3311K1Z9", "27", "Pune, Maharashtra", "ap@auracloud.com"),
            ("Kavach Security Solutions", "Kavach Security", "27AABCK5678B1Z2", "27", "Mumbai, Maharashtra", "finance@kavachsecurity.in"),
            ("HyperScale SaaS Systems", "HyperScale SaaS", "29AAACH8877B1ZN", "29", "Bengaluru, Karnataka", "billing@hyperscalesaas.com")
        ]

        client_map = {}
        for cname, comp, gstin, scode, addr, email in clients_data:
            c = Client(
                id=uuid.uuid4(),
                business_id=DEFAULT_BUSINESS_ID,
                name=cname,
                company_name=comp,
                gstin=gstin,
                state_code=scode,
                billing_address=addr,
                email=email,
                phone="+91 98450 12345",
                currency="INR",
                status="active",
                created_at=now - timedelta(days=60)
            )
            s.add(c)
            client_map[cname] = c
        await s.commit()
        print(f"Seeded {len(client_map)} distinct corporate clients.")

        # Invoices corresponding to Apex Global Dossier
        invoices_data = [
            ("INV-2026-001", "Infosense Technologies Pvt Ltd", 250000.0, "paid", date(2025, 5, 15), date(2025, 6, 14), date(2025, 5, 28), "RTGS-ICICI-001928"),
            ("INV-2026-002", "Titan Infrastructure Corp", 340000.0, "paid", date(2025, 6, 20), date(2025, 7, 20), date(2025, 7, 2), "NEFT-HDFC-991823"),
            ("INV-2026-003", "Wipro Digital Engineering Labs", 180000.0, "paid", date(2025, 7, 10), date(2025, 8, 9), date(2025, 7, 22), "RTGS-SBI-554411"),
            ("INV-2026-004", "Zenith Media & Entertainment", 220000.0, "paid", date(2025, 8, 18), date(2025, 9, 17), date(2025, 9, 1), "IMPS-AXIS-882190"),
            ("INV-2026-005", "Nexus Health Informatics Ltd", 310000.0, "paid", date(2025, 9, 25), date(2025, 10, 25), date(2025, 10, 12), "NEFT-KOTAK-332190"),
            ("INV-2026-006", "Starlight Retail Solutions", 270000.0, "paid", date(2025, 11, 4), date(2025, 12, 4), date(2025, 11, 19), "RTGS-HDFC-771122"),
            ("INV-2026-007", "Aura Cloud Analytics Pvt Ltd", 280000.0, "paid", date(2025, 12, 15), date(2026, 1, 14), date(2026, 1, 5), "NEFT-ICICI-664411"),
            ("INV-2026-008", "Kavach Security Solutions", 210000.0, "overdue", date(2026, 1, 10), date(2026, 2, 9), None, None),
            ("INV-2026-009", "HyperScale SaaS Systems", 240000.0, "issued", date(2026, 2, 14), date(2026, 3, 16), None, None),
            ("INV-2026-010", "Infosense Technologies Pvt Ltd", 180000.0, "issued", date(2026, 3, 2), date(2026, 4, 1), None, None)
        ]

        pay_idx = 1
        for inv_num, cname, base_amt, status, idate, ddate, pdate, pref in invoices_data:
            c = client_map[cname]
            is_intra = c.state_code == "27"
            subtotal = Decimal(str(base_amt))
            
            if is_intra:
                cgst = (subtotal * Decimal("0.09")).quantize(Decimal("0.01"))
                sgst = (subtotal * Decimal("0.09")).quantize(Decimal("0.01"))
                igst = Decimal("0.00")
                tax_type = "intra_state"
            else:
                cgst = Decimal("0.00")
                sgst = Decimal("0.00")
                igst = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
                tax_type = "inter_state"
                
            total_tax = cgst + sgst + igst
            grand_total = subtotal + total_tax
            amt_paid = grand_total if status == "paid" else Decimal("0.00")
            amt_due = Decimal("0.00") if status == "paid" else grand_total

            inv = Invoice(
                id=uuid.uuid4(),
                business_id=DEFAULT_BUSINESS_ID,
                client_id=c.id,
                invoice_number=inv_num,
                invoice_date=idate,
                due_date=ddate,
                status=status,
                currency="INR",
                subtotal=subtotal,
                discount_total=Decimal("0.00"),
                tax_type=tax_type,
                cgst_amount=cgst,
                sgst_amount=sgst,
                igst_amount=igst,
                total_tax=total_tax,
                grand_total=grand_total,
                amount_paid=amt_paid,
                amount_due=amt_due,
                notes=f"Tax invoice for professional cloud architecture & engineering services delivered to {cname}.",
                created_at=now - timedelta(days=30),
                issued_at=now - timedelta(days=30)
            )
            s.add(inv)
            await s.flush()

            # Add Item
            s.add(InvoiceLineItem(
                id=uuid.uuid4(),
                invoice_id=inv.id,
                description=f"Enterprise Architecture & Implementation - Deliverable Phase ({inv_num})",
                hsn_sac_code="998314",
                quantity=Decimal("1.00"),
                unit_price=subtotal,
                discount_pct=Decimal("0.00"),
                tax_rate_pct=Decimal("18.00"),
                line_total=subtotal,
                tax_amount=total_tax
            ))

            # If paid, record payment
            if status == "paid" and pdate and pref:
                pay = Payment(
                    id=uuid.uuid4(),
                    business_id=DEFAULT_BUSINESS_ID,
                    client_id=c.id,
                    payment_number=f"PAY-2026-{pay_idx:03d}",
                    payment_date=pdate,
                    amount=grand_total,
                    currency="INR",
                    payment_method="bank_transfer",
                    reference_number=pref,
                    status="settled",
                    allocated_amount=grand_total,
                    unallocated_amount=Decimal("0.00"),
                    notes=f"Full settlement received via bank transfer against {inv_num}",
                    created_at=now - timedelta(days=20)
                )
                pay_idx += 1
                s.add(pay)
                await s.flush()

                s.add(PaymentAllocation(
                    id=uuid.uuid4(),
                    payment_id=pay.id,
                    invoice_id=inv.id,
                    allocated_amount=grand_total,
                    allocated_at=now - timedelta(days=20)
                ))
        await s.commit()
        print("Seeded 10 distinct invoices and cleared payments.")

        # Seed Operational Expenses
        expenses_data = [
            ("AWS EMEA Cloud Infrastructure (EC2, S3, EKS)", Decimal("240000.00"), "hosting", date(2025, 5, 20), "Direct Debit"),
            ("Embassy TechVillage Managed Office Lease", Decimal("220000.00"), "facilities", date(2025, 6, 1), "Bank Transfer"),
            ("Datadog APM & Cloudflare Enterprise WAF", Decimal("110000.00"), "software", date(2025, 7, 15), "Corporate Card"),
            ("DevOps & SRE Specialist Contractors (Q2)", Decimal("110000.00"), "contractors", date(2025, 8, 10), "Bank Transfer"),
            ("KPMG Statutory Legal & Tax Audit Retainer", Decimal("80000.00"), "legal", date(2025, 10, 5), "Vendor Invoice"),
            ("HDFC ERGO Group Health Cover & Welfare", Decimal("80000.00"), "insurance", date(2025, 12, 1), "Annual Premium"),
        ]
        for vname, amt, cat, edate, pmode in expenses_data:
            s.add(Expense(
                id=uuid.uuid4(),
                business_id=DEFAULT_BUSINESS_ID,
                date=edate,
                category=cat,
                merchant=vname.split()[0],
                amount=amt,
                currency="INR",
                tax_amount=Decimal("0.00"),
                payment_method=pmode,
                notes=f"Statutory operating expenditure: {vname}. Reconciled with GSTR-2B ITC input tax claims.",
                created_at=now - timedelta(days=40)
            ))
        await s.commit()
        print("Seeded distinct operational expenses.")

        # Seed Audit Events
        audit_events = [
            ("invoice.created", "Invoice INV-2026-001 drafted for Infosense Technologies"),
            ("invoice.issued", "Invoice INV-2026-001 issued with 18% GST (Net 30)"),
            ("payment.recorded", "Payment of INR 2,95,000 received via RTGS-ICICI-001928"),
            ("payment.allocated", "Payment allocated to INV-2026-001, balance cleared to 0.00"),
            ("invoice.issued", "Invoice INV-2026-008 issued to Kavach Security Solutions"),
            ("invoice.overdue", "Invoice INV-2026-008 marked overdue (> 45 days)"),
        ]
        for action, desc in audit_events:
            s.add(AuditEvent(
                id=uuid.uuid4(),
                business_id=DEFAULT_BUSINESS_ID,
                action=action,
                actor="System Auditor",
                entity_type="invoice",
                details={"description": desc},
                created_at=now - timedelta(days=10)
            ))
        await s.commit()
        print("Seeded audit events.")

if __name__ == "__main__":
    asyncio.run(seed())
    print("Database seeding completed with 100% distinct, realistic records!")
