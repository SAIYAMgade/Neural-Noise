"""
mcp_server.py - Model Context Protocol (MCP) Server for FinPilot AI.

Exposes safe, typed tools for external AI applications and Claude Desktop / IDEs:
- finpilot_search_clients
- finpilot_get_client_summary
- finpilot_calculate_invoice_totals
- finpilot_create_invoice_draft
- finpilot_list_overdue_invoices
- finpilot_get_financial_summary
"""

from __future__ import annotations

import asyncio
import json
import uuid
from decimal import Decimal
from typing import Any

from mcp.server.mcpserver import MCPServer
from api.database import get_db_manager
from services.client_service import list_clients, get_client_ledger
from services.invoice_service import create_invoice_draft, list_invoices
from services.financial_calculator import calculate_invoice_totals
from services.payment_service import list_payments

mcp = MCPServer("FinPilot AI Financial Operations")
DEFAULT_BUSINESS_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


@mcp.tool()
async def finpilot_search_clients(query: str) -> str:
    """Search clients by name, company, email, or GSTIN."""
    db_mgr = get_db_manager()
    async with db_mgr.session() as session:
        clients = await list_clients(session, DEFAULT_BUSINESS_ID, search=query, limit=10)
        res = [
            {
                "id": str(c.id),
                "name": c.name,
                "company_name": c.company_name,
                "email": c.email,
                "state_code": c.state_code,
                "gstin": c.gstin,
            }
            for c in clients
        ]
        return json.dumps(res, indent=2)


@mcp.tool()
async def finpilot_get_client_summary(client_id: str) -> str:
    """Retrieve full client ledger summary, balance due, and overdue count."""
    db_mgr = get_db_manager()
    async with db_mgr.session() as session:
        cid = uuid.UUID(client_id)
        ledger = await get_client_ledger(session, cid, DEFAULT_BUSINESS_ID)
        if not ledger:
            return json.dumps({"error": "Client not found"})
        return json.dumps({
            "client_name": ledger["client"].company_name or ledger["client"].name,
            "email": ledger["client"].email,
            "gstin": ledger["client"].gstin,
            "total_invoiced": str(ledger["total_invoiced"]),
            "total_paid": str(ledger["total_paid"]),
            "total_due": str(ledger["total_due"]),
            "overdue_invoices_count": ledger["overdue_invoices_count"],
        }, indent=2)


@mcp.tool()
async def finpilot_calculate_invoice_totals(
    line_items_json: str,
    seller_state_code: str = "27",
    buyer_state_code: str = "27",
    is_export: bool = False,
) -> str:
    """Deterministically calculate invoice subtotal, CGST/SGST vs IGST, and grand total."""
    items = json.loads(line_items_json)
    res = calculate_invoice_totals(
        line_items=items,
        seller_state_code=seller_state_code,
        buyer_state_code=buyer_state_code,
        is_export=is_export,
    )
    return json.dumps({
        "subtotal": str(res.subtotal),
        "discount_total": str(res.discount_total),
        "taxable_amount": str(res.taxable_amount),
        "tax_type": res.tax_type,
        "cgst_amount": str(res.cgst_amount),
        "sgst_amount": str(res.sgst_amount),
        "igst_amount": str(res.igst_amount),
        "total_tax": str(res.total_tax),
        "grand_total": str(res.grand_total),
    }, indent=2)


@mcp.tool()
async def finpilot_create_invoice_draft(
    client_id: str,
    amount: float,
    description: str = "Consulting Services",
    due_days: int = 15,
) -> str:
    """Create an uncommitted invoice draft with deterministic GST calculations."""
    db_mgr = get_db_manager()
    async with db_mgr.session() as session:
        cid = uuid.UUID(client_id)
        draft = await create_invoice_draft(
            session=session,
            business_id=DEFAULT_BUSINESS_ID,
            client_id=cid,
            line_items=[{"description": description, "quantity": 1, "unit_price": amount}],
            due_days=due_days,
            actor="agent:mcp",
        )
        await session.commit()
        return json.dumps({
            "status": "draft",
            "invoice_id": str(draft.id),
            "draft_number": draft.invoice_number,
            "grand_total": str(draft.grand_total),
            "due_date": str(draft.due_date),
            "pdf_path": draft.pdf_path,
        }, indent=2)


@mcp.tool()
async def finpilot_list_overdue_invoices() -> str:
    """List all currently overdue invoices across clients."""
    db_mgr = get_db_manager()
    async with db_mgr.session() as session:
        overdue = await list_invoices(session, DEFAULT_BUSINESS_ID, overdue_only=True)
        return json.dumps([
            {
                "invoice_number": inv.invoice_number,
                "client_name": inv.client.company_name or inv.client.name,
                "amount_due": str(inv.amount_due),
                "due_date": str(inv.due_date),
            }
            for inv in overdue
        ], indent=2)


@mcp.tool()
async def finpilot_get_financial_summary() -> str:
    """Retrieve total invoiced, collected, outstanding, and overdue amounts."""
    db_mgr = get_db_manager()
    async with db_mgr.session() as session:
        invoices = await list_invoices(session, DEFAULT_BUSINESS_ID, limit=500)
        tot_inv = sum((i.grand_total for i in invoices if i.status != "cancelled"), Decimal("0.00"))
        tot_paid = sum((i.amount_paid for i in invoices if i.status != "cancelled"), Decimal("0.00"))
        tot_due = sum((i.amount_due for i in invoices if i.status != "cancelled"), Decimal("0.00"))
        return json.dumps({
            "total_invoiced": str(tot_inv),
            "total_collected": str(tot_paid),
            "total_outstanding": str(tot_due),
            "invoices_count": len(invoices),
        }, indent=2)


if __name__ == "__main__":
    mcp.run()
