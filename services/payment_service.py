"""
payment_service.py - Payment Recording and Deterministic Invoice Reconciliation for FinPilot AI.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models import Client, Invoice, Payment, PaymentAllocation, IdempotencyRecord
from services.financial_calculator import quantize_money, compute_payment_allocation
from services.audit_service import record_audit_event


async def _generate_next_payment_number(session: AsyncSession, business_id: uuid.UUID) -> str:
    """Generate sequential payment number: PAY-YYYY-NNNN monotonically."""
    current_year = date.today().year
    prefix = f"PAY-{current_year}-"
    stmt = (
        select(Payment.payment_number)
        .where(Payment.payment_number.like(f"{prefix}%"))
        .order_by(Payment.payment_number.desc())
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


async def record_payment(
    session: AsyncSession,
    business_id: uuid.UUID,
    client_id: uuid.UUID,
    amount: Decimal | float | str,
    payment_date: date | None = None,
    payment_method: str = "bank_transfer",
    reference_number: str | None = None,
    notes: str | None = None,
    allocate_to_invoice_id: uuid.UUID | None = None,
    actor: str = "user:manual",
) -> tuple[Payment, Decimal]:
    """
    Record a received payment and optionally allocate immediately to an invoice.
    Returns (payment, allocated_amount).
    """
    pay_amount = quantize_money(amount)
    if pay_amount <= Decimal("0.00"):
        raise ValueError(f"Payment amount must be greater than zero: {pay_amount}")

    client_stmt = select(Client).where(Client.id == client_id, Client.business_id == business_id)
    client = (await session.execute(client_stmt)).scalar_one_or_none()
    if not client:
        raise ValueError(f"Client '{client_id}' does not exist.")

    pay_number = await _generate_next_payment_number(session, business_id)

    payment = Payment(
        id=uuid.uuid4(),
        business_id=business_id,
        client_id=client_id,
        payment_number=pay_number,
        payment_date=payment_date or date.today(),
        amount=pay_amount,
        currency=client.currency or "INR",
        payment_method=payment_method,
        reference_number=reference_number,
        status="settled",
        notes=notes,
        allocated_amount=Decimal("0.00"),
        unallocated_amount=pay_amount,
    )
    session.add(payment)
    await session.flush()

    total_allocated = Decimal("0.00")
    if allocate_to_invoice_id:
        alloc_amt = await allocate_payment(
            session=session,
            payment_id=payment.id,
            invoice_id=allocate_to_invoice_id,
            business_id=business_id,
            amount_to_allocate=pay_amount,
            actor=actor,
        )
        total_allocated = alloc_amt

    await record_audit_event(
        session=session,
        business_id=business_id,
        action="payment.recorded",
        actor=actor,
        entity_type="payment",
        entity_id=payment.id,
        details={
            "payment_number": payment.payment_number,
            "amount": str(payment.amount),
            "allocated_amount": str(payment.allocated_amount),
            "unallocated_amount": str(payment.unallocated_amount),
        },
    )
    return payment, total_allocated


async def allocate_payment(
    session: AsyncSession,
    payment_id: uuid.UUID,
    invoice_id: uuid.UUID,
    business_id: uuid.UUID,
    amount_to_allocate: Decimal | float | str | None = None,
    actor: str = "user:manual",
) -> Decimal:
    """
    Allocate payment funds to an issued invoice.
    Returns the exact Decimal allocated.
    """
    pay_stmt = (
        select(Payment)
        .options(selectinload(Payment.allocations))
        .where(Payment.id == payment_id, Payment.business_id == business_id)
    )
    payment = (await session.execute(pay_stmt)).scalar_one_or_none()
    if not payment:
        raise ValueError(f"Payment '{payment_id}' not found.")

    inv_stmt = (
        select(Invoice)
        .options(selectinload(Invoice.allocations))
        .where(Invoice.id == invoice_id, Invoice.business_id == business_id)
    )
    invoice = (await session.execute(inv_stmt)).scalar_one_or_none()
    if not invoice:
        raise ValueError(f"Invoice '{invoice_id}' not found.")

    if payment.client_id != invoice.client_id:
        raise ValueError("Cannot allocate payment to an invoice belonging to a different client.")

    if invoice.status not in ("issued", "partially_paid", "overdue"):
        raise ValueError(f"Cannot allocate payment to invoice with status '{invoice.status}'.")

    if payment.unallocated_amount <= Decimal("0.00"):
        raise ValueError("Payment has no remaining unallocated funds.")

    max_possible = min(payment.unallocated_amount, invoice.amount_due)
    if amount_to_allocate is not None:
        requested = quantize_money(amount_to_allocate)
        if requested > max_possible:
            raise ValueError(
                f"Requested allocation ₹{requested} exceeds maximum allowable ₹{max_possible} "
                f"(Unallocated: ₹{payment.unallocated_amount}, Due: ₹{invoice.amount_due})"
            )
        allocation_amount = requested
    else:
        allocation_amount = max_possible

    if allocation_amount <= Decimal("0.00"):
        return Decimal("0.00")

    # Update invoice state
    allocated, new_paid, new_due, new_status = compute_payment_allocation(
        payment_amount=allocation_amount,
        current_amount_paid=invoice.amount_paid,
        grand_total=invoice.grand_total,
    )
    invoice.amount_paid = new_paid
    invoice.amount_due = new_due
    invoice.status = new_status

    # Update payment state
    payment.allocated_amount = quantize_money(payment.allocated_amount + allocated)
    payment.unallocated_amount = quantize_money(payment.amount - payment.allocated_amount)

    # Create allocation record
    alloc_record = PaymentAllocation(
        id=uuid.uuid4(),
        payment_id=payment.id,
        invoice_id=invoice.id,
        allocated_amount=allocated,
        allocated_at=datetime.now(timezone.utc),
    )
    session.add(alloc_record)
    await session.flush()

    await record_audit_event(
        session=session,
        business_id=business_id,
        action="payment.allocated",
        actor=actor,
        entity_type="payment_allocation",
        entity_id=alloc_record.id,
        details={
            "payment_id": str(payment.id),
            "invoice_id": str(invoice.id),
            "allocated_amount": str(allocated),
            "invoice_remaining_due": str(invoice.amount_due),
            "invoice_status": invoice.status,
        },
    )
    return allocated


async def list_payments(
    session: AsyncSession,
    business_id: uuid.UUID,
    client_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Payment]:
    """List payments with optional client filter."""
    stmt = (
        select(Payment)
        .options(selectinload(Payment.allocations), selectinload(Payment.client))
        .where(Payment.business_id == business_id)
    )
    if client_id:
        stmt = stmt.where(Payment.client_id == client_id)
    stmt = stmt.order_by(Payment.payment_date.desc(), Payment.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return list(result.scalars().all())
