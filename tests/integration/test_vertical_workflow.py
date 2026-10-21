"""
test_vertical_workflow.py - End-to-End Vertical Flow Verification for FinPilot AI.

Workflow:
1. Create client.
2. Draft invoice with deterministic GST calculations.
3. Validate line item calculations, taxes, and grand totals.
4. Issue invoice with approval confirmation & sequential numbering.
5. Generate official PDF and verify file existence.
6. Query and retrieve the invoice and client state through FinPilot AI Assistant.
7. Record payment, allocate funds, and verify legal state transitions (draft -> issued -> partially_paid -> paid).
"""

import os
import uuid
from decimal import Decimal
from datetime import date
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from langchain_core.messages import HumanMessage

from api.models import Base
from services.client_service import create_client, get_client_ledger
from services.invoice_service import create_invoice_draft, issue_invoice, get_invoice, list_invoices
from services.payment_service import record_payment, allocate_payment
from agents.finpilot_assistant import FinPilotAssistant


@pytest.fixture(scope="function")
async def db_session():
    """Provides an isolated test database session."""
    test_db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    engine = create_async_engine(test_db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_vertical_financial_workflow_end_to_end(db_session: AsyncSession):
    business_id = uuid.uuid4()

    # Step 1: Create Client
    client = await create_client(
        session=db_session,
        business_id=business_id,
        name="Rajesh Sharma",
        company_name="Acme Consulting India",
        email="rajesh@acmeconsulting.in",
        phone="+91 98200 54321",
        billing_address="102 Corporate Park, BKC, Mumbai",
        state_code="27",
        gstin="27AAPFU0939F1ZV",
        payment_terms_days=15,
        actor="user:recruiter_demo",
    )
    assert client.id is not None
    assert client.company_name == "Acme Consulting India"
    assert client.state_code == "27"

    # Step 2: Draft Invoice with 18% GST (Intra-state: 27 -> 27)
    line_items = [
        {
            "description": "Full-Stack AI Financial Operations Platform Architecture",
            "quantity": 1,
            "unit_price": 50000.00,
            "discount_pct": 0,
            "tax_rate_pct": 18,
        }
    ]
    draft = await create_invoice_draft(
        session=db_session,
        business_id=business_id,
        client_id=client.id,
        line_items=line_items,
        due_days=15,
        notes="Thank you for your business. Please make payment via NEFT/IMPS.",
        actor="user:recruiter_demo",
    )

    # Step 3: Validate Deterministic Totals
    assert draft.status == "draft"
    assert draft.subtotal == Decimal("50000.00")
    assert draft.tax_type == "intra_state"
    assert draft.cgst_amount == Decimal("4500.00")
    assert draft.sgst_amount == Decimal("4500.00")
    assert draft.igst_amount == Decimal("0.00")
    assert draft.total_tax == Decimal("9000.00")
    assert draft.grand_total == Decimal("59000.00")
    assert draft.amount_paid == Decimal("0.00")
    assert draft.amount_due == Decimal("59000.00")
    assert draft.pdf_path is not None
    assert os.path.exists(draft.pdf_path)

    # Step 4: Issue Invoice (Confirm issuance & assign sequential number)
    issued_inv = await issue_invoice(
        session=db_session,
        invoice_id=draft.id,
        business_id=business_id,
        idempotency_key="idem_inv_001",
        actor="user:recruiter_demo",
    )
    assert issued_inv.status == "issued"
    assert issued_inv.invoice_number.startswith(f"INV-{date.today().year}-")
    assert issued_inv.issued_at is not None

    # Step 5: Test Idempotent Retry of Issuance
    retry_inv = await issue_invoice(
        session=db_session,
        invoice_id=draft.id,
        business_id=business_id,
        idempotency_key="idem_inv_001",
        actor="user:recruiter_demo",
    )
    assert retry_inv.id == issued_inv.id
    assert retry_inv.invoice_number == issued_inv.invoice_number

    # Step 6: Query through FinPilot AI Assistant
    assistant = FinPilotAssistant()
    
    # Query A: "Create an invoice for Acme Consulting for ₹50,000 plus 18% GST, due in 15 days"
    result_ai = await assistant.chat(
        message="Create an invoice for Acme Consulting for ₹50,000 plus 18% GST, due in 15 days",
        business_id=business_id,
        session=db_session,
    )
    assert result_ai["intent"] == "create_invoice_draft"
    assert result_ai["card_type"] == "invoice_draft"
    assert result_ai["card_data"]["grand_total"] == "59000.00"
    assert "₹59000.00" in result_ai["final_response"] or "₹59,000.00" in result_ai["final_response"] or "59000.00" in result_ai["final_response"]

    # Query B: "What is the financial summary?"
    result_sum = await assistant.chat(
        message="What is my financial summary and outstanding amount?",
        business_id=business_id,
        session=db_session,
    )
    assert result_sum["intent"] == "financial_summary"
    assert result_sum["tool_result"]["total_invoiced"] == str(issued_inv.grand_total + Decimal("59000.00")) # previous + new draft

    # Step 7: Record Payment and Allocate
    # Record payment of ₹30,000 against issued invoice
    payment, allocated = await record_payment(
        session=db_session,
        business_id=business_id,
        client_id=client.id,
        amount=Decimal("30000.00"),
        payment_method="bank_transfer",
        reference_number="UTR9876543210",
        allocate_to_invoice_id=issued_inv.id,
        actor="user:recruiter_demo",
    )
    assert allocated == Decimal("30000.00")
    assert payment.allocated_amount == Decimal("30000.00")
    assert payment.unallocated_amount == Decimal("0.00")

    # Refresh invoice state
    reloaded_inv = await get_invoice(db_session, issued_inv.id, business_id)
    assert reloaded_inv.status == "partially_paid"
    assert reloaded_inv.amount_paid == Decimal("30000.00")
    assert reloaded_inv.amount_due == Decimal("29000.00")

    # Step 8: Pay Remaining Balance
    payment2, allocated2 = await record_payment(
        session=db_session,
        business_id=business_id,
        client_id=client.id,
        amount=Decimal("29000.00"),
        payment_method="upi",
        reference_number="UPI-PAY-002",
        allocate_to_invoice_id=issued_inv.id,
        actor="user:recruiter_demo",
    )
    assert allocated2 == Decimal("29000.00")

    # Verify final paid state
    reloaded_inv2 = await get_invoice(db_session, issued_inv.id, business_id)
    assert reloaded_inv2.status == "paid"
    assert reloaded_inv2.amount_paid == Decimal("59000.00")
    assert reloaded_inv2.amount_due == Decimal("0.00")

    # Step 9: Verify Client Ledger
    ledger = await get_client_ledger(db_session, client.id, business_id)
    assert ledger["total_invoiced"] == Decimal("118000.00") # 2 invoices of 59,000
    assert ledger["total_paid"] == Decimal("59000.00")
    assert ledger["total_due"] == Decimal("59000.00") # from the 2nd draft
