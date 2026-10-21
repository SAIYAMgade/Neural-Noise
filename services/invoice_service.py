"""
invoice_service.py - Invoicing Engine, GST calculations, and State Machine for FinPilot AI.
"""

from __future__ import annotations

import os
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models import Client, Invoice, InvoiceLineItem, IdempotencyRecord
from services.financial_calculator import (
    calculate_invoice_totals,
    quantize_money,
    InvoiceCalculationResult,
)
from services.pdf_generator import generate_invoice_pdf
from services.audit_service import record_audit_event


async def _generate_next_invoice_number(session: AsyncSession, business_id: uuid.UUID) -> str:
    """Generate sequential invoice number: INV-YYYY-NNNN monotonically."""
    current_year = date.today().year
    prefix = f"INV-{current_year}-"
    stmt = (
        select(Invoice.invoice_number)
        .where(Invoice.invoice_number.like(f"{prefix}%"))
        .order_by(Invoice.invoice_number.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    latest = result.scalar_one_or_none()
    if latest:
        try:
            num = int(latest.split("-")[-1])
            return f"{prefix}{str(num + 1).zfill(4)}"
        except (ValueError, IndexError):
            pass
    return f"{prefix}0001"


async def create_invoice_draft(
    session: AsyncSession,
    business_id: uuid.UUID,
    client_id: uuid.UUID,
    line_items: list[dict[str, Any]],
    invoice_date: date | None = None,
    due_date: date | None = None,
    due_days: int | None = None,
    notes: str | None = None,
    is_export: bool = False,
    actor: str = "user:manual",
) -> Invoice:
    """
    Create an invoice draft with deterministic calculations.
    """
    # Fetch client to determine tax treatment from state code
    client_stmt = select(Client).where(Client.id == client_id, Client.business_id == business_id)
    client_res = await session.execute(client_stmt)
    client = client_res.scalar_one_or_none()
    if not client:
        raise ValueError(f"Client with ID '{client_id}' does not exist.")

    seller_state = os.getenv("BUSINESS_STATE_CODE", "27")
    buyer_state = client.state_code or "27"

    calc_res: InvoiceCalculationResult = calculate_invoice_totals(
        line_items=line_items,
        seller_state_code=seller_state,
        buyer_state_code=buyer_state,
        is_export=is_export,
    )

    inv_date = invoice_date or date.today()
    if due_date:
        inv_due_date = due_date
    elif due_days is not None:
        inv_due_date = inv_date + timedelta(days=due_days)
    else:
        inv_due_date = inv_date + timedelta(days=client.payment_terms_days or 15)

    temp_draft_number = f"DRAFT-{uuid.uuid4().hex[:8].upper()}"

    invoice = Invoice(
        id=uuid.uuid4(),
        business_id=business_id,
        client_id=client_id,
        invoice_number=temp_draft_number,
        invoice_date=inv_date,
        due_date=inv_due_date,
        status="draft",
        currency=client.currency or "INR",
        subtotal=calc_res.subtotal,
        discount_total=calc_res.discount_total,
        tax_type=calc_res.tax_type,
        cgst_amount=calc_res.cgst_amount,
        sgst_amount=calc_res.sgst_amount,
        igst_amount=calc_res.igst_amount,
        total_tax=calc_res.total_tax,
        grand_total=calc_res.grand_total,
        amount_paid=Decimal("0.00"),
        amount_due=calc_res.grand_total,
        notes=notes,
    )
    session.add(invoice)
    await session.flush()

    for item in calc_res.line_items:
        line_item = InvoiceLineItem(
            id=uuid.uuid4(),
            invoice_id=invoice.id,
            description=item.description,
            hsn_sac_code=item.hsn_sac_code,
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount_pct=item.discount_pct,
            tax_rate_pct=item.tax_rate_pct,
            line_total=item.line_total,
            tax_amount=item.tax_amount,
        )
        session.add(line_item)

    await session.flush()

    # Generate draft PDF
    client_dict = {
        "name": client.name,
        "company_name": client.company_name,
        "email": client.email,
        "billing_address": client.billing_address,
        "state_code": client.state_code,
        "gstin": client.gstin,
    }
    inv_dict = {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date,
        "due_date": invoice.due_date,
        "status": invoice.status,
        "subtotal": invoice.subtotal,
        "discount_total": invoice.discount_total,
        "tax_type": invoice.tax_type,
        "cgst_amount": invoice.cgst_amount,
        "sgst_amount": invoice.sgst_amount,
        "igst_amount": invoice.igst_amount,
        "total_tax": invoice.total_tax,
        "grand_total": invoice.grand_total,
        "amount_paid": invoice.amount_paid,
        "amount_due": invoice.amount_due,
        "notes": invoice.notes,
        "line_items": [
            {
                "description": li.description,
                "hsn_sac_code": li.hsn_sac_code,
                "quantity": li.quantity,
                "unit_price": li.unit_price,
                "tax_rate_pct": li.tax_rate_pct,
                "line_total": li.line_total,
            }
            for li in calc_res.line_items
        ],
    }
    pdf_path = generate_invoice_pdf(invoice_data=inv_dict, client_data=client_dict)
    invoice.pdf_path = str(pdf_path)

    await record_audit_event(
        session=session,
        business_id=business_id,
        action="invoice.draft_created",
        actor=actor,
        entity_type="invoice",
        entity_id=invoice.id,
        details={
            "invoice_number": invoice.invoice_number,
            "grand_total": str(invoice.grand_total),
            "client_id": str(client.id),
        },
    )
    return invoice


async def issue_invoice(
    session: AsyncSession,
    invoice_id: uuid.UUID,
    business_id: uuid.UUID,
    idempotency_key: str | None = None,
    actor: str = "user:manual",
) -> Invoice:
    """
    Issue an invoice draft. Assigns official sequential invoice number,
    commits state transition to 'issued', generates official PDF, and records audit event.
    """
    if idempotency_key:
        stmt_idem = select(IdempotencyRecord).where(
            IdempotencyRecord.business_id == business_id,
            IdempotencyRecord.idempotency_key == idempotency_key,
        )
        existing_idem = (await session.execute(stmt_idem)).scalar_one_or_none()
        if existing_idem:
            orig_id_str = existing_idem.response_payload.get("invoice_id")
            if orig_id_str and str(invoice_id) != orig_id_str:
                raise ValueError(
                    f"Idempotency key '{idempotency_key}' was already used for a different invoice ({orig_id_str})."
                )
            orig_inv_id = uuid.UUID(orig_id_str) if orig_id_str else invoice_id
            return await get_invoice(session, orig_inv_id, business_id)

    invoice = await get_invoice(session, invoice_id, business_id)
    if not invoice:
        raise ValueError(f"Invoice '{invoice_id}' not found.")

    if invoice.status not in ("draft", "pending_approval"):
        raise ValueError(f"Cannot issue invoice with status '{invoice.status}'. Must be 'draft' or 'pending_approval'.")

    # Generate sequential official invoice number
    official_num = await _generate_next_invoice_number(session, business_id)
    invoice.invoice_number = official_num
    invoice.status = "issued"
    invoice.issued_at = datetime.now(timezone.utc)

    # Re-generate PDF with official number and no draft watermark
    client = invoice.client
    client_dict = {
        "name": client.name,
        "company_name": client.company_name,
        "email": client.email,
        "billing_address": client.billing_address,
        "state_code": client.state_code,
        "gstin": client.gstin,
    }
    inv_dict = {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date,
        "due_date": invoice.due_date,
        "status": invoice.status,
        "subtotal": invoice.subtotal,
        "discount_total": invoice.discount_total,
        "tax_type": invoice.tax_type,
        "cgst_amount": invoice.cgst_amount,
        "sgst_amount": invoice.sgst_amount,
        "igst_amount": invoice.igst_amount,
        "total_tax": invoice.total_tax,
        "grand_total": invoice.grand_total,
        "amount_paid": invoice.amount_paid,
        "amount_due": invoice.amount_due,
        "notes": invoice.notes,
        "line_items": [
            {
                "description": li.description,
                "hsn_sac_code": li.hsn_sac_code,
                "quantity": li.quantity,
                "unit_price": li.unit_price,
                "tax_rate_pct": li.tax_rate_pct,
                "line_total": li.line_total,
            }
            for li in invoice.line_items
        ],
    }
    pdf_path = generate_invoice_pdf(invoice_data=inv_dict, client_data=client_dict)
    invoice.pdf_path = str(pdf_path)

    if idempotency_key:
        idem = IdempotencyRecord(
            id=uuid.uuid4(),
            business_id=business_id,
            idempotency_key=idempotency_key,
            action="invoice.issued",
            request_hash=str(invoice.id),
            response_payload={"invoice_id": str(invoice.id), "invoice_number": invoice.invoice_number},
        )
        session.add(idem)

    await record_audit_event(
        session=session,
        business_id=business_id,
        action="invoice.issued",
        actor=actor,
        entity_type="invoice",
        entity_id=invoice.id,
        details={
            "invoice_number": invoice.invoice_number,
            "grand_total": str(invoice.grand_total),
            "due_date": str(invoice.due_date),
        },
    )
    return invoice


async def get_invoice(
    session: AsyncSession,
    invoice_id: uuid.UUID,
    business_id: uuid.UUID | None = None,
) -> Invoice | None:
    """Retrieve invoice with line items and client eager-loaded."""
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.line_items), selectinload(Invoice.client))
        .where(Invoice.id == invoice_id)
    )
    if business_id:
        stmt = stmt.where(Invoice.business_id == business_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_invoices(
    session: AsyncSession,
    business_id: uuid.UUID,
    client_id: uuid.UUID | None = None,
    status: str | None = None,
    overdue_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[Invoice]:
    """List invoices with filters."""
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.line_items), selectinload(Invoice.client))
        .where(Invoice.business_id == business_id)
    )
    if client_id:
        stmt = stmt.where(Invoice.client_id == client_id)
    if status:
        stmt = stmt.where(Invoice.status == status)
    if overdue_only:
        today = date.today()
        stmt = stmt.where(
            Invoice.status.in_(["issued", "partially_paid", "overdue"]),
            Invoice.due_date < today,
        )

    stmt = stmt.order_by(Invoice.invoice_date.desc(), Invoice.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def cancel_invoice(
    session: AsyncSession,
    invoice_id: uuid.UUID,
    business_id: uuid.UUID,
    reason: str | None = None,
    actor: str = "user:manual",
) -> Invoice:
    """Cancel an invoice if no payments have been allocated."""
    invoice = await get_invoice(session, invoice_id, business_id)
    if not invoice:
        raise ValueError(f"Invoice '{invoice_id}' not found.")
    if invoice.amount_paid > Decimal("0.00"):
        raise ValueError(f"Cannot cancel invoice '{invoice.invoice_number}' because payments of ₹{invoice.amount_paid} are allocated to it.")

    invoice.status = "cancelled"
    await record_audit_event(
        session=session,
        business_id=business_id,
        action="invoice.cancelled",
        actor=actor,
        entity_type="invoice",
        entity_id=invoice.id,
        details={"reason": reason or "User requested cancellation"},
    )
    return invoice
