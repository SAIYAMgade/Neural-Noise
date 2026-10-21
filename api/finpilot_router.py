"""
finpilot_router.py - Modular FastAPI Router for FinPilot AI Financial Operations.
"""

from __future__ import annotations

import os
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db_manager
from api.models import Client, Invoice, Payment, Expense, AuditEvent, ApprovalRequest
from api.schemas import (
    ClientCreateRequest,
    ClientResponse,
    ClientLedgerResponse,
    InvoiceDraftRequest,
    InvoiceIssueRequest,
    InvoiceResponse,
    InvoiceLineItemResponse,
    InvoiceCalculationPreviewRequest,
    InvoiceCalculationPreviewResponse,
    PaymentCreateRequest,
    PaymentAllocationRequest,
    PaymentResponse,
    ExpenseCreateRequest,
    ExpenseResponse,
    AssistantChatRequest,
    AssistantChatResponse,
    ApprovalConfirmRequest,
)
from services.client_service import create_client, get_client, get_client_ledger, list_clients
from services.invoice_service import (
    create_invoice_draft,
    issue_invoice,
    get_invoice,
    list_invoices,
    cancel_invoice,
)
from services.payment_service import record_payment, allocate_payment, list_payments
from services.financial_calculator import calculate_invoice_totals
from services.audit_service import record_audit_event
from agents.finpilot_assistant import FinPilotAssistant

router = APIRouter(tags=["FinPilot Financial Operations"])

# Default business workspace UUID (multi-tenant ready)
DEFAULT_BUSINESS_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
_assistant_instance: FinPilotAssistant | None = None


def get_assistant() -> FinPilotAssistant:
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = FinPilotAssistant()
    return _assistant_instance


async def get_session():
    """Dependency yielding an active AsyncSession."""
    db_mgr = get_db_manager()
    async with db_mgr.session() as session:
        yield session


# ---------------------------------------------------------------------------
# Client Endpoints
# ---------------------------------------------------------------------------

@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def api_create_client(
    payload: ClientCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        client = await create_client(
            session=session,
            business_id=DEFAULT_BUSINESS_ID,
            name=payload.name,
            email=payload.email,
            company_name=payload.company_name,
            phone=payload.phone,
            billing_address=payload.billing_address,
            state_code=payload.state_code,
            gstin=payload.gstin,
            currency=payload.currency,
            payment_terms_days=payload.payment_terms_days,
            notes=payload.notes,
        )
        await session.commit()
        return client
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/clients", response_model=list[ClientResponse])
async def api_list_clients(
    search: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    return await list_clients(session, DEFAULT_BUSINESS_ID, search=search, limit=limit, offset=offset)


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def api_get_client(
    client_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    client = await get_client(session, client_id, DEFAULT_BUSINESS_ID)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("/clients/{client_id}/ledger", response_model=ClientLedgerResponse)
async def api_get_client_ledger(
    client_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    ledger = await get_client_ledger(session, client_id, DEFAULT_BUSINESS_ID)
    if not ledger:
        raise HTTPException(status_code=404, detail="Client not found")
    return ledger


# ---------------------------------------------------------------------------
# Invoice Endpoints
# ---------------------------------------------------------------------------

@router.post("/invoices/draft", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def api_create_invoice_draft(
    payload: InvoiceDraftRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        items = [item.model_dump() for item in payload.line_items]
        draft = await create_invoice_draft(
            session=session,
            business_id=DEFAULT_BUSINESS_ID,
            client_id=payload.client_id,
            line_items=items,
            invoice_date=payload.invoice_date,
            due_date=payload.due_date,
            due_days=payload.due_days,
            notes=payload.notes,
            is_export=payload.is_export,
        )
        await session.commit()
        # Eager reload
        reloaded = await get_invoice(session, draft.id, DEFAULT_BUSINESS_ID)
        return _serialize_invoice(reloaded)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invoices/preview", response_model=InvoiceCalculationPreviewResponse)
async def api_preview_invoice(
    payload: InvoiceCalculationPreviewRequest,
    session: AsyncSession = Depends(get_session),
):
    client = await get_client(session, payload.client_id, DEFAULT_BUSINESS_ID)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    seller_state = os.getenv("BUSINESS_STATE_CODE", "27")
    buyer_state = client.state_code or "27"
    items = [item.model_dump() for item in payload.line_items]
    res = calculate_invoice_totals(
        line_items=items,
        seller_state_code=seller_state,
        buyer_state_code=buyer_state,
        is_export=payload.is_export,
    )
    return {
        "subtotal": res.subtotal,
        "discount_total": res.discount_total,
        "taxable_amount": res.taxable_amount,
        "tax_type": res.tax_type,
        "cgst_amount": res.cgst_amount,
        "sgst_amount": res.sgst_amount,
        "igst_amount": res.igst_amount,
        "total_tax": res.total_tax,
        "grand_total": res.grand_total,
    }


@router.post("/invoices/{invoice_id}/issue", response_model=InvoiceResponse)
async def api_issue_invoice(
    invoice_id: uuid.UUID,
    payload: InvoiceIssueRequest | None = None,
    session: AsyncSession = Depends(get_session),
):
    try:
        idem_key = payload.idempotency_key if payload else None
        issued = await issue_invoice(
            session=session,
            invoice_id=invoice_id,
            business_id=DEFAULT_BUSINESS_ID,
            idempotency_key=idem_key,
        )
        await session.commit()
        reloaded = await get_invoice(session, issued.id, DEFAULT_BUSINESS_ID)
        return _serialize_invoice(reloaded)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/invoices", response_model=list[InvoiceResponse])
async def api_list_invoices(
    client_id: uuid.UUID | None = None,
    status: str | None = None,
    overdue_only: bool = False,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    invoices = await list_invoices(
        session=session,
        business_id=DEFAULT_BUSINESS_ID,
        client_id=client_id,
        status=status,
        overdue_only=overdue_only,
        limit=limit,
        offset=offset,
    )
    return [_serialize_invoice(inv) for inv in invoices]


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def api_get_invoice(
    invoice_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    inv = await get_invoice(session, invoice_id, DEFAULT_BUSINESS_ID)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return _serialize_invoice(inv)


@router.get("/invoices/{invoice_id}/pdf")
async def api_download_invoice_pdf(
    invoice_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    inv = await get_invoice(session, invoice_id, DEFAULT_BUSINESS_ID)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Auto-generate PDF on the fly if missing from disk
    if not inv.pdf_path or not os.path.exists(inv.pdf_path):
        from services.pdf_generator import generate_invoice_pdf
        client = inv.client
        inv_dict = {
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "due_date": inv.due_date,
            "status": inv.status,
            "currency": inv.currency,
            "subtotal": inv.subtotal,
            "discount_total": inv.discount_total,
            "tax_type": inv.tax_type,
            "cgst_amount": inv.cgst_amount,
            "sgst_amount": inv.sgst_amount,
            "igst_amount": inv.igst_amount,
            "total_tax": inv.total_tax,
            "grand_total": inv.grand_total,
            "amount_paid": inv.amount_paid,
            "amount_due": inv.amount_due,
            "notes": inv.notes,
            "line_items": [
                {
                    "description": item.description,
                    "hsn_sac_code": item.hsn_sac_code,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "discount_pct": item.discount_pct,
                    "tax_rate_pct": item.tax_rate_pct,
                    "line_total": item.line_total,
                    "tax_amount": item.tax_amount,
                }
                for item in inv.line_items
            ],
        }
        client_dict = {
            "name": client.name if client else "Client",
            "company_name": client.company_name if client else None,
            "billing_address": client.billing_address if client else None,
            "gstin": client.gstin if client else None,
            "state_code": client.state_code if client else None,
            "email": client.email if client else None,
            "phone": client.phone if client else None,
        }
        pdf_path = generate_invoice_pdf(inv_dict, client_dict)
        inv.pdf_path = str(pdf_path)
        await session.commit()

    return FileResponse(
        inv.pdf_path,
        media_type="application/pdf",
        filename=f"{inv.invoice_number}.pdf",
    )


@router.post("/invoices/{invoice_id}/cancel", response_model=InvoiceResponse)
async def api_cancel_invoice(
    invoice_id: uuid.UUID,
    reason: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    try:
        inv = await cancel_invoice(session, invoice_id, DEFAULT_BUSINESS_ID, reason)
        await session.commit()
        return _serialize_invoice(inv)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Payment Endpoints
# ---------------------------------------------------------------------------

@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def api_record_payment(
    payload: PaymentCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        payment, allocated = await record_payment(
            session=session,
            business_id=DEFAULT_BUSINESS_ID,
            client_id=payload.client_id,
            amount=payload.amount,
            payment_date=payload.payment_date,
            payment_method=payload.payment_method,
            reference_number=payload.reference_number,
            notes=payload.notes,
            allocate_to_invoice_id=payload.allocate_to_invoice_id,
        )
        await session.commit()
        return payment
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payments/allocate")
async def api_allocate_payment(
    payload: PaymentAllocationRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        allocated = await allocate_payment(
            session=session,
            payment_id=payload.payment_id,
            invoice_id=payload.invoice_id,
            business_id=DEFAULT_BUSINESS_ID,
            amount_to_allocate=payload.amount_to_allocate,
        )
        await session.commit()
        return {"allocated_amount": str(allocated), "status": "allocated"}
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payments", response_model=list[PaymentResponse])
async def api_list_payments(
    client_id: uuid.UUID | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    return await list_payments(session, DEFAULT_BUSINESS_ID, client_id=client_id, limit=limit, offset=offset)


# ---------------------------------------------------------------------------
# Expense Endpoints
# ---------------------------------------------------------------------------

@router.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def api_create_expense(
    payload: ExpenseCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    expense = Expense(
        id=uuid.uuid4(),
        business_id=DEFAULT_BUSINESS_ID,
        date=payload.date,
        category=payload.category,
        merchant=payload.merchant,
        amount=payload.amount,
        tax_amount=payload.tax_amount,
        gstin=payload.gstin,
        payment_method=payload.payment_method,
        notes=payload.notes,
        is_verified=True,
    )
    session.add(expense)
    await record_audit_event(
        session=session,
        business_id=DEFAULT_BUSINESS_ID,
        action="expense.created",
        actor="user:manual",
        entity_type="expense",
        entity_id=expense.id,
        details={"merchant": expense.merchant, "amount": str(expense.amount)},
    )
    await session.commit()
    return expense


@router.get("/expenses", response_model=list[ExpenseResponse])
async def api_list_expenses(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Expense)
        .where(Expense.business_id == DEFAULT_BUSINESS_ID)
        .order_by(Expense.date.desc())
        .limit(limit)
        .offset(offset)
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


# ---------------------------------------------------------------------------
# FinPilot AI Assistant Chat Endpoints
# ---------------------------------------------------------------------------

@router.post("/assistant/chat", response_model=AssistantChatResponse)
async def api_assistant_chat(
    payload: AssistantChatRequest,
    session: AsyncSession = Depends(get_session),
    assistant: FinPilotAssistant = Depends(get_assistant),
):
    conv_id = payload.conversation_id or uuid.uuid4()
    result = await assistant.chat(
        message=payload.message,
        business_id=DEFAULT_BUSINESS_ID,
        session=session,
        conversation_id=conv_id,
        approval_request_id=payload.approval_request_id,
    )
    await session.commit()

    card_type = result.get("card_type")
    card_data = result.get("card_data")
    final_resp = result.get("final_response", "")
    return {
        "response": final_resp,
        "message": final_resp,
        "reply": final_resp,
        "conversation_id": conv_id,
        "intent": result.get("intent", "general"),
        "tool_name": result.get("tool_name"),
        "card_type": card_type,
        "card_data": card_data,
        "structured_card": {"type": card_type, "data": card_data} if card_type else None,
        "requires_approval": result.get("requires_approval", False),
        "approval_request_id": result.get("approval_request_id"),
    }


@router.post("/assistant/approve")
async def api_assistant_approve(
    payload: ApprovalConfirmRequest,
    session: AsyncSession = Depends(get_session),
    assistant: FinPilotAssistant = Depends(get_assistant),
):
    result = await assistant.chat(
        message="confirm and issue",
        business_id=DEFAULT_BUSINESS_ID,
        session=session,
        approval_request_id=payload.approval_request_id,
    )
    await session.commit()
    return result


# ---------------------------------------------------------------------------
# Overview & Audit History
# ---------------------------------------------------------------------------

@router.get("/overview")
async def api_get_overview(session: AsyncSession = Depends(get_session)):
    """Computes authoritative financial overview metrics."""
    invoices = await list_invoices(session, DEFAULT_BUSINESS_ID, limit=500)
    payments = await list_payments(session, DEFAULT_BUSINESS_ID, limit=500)
    
    total_invoiced = Decimal("0.00")
    total_collected = Decimal("0.00")
    total_outstanding = Decimal("0.00")
    overdue_amount = Decimal("0.00")
    overdue_count = 0
    today = date.today()

    for inv in invoices:
        if inv.status != "cancelled":
            total_invoiced += inv.grand_total
            total_collected += inv.amount_paid
            total_outstanding += inv.amount_due
            if inv.status in ("issued", "partially_paid", "overdue") and inv.due_date < today:
                overdue_amount += inv.amount_due
                overdue_count += 1

    # Expenses sum
    exp_stmt = select(func.sum(Expense.amount)).where(Expense.business_id == DEFAULT_BUSINESS_ID)
    total_expenses = (await session.execute(exp_stmt)).scalar() or Decimal("0.00")

    # Recent Audit logs
    audit_stmt = (
        select(AuditEvent)
        .where(AuditEvent.business_id == DEFAULT_BUSINESS_ID)
        .order_by(AuditEvent.created_at.desc())
        .limit(10)
    )
    recent_audits = list((await session.execute(audit_stmt)).scalars().all())

    return {
        "total_invoiced": str(total_invoiced),
        "total_collected": str(total_collected),
        "total_outstanding": str(total_outstanding),
        "overdue_amount": str(overdue_amount),
        "overdue_count": overdue_count,
        "total_expenses": str(total_expenses),
        "net_cash_flow": str(total_collected - total_expenses),
        "invoices_count": len(invoices),
        "payments_count": len(payments),
        "recent_audit_events": [
            {
                "id": str(a.id),
                "action": a.action,
                "actor": a.actor,
                "entity_type": a.entity_type,
                "entity_id": str(a.entity_id) if a.entity_id else None,
                "details": a.details,
                "created_at": a.created_at.isoformat(),
            }
            for a in recent_audits
        ],
    }


@router.get("/audit-events")
async def api_list_audit_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(AuditEvent)
        .where(AuditEvent.business_id == DEFAULT_BUSINESS_ID)
        .order_by(AuditEvent.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    res = await session.execute(stmt)
    events = list(res.scalars().all())
    return [
        {
            "id": str(a.id),
            "action": a.action,
            "actor": a.actor,
            "entity_type": a.entity_type,
            "entity_id": str(a.entity_id) if a.entity_id else None,
            "details": a.details,
            "created_at": a.created_at.isoformat(),
        }
        for a in events
    ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _serialize_invoice(inv: Invoice) -> dict[str, Any]:
    return {
        "id": inv.id,
        "business_id": inv.business_id,
        "client_id": inv.client_id,
        "client_name": inv.client.company_name or inv.client.name if inv.client else None,
        "invoice_number": inv.invoice_number,
        "invoice_date": inv.invoice_date,
        "due_date": inv.due_date,
        "status": inv.status,
        "currency": inv.currency,
        "subtotal": inv.subtotal,
        "discount_total": inv.discount_total,
        "tax_type": inv.tax_type,
        "cgst_amount": inv.cgst_amount,
        "sgst_amount": inv.sgst_amount,
        "igst_amount": inv.igst_amount,
        "total_tax": inv.total_tax,
        "grand_total": inv.grand_total,
        "amount_paid": inv.amount_paid,
        "amount_due": inv.amount_due,
        "notes": inv.notes,
        "pdf_path": inv.pdf_path,
        "created_at": inv.created_at,
        "issued_at": inv.issued_at,
        "line_items": [
            {
                "id": li.id,
                "description": li.description,
                "hsn_sac_code": li.hsn_sac_code,
                "quantity": li.quantity,
                "unit_price": li.unit_price,
                "discount_pct": li.discount_pct,
                "tax_rate_pct": li.tax_rate_pct,
                "line_total": li.line_total,
                "tax_amount": li.tax_amount,
            }
            for li in inv.line_items
        ],
    }
