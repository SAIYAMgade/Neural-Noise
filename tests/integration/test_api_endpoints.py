"""
test_api_endpoints.py - Integration tests for FinPilot AI FastAPI endpoints.
"""

import os
import uuid
from decimal import Decimal
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from api.models import Base
from api.main import create_app
from api.database import get_db_manager, DatabaseManager


@pytest.fixture(scope="function")
async def client():
    """Provides an ASGI test client with initialized database."""
    test_db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    engine = create_async_engine(test_db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app = create_app()
    app.state.db_manager = DatabaseManager(engine=engine)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()


@pytest.mark.asyncio
async def test_client_and_invoice_api_lifecycle(client: AsyncClient):
    # 1. Create Client
    client_payload = {
        "name": "Ananya Roy",
        "company_name": "Zenith Media Mumbai",
        "email": "ananya@zenithmedia.in",
        "phone": "+91 98111 22334",
        "billing_address": "401 Lotus Grandeur, Andheri West, Mumbai",
        "state_code": "27",
        "gstin": "27AAPFU0939F1ZV",
        "currency": "INR",
        "payment_terms_days": 15,
        "notes": "Premium media agency account",
    }
    res_client = await client.post("/api/v1/clients", json=client_payload)
    assert res_client.status_code == 201
    c_data = res_client.json()
    client_id = c_data["id"]
    assert c_data["company_name"] == "Zenith Media Mumbai"

    # 2. Preview Invoice Calculation (Intra-state: 27 to 27)
    preview_payload = {
        "client_id": client_id,
        "line_items": [
            {
                "description": "Quarterly Social Media Campaign Strategy",
                "quantity": 1,
                "unit_price": 75000.00,
                "discount_pct": 0,
                "tax_rate_pct": 18,
            }
        ],
        "is_export": False,
    }
    res_prev = await client.post("/api/v1/invoices/preview", json=preview_payload)
    assert res_prev.status_code == 200
    p_data = res_prev.json()
    assert Decimal(str(p_data["subtotal"])) == Decimal("75000.00")
    assert Decimal(str(p_data["cgst_amount"])) == Decimal("6750.00")
    assert Decimal(str(p_data["sgst_amount"])) == Decimal("6750.00")
    assert Decimal(str(p_data["total_tax"])) == Decimal("13500.00")
    assert Decimal(str(p_data["grand_total"])) == Decimal("88500.00")

    # 3. Create Draft Invoice
    draft_payload = {
        "client_id": client_id,
        "line_items": preview_payload["line_items"],
        "due_days": 15,
        "notes": "Payment via NEFT/RTGS to HDFC Bank",
    }
    res_draft = await client.post("/api/v1/invoices/draft", json=draft_payload)
    assert res_draft.status_code == 201
    d_data = res_draft.json()
    invoice_id = d_data["id"]
    assert d_data["status"] == "draft"
    assert Decimal(str(d_data["grand_total"])) == Decimal("88500.00")

    # 4. Issue Invoice
    idem_key = f"api_test_{uuid.uuid4().hex[:8]}"
    res_issue = await client.post(f"/api/v1/invoices/{invoice_id}/issue", json={"idempotency_key": idem_key})
    assert res_issue.status_code == 200
    i_data = res_issue.json()
    assert i_data["status"] == "issued"
    assert "INV-" in i_data["invoice_number"]

    # 5. Download Generated PDF
    res_pdf = await client.get(f"/api/v1/invoices/{invoice_id}/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 1000

    # 6. Record Payment
    pay_payload = {
        "client_id": client_id,
        "amount": 50000.00,
        "payment_method": "bank_transfer",
        "reference_number": "UTR1234567890",
        "notes": "Partial milestone payment 1",
        "allocate_to_invoice_id": invoice_id,
    }
    res_pay = await client.post("/api/v1/payments", json=pay_payload)
    assert res_pay.status_code == 201
    pay_data = res_pay.json()
    assert Decimal(str(pay_data["allocated_amount"])) == Decimal("50000.00")

    # 7. Check Invoice Remaining Due
    res_inv = await client.get(f"/api/v1/invoices/{invoice_id}")
    assert res_inv.status_code == 200
    reloaded_inv = res_inv.json()
    assert reloaded_inv["status"] == "partially_paid"
    assert Decimal(str(reloaded_inv["amount_paid"])) == Decimal("50000.00")
    assert Decimal(str(reloaded_inv["amount_due"])) == Decimal("38500.00")

    # 8. Check Overview Metrics
    res_ov = await client.get("/api/v1/overview")
    assert res_ov.status_code == 200
    ov_data = res_ov.json()
    assert Decimal(ov_data["total_invoiced"]) >= Decimal("88500.00")
    assert Decimal(ov_data["total_collected"]) >= Decimal("50000.00")
    assert len(ov_data["recent_audit_events"]) >= 3

    # 9. Conversational Assistant Interaction
    chat_payload = {
        "message": "What is the financial summary and outstanding amount?",
    }
    res_chat = await client.post("/api/v1/assistant/chat", json=chat_payload)
    assert res_chat.status_code == 200
    c_chat = res_chat.json()
    assert c_chat["intent"] == "financial_summary"
    assert "Financial Summary" in c_chat["response"]
