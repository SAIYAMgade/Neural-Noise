"""
client_service.py - Client and Customer Ledger Management for FinPilot AI.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any
from datetime import date

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models import Client, Invoice, Payment
from services.financial_calculator import validate_gstin
from services.audit_service import record_audit_event


async def create_client(
    session: AsyncSession,
    business_id: uuid.UUID,
    name: str,
    email: str,
    company_name: str | None = None,
    phone: str | None = None,
    billing_address: str | None = None,
    state_code: str = "27",
    gstin: str | None = None,
    currency: str = "INR",
    payment_terms_days: int = 15,
    notes: str | None = None,
    actor: str = "user:manual",
) -> Client:
    """Create a new client with validated fields."""
    if gstin:
        is_valid, msg = validate_gstin(gstin)
        if not is_valid:
            raise ValueError(f"Invalid GSTIN: {msg}")
        # Automatically align state_code if valid GSTIN provided
        state_code = gstin[:2]

    client = Client(
        id=uuid.uuid4(),
        business_id=business_id,
        name=name.strip(),
        company_name=company_name.strip() if company_name else None,
        email=email.strip().lower(),
        phone=phone.strip() if phone else None,
        billing_address=billing_address.strip() if billing_address else None,
        state_code=str(state_code).zfill(2),
        gstin=gstin.strip().upper() if gstin else None,
        currency=currency.upper(),
        payment_terms_days=payment_terms_days,
        status="active",
        notes=notes,
    )
    session.add(client)
    await session.flush()

    await record_audit_event(
        session=session,
        business_id=business_id,
        action="client.created",
        actor=actor,
        entity_type="client",
        entity_id=client.id,
        details={"name": client.name, "company": client.company_name, "email": client.email},
    )
    return client


async def get_client(
    session: AsyncSession,
    client_id: uuid.UUID,
    business_id: uuid.UUID | None = None,
) -> Client | None:
    """Retrieve client by ID."""
    stmt = select(Client).where(Client.id == client_id)
    if business_id:
        stmt = stmt.where(Client.business_id == business_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_clients(
    session: AsyncSession,
    business_id: uuid.UUID,
    search: str | None = None,
    status: str = "active",
    limit: int = 50,
    offset: int = 0,
) -> list[Client]:
    """List clients with optional search."""
    stmt = select(Client).where(Client.business_id == business_id)
    if status:
        stmt = stmt.where(Client.status == status)
    if search:
        term = f"%{search.strip().lower()}%"
        stmt = stmt.where(
            func.lower(Client.name).like(term)
            | func.lower(Client.company_name).like(term)
            | func.lower(Client.email).like(term)
            | func.lower(Client.gstin).like(term)
        )
    stmt = stmt.order_by(Client.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_client_ledger(
    session: AsyncSession,
    client_id: uuid.UUID,
    business_id: uuid.UUID,
) -> dict[str, Any] | None:
    """
    Computes deterministic client ledger totals:
    - Total Invoiced
    - Total Paid
    - Balance Due
    - Overdue Count
    - List of Invoices
    - List of Payments
    """
    client = await get_client(session, client_id, business_id)
    if not client:
        return None

    # Invoices for this client
    inv_stmt = select(Invoice).where(
        Invoice.client_id == client_id,
        Invoice.business_id == business_id,
    ).order_by(Invoice.invoice_date.desc())
    inv_res = await session.execute(inv_stmt)
    invoices = list(inv_res.scalars().all())

    # Payments for this client
    pay_stmt = select(Payment).where(
        Payment.client_id == client_id,
        Payment.business_id == business_id,
    ).order_by(Payment.payment_date.desc())
    pay_res = await session.execute(pay_stmt)
    payments = list(pay_res.scalars().all())

    total_invoiced = Decimal("0.00")
    total_paid = Decimal("0.00")
    total_due = Decimal("0.00")
    overdue_count = 0
    today = date.today()

    for inv in invoices:
        if inv.status != "cancelled":
            total_invoiced += inv.grand_total
            total_paid += inv.amount_paid
            total_due += inv.amount_due
            if inv.status in ("issued", "partially_paid", "overdue") and inv.due_date < today:
                overdue_count += 1

    return {
        "client": client,
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_due": total_due,
        "overdue_invoices_count": overdue_count,
        "invoices_count": len(invoices),
        "payments_count": len(payments),
        "invoices": invoices,
        "payments": payments,
    }
