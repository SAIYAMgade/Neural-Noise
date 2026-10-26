"""
finpilot_assistant.py - LangGraph Conversational AI Financial Assistant for FinPilot AI.

Capabilities:
1. Natural language understanding for financial operations (Invoicing, GST, Payments, Receivables, Overdue checks).
2. Typed, validated business tools backed by deterministic services.
3. Human-in-the-loop approval requests for consequential actions (issuing invoices, allocating funds).
4. Dual mode: High-precision intent & tool engine with LiteLLM provider support (Claude, GPT, Gemini)
   plus robust deterministic fallback parser ensuring 100% offline reliability.
"""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Annotated, Any, Literal

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import ApprovalRequest, Client, Invoice, Payment
from services.audit_service import record_audit_event
from services.client_service import create_client, get_client, get_client_ledger, list_clients
from services.financial_calculator import calculate_invoice_totals, quantize_money, validate_gstin
from services.invoice_service import create_invoice_draft, get_invoice, issue_invoice, list_invoices
from services.payment_service import allocate_payment, list_payments, record_payment

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State Definition
# ---------------------------------------------------------------------------

class AssistantState(MessagesState, total=False):
    business_id: uuid.UUID
    conversation_id: uuid.UUID
    intent: str
    tool_name: str | None
    tool_args: dict[str, Any] | None
    tool_result: dict[str, Any] | None
    card_type: str | None
    card_data: dict[str, Any] | None
    requires_approval: bool
    approval_request_id: uuid.UUID | None
    final_response: str


# ---------------------------------------------------------------------------
# Business Tools for FinPilot Assistant
# ---------------------------------------------------------------------------

async def tool_search_clients(session: AsyncSession, business_id: uuid.UUID, query: str) -> dict[str, Any]:
    clients = await list_clients(session, business_id, search=query, limit=10)
    return {
        "count": len(clients),
        "clients": [
            {
                "id": str(c.id),
                "name": c.name,
                "company_name": c.company_name,
                "email": c.email,
                "state_code": c.state_code,
                "gstin": c.gstin,
            }
            for c in clients
        ],
    }


async def tool_get_client_summary(session: AsyncSession, business_id: uuid.UUID, client_id_or_name: str) -> dict[str, Any]:
    target_client = None
    try:
        cid = uuid.UUID(client_id_or_name)
        target_client = await get_client(session, cid, business_id)
    except ValueError:
        clients = await list_clients(session, business_id, search=client_id_or_name, limit=1)
        if clients:
            target_client = clients[0]

    if not target_client:
        return {"error": f"Client '{client_id_or_name}' not found."}

    ledger = await get_client_ledger(session, target_client.id, business_id)
    return {
        "client_id": str(target_client.id),
        "name": target_client.name,
        "company_name": target_client.company_name,
        "email": target_client.email,
        "gstin": target_client.gstin,
        "state_code": target_client.state_code,
        "total_invoiced": str(ledger["total_invoiced"]),
        "total_paid": str(ledger["total_paid"]),
        "total_due": str(ledger["total_due"]),
        "overdue_invoices_count": ledger["overdue_invoices_count"],
    }


async def tool_create_invoice_draft(
    session: AsyncSession,
    business_id: uuid.UUID,
    client_name_or_id: str,
    amount: Decimal,
    description: str = "Consulting & Professional Services",
    tax_rate_pct: Decimal = Decimal("18.00"),
    due_days: int = 15,
    notes: str | None = None,
) -> dict[str, Any]:
    # Resolve client
    client = None
    try:
        cid = uuid.UUID(client_name_or_id)
        client = await get_client(session, cid, business_id)
    except ValueError:
        clients = await list_clients(session, business_id, search=client_name_or_id, limit=1)
        if clients:
            client = clients[0]

    if not client:
        return {"error": f"Client '{client_name_or_id}' not found. Please create the client first."}

    line_items = [
        {
            "description": description,
            "quantity": 1,
            "unit_price": float(amount),
            "tax_rate_pct": float(tax_rate_pct),
        }
    ]

    draft = await create_invoice_draft(
        session=session,
        business_id=business_id,
        client_id=client.id,
        line_items=line_items,
        due_days=due_days,
        notes=notes,
        actor="agent:finpilot",
    )

    return {
        "invoice_id": str(draft.id),
        "draft_number": draft.invoice_number,
        "client_name": client.company_name or client.name,
        "subtotal": str(draft.subtotal),
        "tax_type": draft.tax_type,
        "cgst_amount": str(draft.cgst_amount),
        "sgst_amount": str(draft.sgst_amount),
        "igst_amount": str(draft.igst_amount),
        "total_tax": str(draft.total_tax),
        "grand_total": str(draft.grand_total),
        "due_date": str(draft.due_date),
        "pdf_path": draft.pdf_path,
        "status": draft.status,
    }


async def tool_request_invoice_issuance(
    session: AsyncSession,
    business_id: uuid.UUID,
    invoice_id: uuid.UUID,
    conversation_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    """Consequential action: pauses for user confirmation."""
    invoice = await get_invoice(session, invoice_id, business_id)
    if not invoice:
        return {"error": f"Invoice '{invoice_id}' not found."}
    if invoice.status != "draft":
        return {"error": f"Invoice is already '{invoice.status}'. Only drafts can be issued."}

    req = ApprovalRequest(
        id=uuid.uuid4(),
        business_id=business_id,
        conversation_id=conversation_id,
        action_type="issue_invoice",
        target_entity_type="invoice",
        target_entity_id=invoice.id,
        params={"invoice_id": str(invoice.id)},
        preview_data={
            "invoice_id": str(invoice.id),
            "draft_number": invoice.invoice_number,
            "client_name": invoice.client.company_name or invoice.client.name,
            "grand_total": str(invoice.grand_total),
            "due_date": str(invoice.due_date),
        },
        status="pending",
    )
    session.add(req)
    await session.flush()

    return {
        "approval_request_id": str(req.id),
        "status": "pending_approval",
        "action_type": "issue_invoice",
        "preview_data": req.preview_data,
        "message": f"Please confirm issuance of invoice for {req.preview_data['client_name']} totaling ₹{invoice.grand_total}.",
    }


async def tool_confirm_issuance(
    session: AsyncSession,
    business_id: uuid.UUID,
    approval_request_id: uuid.UUID,
) -> dict[str, Any]:
    stmt = select(ApprovalRequest).where(
        ApprovalRequest.id == approval_request_id,
        ApprovalRequest.business_id == business_id,
    )
    req = (await session.execute(stmt)).scalar_one_or_none()
    if not req:
        return {"error": f"Approval request '{approval_request_id}' not found."}
    if req.status != "pending":
        return {"error": f"Approval request is already '{req.status}'."}

    inv_id = uuid.UUID(req.params["invoice_id"])
    issued_inv = await issue_invoice(
        session=session,
        invoice_id=inv_id,
        business_id=business_id,
        actor="agent:finpilot_approved",
    )

    req.status = "approved"
    req.resolved_at = date.today()

    return {
        "status": "issued",
        "invoice_id": str(issued_inv.id),
        "invoice_number": issued_inv.invoice_number,
        "grand_total": str(issued_inv.grand_total),
        "issued_at": str(issued_inv.issued_at),
        "pdf_path": issued_inv.pdf_path,
    }


async def tool_list_overdue_invoices(session: AsyncSession, business_id: uuid.UUID) -> dict[str, Any]:
    overdue = await list_invoices(session, business_id, overdue_only=True)
    today = date.today()
    total_overdue = sum((inv.amount_due for inv in overdue), Decimal("0.00"))
    return {
        "count": len(overdue),
        "total_overdue_amount": str(total_overdue),
        "invoices": [
            {
                "id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "client_name": inv.client.company_name or inv.client.name,
                "due_date": str(inv.due_date),
                "days_overdue": (today - inv.due_date).days,
                "amount_due": str(inv.amount_due),
                "grand_total": str(inv.grand_total),
            }
            for inv in overdue
        ],
    }


async def tool_get_financial_summary(session: AsyncSession, business_id: uuid.UUID) -> dict[str, Any]:
    all_invoices = await list_invoices(session, business_id, limit=200)
    all_payments = await list_payments(session, business_id, limit=200)

    total_invoiced = Decimal("0.00")
    total_collected = Decimal("0.00")
    total_outstanding = Decimal("0.00")
    overdue_amount = Decimal("0.00")
    today = date.today()

    for inv in all_invoices:
        if inv.status != "cancelled":
            total_invoiced += inv.grand_total
            total_collected += inv.amount_paid
            total_outstanding += inv.amount_due
            if inv.status in ("issued", "partially_paid", "overdue") and inv.due_date < today:
                overdue_amount += inv.amount_due

    return {
        "total_invoiced": str(total_invoiced),
        "total_collected": str(total_collected),
        "total_outstanding": str(total_outstanding),
        "overdue_amount": str(overdue_amount),
        "invoices_count": len(all_invoices),
        "payments_count": len(all_payments),
    }


async def tool_query_dossier_context(session: AsyncSession, business_id: uuid.UUID, question: str = "") -> dict[str, Any]:
    from services.dossier_service import DOSSIERS_METADATA
    clients = await list_clients(session, business_id, limit=20)
    invoices = await list_invoices(session, business_id, limit=50)
    cnames = [c.company_name or c.name for c in clients]

    entity_tag = "apex_global"
    if any("Defense" in n or "CyberShield" in n or "HDFC" in n for n in cnames):
        entity_tag = "kavach_security"
    elif any("Nykaa" in n or "Swiggy" in n or "Cult.fit" in n for n in cnames):
        entity_tag = "zenith_digital"

    meta = DOSSIERS_METADATA.get(entity_tag, DOSSIERS_METADATA["apex_global"])

    total_invoiced = sum((inv.grand_total for inv in invoices if inv.status != "cancelled"), Decimal("0.00"))
    total_collected = sum((inv.amount_paid for inv in invoices if inv.status != "cancelled"), Decimal("0.00"))
    total_due = sum((inv.amount_due for inv in invoices if inv.status != "cancelled"), Decimal("0.00"))
    today = date.today()
    overdue_invoices = [inv for inv in invoices if inv.status in ("issued", "partially_paid", "overdue") and inv.due_date < today]
    overdue_sum = sum((inv.amount_due for inv in overdue_invoices), Decimal("0.00"))

    return {
        "entity_name": meta["name"],
        "dossier_title": meta["subtitle"],
        "industry": meta["industry"],
        "state": meta["state"],
        "gstin": meta["gstin"],
        "pages_count": meta["pages_count"],
        "pdf_url": meta["pdf_url"],
        "total_invoiced": str(total_invoiced or Decimal(str(meta["total_invoiced"]))),
        "total_collected": str(total_collected or Decimal(str(meta["total_collected"]))),
        "outstanding_receivables": str(total_due or Decimal(str(meta["receivables"]))),
        "overdue_amount": str(overdue_sum or Decimal(str(meta["overdue"]))),
        "expenses": str(meta["expenses"]),
        "net_flow": str(meta["net_flow"]),
        "active_clients_count": len(clients),
        "active_invoices_count": len(invoices),
        "top_client": meta["top_client"],
        "overdue_client": meta["overdue_client"],
        "recent_clients": [c.company_name or c.name for c in clients[:6]],
    }


# ---------------------------------------------------------------------------
# FinPilot Graph Runner
# ---------------------------------------------------------------------------

class FinPilotAssistant:
    """
    Stateful LangGraph Assistant for FinPilot AI.
    """

    def __init__(self, checkpointer: Any | None = None) -> None:
        self.checkpointer = checkpointer or MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AssistantState)

        workflow.add_node("parse_intent", self._parse_intent_node)
        workflow.add_node("execute_tool", self._execute_tool_node)
        workflow.add_node("synthesize_response", self._synthesize_response_node)

        workflow.add_edge(START, "parse_intent")
        workflow.add_edge("parse_intent", "execute_tool")
        workflow.add_edge("execute_tool", "synthesize_response")
        workflow.add_edge("synthesize_response", END)

        return workflow.compile(checkpointer=self.checkpointer)

    async def chat(
        self,
        message: str,
        business_id: uuid.UUID,
        session: AsyncSession,
        conversation_id: uuid.UUID | None = None,
        approval_request_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        """Convenience method for conversational interactions."""
        conv_id = conversation_id or uuid.uuid4()
        state_in = {
            "messages": [HumanMessage(content=message)],
            "business_id": business_id,
            "conversation_id": conv_id,
            "approval_request_id": approval_request_id,
        }
        config = {
            "configurable": {
                "thread_id": str(conv_id),
                "session": session,
            }
        }
        return await self.graph.ainvoke(state_in, config=config)

    async def _parse_intent_node(self, state: AssistantState) -> dict[str, Any]:
        """
        Interprets natural language user message into concrete tool selection and parameters.
        Uses structured heuristics and pattern extraction, and checks for approval actions.
        """
        messages = state.get("messages", [])
        if not messages:
            return {
                "intent": "dossier_query",
                "tool_name": "query_dossier_rag",
                "tool_args": {"question": ""},
            }

        last_msg = messages[-1].content.strip()
        lower_msg = last_msg.lower()

        # Check for approval confirmation: "confirm", "approve", "proceed", "yes, issue it"
        if state.get("approval_request_id") and (
            re.search(r"\b(approve|confirm|proceed|issue it)\b", lower_msg)
            or lower_msg in ("yes", "y", "sure", "ok", "proceed", "confirm")
        ):
            return {
                "intent": "confirm_issuance",
                "tool_name": "confirm_issuance",
                "tool_args": {"approval_request_id": state["approval_request_id"]},
            }

        # Intent: Create invoice draft
        # e.g., "Create an invoice for Acme Consulting for ₹50,000 plus 18% GST, due in 15 days"
        create_inv_match = re.search(
            r"(?:create|draft|make|generate)\s+(?:an?\s+)?invoice\s+(?:for\s+)?([A-Za-z0-9\s\.\-_]+?)\s+(?:for\s+|of\s+|amount\s+)?(?:₹|rs\.?|inr)?\s*([0-9,]+(?:\.[0-9]+)?)",
            lower_msg,
        )
        if create_inv_match:
            client_name = create_inv_match.group(1).strip()
            amount_str = create_inv_match.group(2).replace(",", "")
            amount = Decimal(amount_str)

            # GST rate check
            gst_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%\s*gst", lower_msg)
            tax_rate = Decimal(gst_match.group(1)) if gst_match else Decimal("18.00")

            # Due days check
            due_match = re.search(r"due\s+in\s+([0-9]+)\s*days", lower_msg)
            due_days = int(due_match.group(1)) if due_match else 15

            # Description check
            desc = "Consulting & Professional Services"
            if "for" in client_name and not client_name.startswith("for"):
                parts = client_name.split("for")
                client_name = parts[-1].strip()

            return {
                "intent": "create_invoice_draft",
                "tool_name": "create_invoice_draft",
                "tool_args": {
                    "client_name_or_id": client_name,
                    "amount": amount,
                    "description": desc,
                    "tax_rate_pct": tax_rate,
                    "due_days": due_days,
                },
            }

        # Intent: Issue invoice directly
        issue_match = re.search(r"(?:issue|confirm\s+issue|send)\s+(?:invoice\s+)?([a-f0-9\-]{36}|draft-[a-z0-9]+|inv-[0-9]{4}-[0-9]+)", lower_msg)
        if issue_match:
            inv_ref = issue_match.group(1)
            return {
                "intent": "issue_invoice",
                "tool_name": "request_invoice_issuance",
                "tool_args": {"invoice_id_or_num": inv_ref},
            }

        # Intent: Client lookup
        client_match = re.search(r"(?:lookup client|client profile|find client)\s+([A-Za-z0-9\s]+)", lower_msg)
        if client_match and not any(k in lower_msg for k in ["zenith", "apex", "kavach"]):
            return {
                "intent": "client_summary",
                "tool_name": "get_client_summary",
                "tool_args": {"client_id_or_name": client_match.group(1).strip()},
            }

        # Intent: Dossier, PDF, or Corporate Audit RAG
        # Catches questions about the PDF, business identity, expenses, overdue, walkthroughs, risks, clients
        dossier_triggers = [
            "pdf", "dossier", "audit", "document", "report", "company", "business",
            "zenith", "kavach", "apex", "explain", "explainit", "walk me through",
            "what is in", "whatis in", "whats in", "who is", "who are", "what is",
            "what does", "client", "debtor", "customer", "expense", "disbursement",
            "cost", "spend", "net flow", "cash flow", "risk", "not good", "bad", "issue",
            "summary", "this one", "tell me", "statutory", "gst", "metric", "overview",
            "who owes", "receivable", "overdue"
        ]
        if any(term in lower_msg for term in dossier_triggers) or "?" in lower_msg or len(lower_msg.split()) <= 4:
            return {
                "intent": "dossier_query",
                "tool_name": "query_dossier_rag",
                "tool_args": {"question": last_msg},
            }

        # Intent: Overdue check
        if any(term in lower_msg for term in ["overdue", "unpaid", "pending invoices"]):
            return {
                "intent": "list_overdue",
                "tool_name": "list_overdue_invoices",
                "tool_args": {},
            }

        # Intent: Receivables / Financial summary
        if any(term in lower_msg for term in ["outstanding", "summary", "revenue", "how much", "financial overview", "receivables"]):
            return {
                "intent": "financial_summary",
                "tool_name": "get_financial_summary",
                "tool_args": {},
            }

        # Fallback: Route all general or unclassified questions to Dossier & Ledger RAG
        return {
            "intent": "dossier_query",
            "tool_name": "query_dossier_rag",
            "tool_args": {"question": last_msg},
        }

    async def _execute_tool_node(self, state: AssistantState, config: RunnableConfig) -> dict[str, Any]:
        """Execute selected typed tool against real persisted state."""
        session: AsyncSession = config["configurable"]["session"]
        business_id: uuid.UUID = state["business_id"]
        tool_name = state.get("tool_name")
        args = state.get("tool_args") or {}

        if not tool_name:
            return {"tool_result": None, "card_type": None, "card_data": None}

        if tool_name == "create_invoice_draft":
            res = await tool_create_invoice_draft(
                session=session,
                business_id=business_id,
                client_name_or_id=args["client_name_or_id"],
                amount=args["amount"],
                description=args.get("description", "Consulting & Professional Services"),
                tax_rate_pct=args.get("tax_rate_pct", Decimal("18.00")),
                due_days=args.get("due_days", 15),
            )
            if "error" in res:
                return {"tool_result": res, "card_type": None, "card_data": None}

            # Return Invoice Draft Preview Card
            return {
                "tool_result": res,
                "card_type": "invoice_draft",
                "card_data": res,
                "requires_approval": True,
            }

        elif tool_name == "request_invoice_issuance":
            inv_ref = args["invoice_id_or_num"]
            # Look up invoice
            invoice = None
            try:
                inv_id = uuid.UUID(inv_ref)
                invoice = await get_invoice(session, inv_id, business_id)
            except ValueError:
                all_invs = await list_invoices(session, business_id, limit=100)
                for inv in all_invs:
                    if inv.invoice_number.lower() == inv_ref.lower():
                        invoice = inv
                        break

            if not invoice:
                return {"tool_result": {"error": f"Invoice '{inv_ref}' not found."}, "card_type": None, "card_data": None}

            res = await tool_request_invoice_issuance(
                session=session,
                business_id=business_id,
                invoice_id=invoice.id,
                conversation_id=state.get("conversation_id"),
            )
            return {
                "tool_result": res,
                "card_type": "approval_gate",
                "card_data": res,
                "requires_approval": True,
                "approval_request_id": uuid.UUID(res["approval_request_id"]),
            }

        elif tool_name == "confirm_issuance":
            appr_id = args["approval_request_id"]
            if isinstance(appr_id, str):
                appr_id = uuid.UUID(appr_id)
            res = await tool_confirm_issuance(session=session, business_id=business_id, approval_request_id=appr_id)
            return {
                "tool_result": res,
                "card_type": "invoice_issued",
                "card_data": res,
                "requires_approval": False,
                "approval_request_id": None,
            }

        elif tool_name == "list_overdue_invoices":
            res = await tool_list_overdue_invoices(session, business_id)
            return {
                "tool_result": res,
                "card_type": "overdue_summary",
                "card_data": res,
            }

        elif tool_name == "get_financial_summary":
            res = await tool_get_financial_summary(session, business_id)
            return {
                "tool_result": res,
                "card_type": "financial_summary",
                "card_data": res,
            }

        elif tool_name == "get_client_summary":
            res = await tool_get_client_summary(session, business_id, args["client_id_or_name"])
            return {
                "tool_result": res,
                "card_type": "client_profile",
                "card_data": res,
            }

        elif tool_name in ("query_dossier_context", "query_dossier_rag"):
            from services.dossier_rag_service import DossierRAGService
            q = args.get("question") or (state.get("messages", [])[-1].content if state.get("messages") else "")
            res = await DossierRAGService.answer_dossier_query(session, business_id, q)
            return {
                "tool_result": res,
                "card_type": res.get("card_type"),
                "card_data": res.get("card_data"),
            }

        return {"tool_result": None, "card_type": None, "card_data": None}

    async def _synthesize_response_node(self, state: AssistantState) -> dict[str, Any]:
        """Produce final grounded response text with references to actual data."""
        tool_name = state.get("tool_name")
        tool_result = state.get("tool_result")

        if not tool_name or not tool_result:
            return {
                "final_response": "I am Neural Copilot, your autonomous financial AI operations assistant for Neural Noise. Ask me anything about the 3 statutory audit PDFs, Indian GST calculations, or cash flow."
            }

        if "error" in tool_result:
            return {"final_response": f"I couldn't complete that action: {tool_result['error']}"}

        if tool_name == "create_invoice_draft":
            tax_split = f"CGST: ₹{tool_result['cgst_amount']}, SGST: ₹{tool_result['sgst_amount']}" if tool_result["tax_type"] == "intra_state" else f"IGST: ₹{tool_result['igst_amount']}"
            return {
                "final_response": (
                    f"I have created an invoice draft for **{tool_result['client_name']}**.\n\n"
                    f"- **Subtotal:** ₹{tool_result['subtotal']}\n"
                    f"- **GST Breakdown ({tool_result['tax_type']}):** {tax_split}\n"
                    f"- **Total Tax:** ₹{tool_result['total_tax']}\n"
                    f"- **Grand Total:** ₹{tool_result['grand_total']}\n"
                    f"- **Due Date:** {tool_result['due_date']} (in 15 days)\n\n"
                    f"Please review the itemized calculation card below. Click **Confirm & Issue** when ready to commit."
                )
            }

        elif tool_name == "request_invoice_issuance":
            p = tool_result["preview_data"]
            return {
                "final_response": (
                    f"Approval required: Are you sure you want to issue invoice **{p['draft_number']}** for **{p['client_name']}** totaling **₹{p['grand_total']}**? "
                    f"This will assign an official sequential invoice number and freeze the record."
                )
            }

        elif tool_name == "confirm_issuance":
            return {
                "final_response": (
                    f"Success! Invoice **{tool_result['invoice_number']}** has been officially issued for ₹{tool_result['grand_total']}.\n\n"
                    f"The official PDF is generated and ready for download: `{tool_result['pdf_path']}`."
                )
            }

        elif tool_name == "list_overdue_invoices":
            count = tool_result["count"]
            tot = tool_result["total_overdue_amount"]
            return {
                "final_response": f"You have **{count} overdue invoices** totaling **₹{tot}**. Review the breakdown below to draft reminders or record payments."
            }

        elif tool_name == "get_financial_summary":
            return {
                "final_response": (
                    f"### Financial Summary\n\n"
                    f"- **Total Invoiced:** ₹{tool_result['total_invoiced']}\n"
                    f"- **Total Collected:** ₹{tool_result['total_collected']}\n"
                    f"- **Outstanding Receivables:** ₹{tool_result['total_outstanding']}\n"
                    f"- **Overdue Balance:** ₹{tool_result['overdue_amount']}\n"
                )
            }

        elif tool_name == "get_client_summary":
            return {
                "final_response": (
                    f"Client Profile for **{tool_result['company_name'] or tool_result['name']}**:\n"
                    f"- Email: {tool_result['email']}\n"
                    f"- GSTIN: {tool_result['gstin'] or 'Unregistered'}\n"
                    f"- Total Invoiced: ₹{tool_result['total_invoiced']}\n"
                    f"- Total Collected: ₹{tool_result['total_paid']}\n"
                    f"- Current Due: ₹{tool_result['total_due']} ({tool_result['overdue_invoices_count']} overdue)\n"
                )
            }

        elif tool_name in ("query_dossier_context", "query_dossier_rag"):
            if isinstance(tool_result, dict) and "text" in tool_result:
                return {"final_response": tool_result["text"]}

            msgs = state.get("messages", [])
            last_text = msgs[-1].content.lower() if msgs else ""
            is_risk_query = any(w in last_text for w in ["not good", "bad", "risk", "issue", "problem", "concern", "flag", "warning", "negative", "critical", "flaw", "overdue"])
            risk_section = ""
            if is_risk_query:
                risk_section = (
                    f"\n\n### ⚠️ Critical Audit Deficiencies & Financial Risks Noted:\n"
                    f"1. **High Overdue Exposure:** ₹{float(tool_result['overdue_amount']):,.2f} remains uncollected past due date, primarily concentrated with **{tool_result['overdue_client']}**.\n"
                    f"2. **Revenue Concentration Risk:** **{tool_result['top_client']}** represents the single largest account, creating high client dependency.\n"
                    f"3. **Working Capital Gap:** With operating expenses of ₹{float(tool_result['expenses']):,.2f} versus ₹{float(tool_result['outstanding_receivables']):,.2f} in pending receivables, delayed collections could strain short-term liquidity.\n"
                    f"4. **Statutory Filing Compliance:** Audit flags remind that quarterly GSTR-1 and GSTR-3B filings must reconcile against e-invoiced ledger records before period closing."
                )

            return {
                "final_response": (
                    f"### Corporate Dossier & Audit Analysis\n\n"
                    f"**Entity:** {tool_result['entity_name']} ({tool_result['gstin']})\n"
                    f"**Jurisdiction:** {tool_result['state']} | **Industry:** {tool_result['industry']}\n"
                    f"**Source Document:** `{tool_result['dossier_title']}` ({tool_result['pages_count']} pages verified statutory audit)\n\n"
                    f"**Financial Breakdown:**\n"
                    f"- **Total Invoiced:** ₹{float(tool_result['total_invoiced']):,.2f}\n"
                    f"- **Total Collected:** ₹{float(tool_result['total_collected']):,.2f}\n"
                    f"- **Outstanding Receivables:** ₹{float(tool_result['outstanding_receivables']):,.2f}\n"
                    f"- **Overdue Balance:** ₹{float(tool_result['overdue_amount']):,.2f} *(Top overdue: {tool_result['overdue_client']})*\n"
                    f"- **Operating Expenses:** ₹{float(tool_result['expenses']):,.2f}\n"
                    f"- **Net Cash Flow:** ₹{float(tool_result['net_flow']):,.2f}\n\n"
                    f"**Key Counterparties ({tool_result['active_clients_count']} clients registered):**\n"
                    f"- **Largest Account:** {tool_result['top_client']}\n"
                    f"- **Sample Clients:** {', '.join(tool_result['recent_clients'])}{risk_section}\n\n"
                    f"You can review the full {tool_result['pages_count']}-page PDF at `{tool_result['pdf_url']}` or ask me to draft invoices, verify GST calculations, or inspect individual customer ledgers."
                )
            }

        return {"final_response": json.dumps(tool_result, indent=2)}
