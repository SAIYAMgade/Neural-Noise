"""
dossier_rag_service.py - Gemini-powered RAG over statutory financial dossiers.
Vector search retrieves relevant PDF chunks; Gemini Flash synthesizes grounded answers.
"""

from __future__ import annotations

import os
import re
import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import Any
import pypdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.ext.asyncio import AsyncSession

from services.client_service import list_clients
from services.invoice_service import list_invoices
from services.dossier_service import DOSSIERS_METADATA

DOSSIER_FILES = {
    "apex_global": "frontend/public/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf",
    "kavach_security": "frontend/public/dossiers/Kavach_Security_Solutions_Annual_Audit_2026.pdf",
    "zenith_digital": "frontend/public/dossiers/Zenith_Digital_Media_Q3_Financial_Review.pdf",
}

# Lazy-init Gemini client
_gemini_model = None

def _get_gemini_model():
    global _gemini_model
    if _gemini_model is None:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set in environment")
        genai.configure(api_key=api_key)
        # Try preferred modern models
        for m_name in ["gemini-3.8-flash", "gemini-flash-latest", "gemini-2.0-flash", "gemini-1.5-flash"]:
            try:
                _gemini_model = genai.GenerativeModel(
                    m_name,
                    generation_config={"temperature": 0.2, "max_output_tokens": 400},
                )
                break
            except Exception:
                continue
    return _gemini_model


SYSTEM_PROMPT = """You are Neural Copilot, the autonomous financial AI assistant for the Neural Noise platform.

RULES — follow every one strictly:
1. Answer in 2–5 lines. Never wall-of-text.
2. Ground every financial fact in the CONTEXT below. If the context doesn't cover the question, say so honestly in one line.
3. Never hallucinate numbers, names, or dates. If unsure, say "I don't have that information in the current ledger."
4. For general questions (date, greetings, nonsense input, off-topic), answer naturally and briefly — don't dump financial data.
5. Use ₹ for Indian Rupees. Format large numbers with commas (₹29,26,400).
6. Refer to yourself as "Neural Copilot" — never "FinPilot".
7. When the user says "this pdf" or "that pdf" or just "pdf", refer to whichever dossier is currently active in the database context.
8. For very short or unclear messages (single letters, gibberish), politely ask for clarification.

Today's date: {today}
"""


def _generate_smart_fallback(
    query: str,
    meta: dict[str, Any],
    total_invoiced: Decimal,
    total_collected: Decimal,
    total_due: Decimal,
    overdue_sum: Decimal,
    overdue_invoices: list,
    clients: list,
    today: date,
    top_chunks: list[dict[str, Any]],
) -> str:
    """Intelligent, deterministic, zero-hallucination fallback answering engine."""
    q = query.lower().strip()

    # 1. Very short, greetings, or gibberish
    if len(q) <= 2 or q in ("ok", "okay", "k", "ca", "hi", "hello", "hey", "test", "help"):
        return (
            f"Hello! I am Neural Copilot. Currently viewing **{meta['name']}**.\n"
            "Ask me about statutory audit figures, overdue receivables, GST splits, or compare any of the 3 available corporate dossiers."
        )

    # 2. Date queries
    if any(k in q for k in ["date today", "what is the date", "today's date", "current date", "what date"]):
        return f"Today is {today.strftime('%A, %d %B %Y')}. Active financial reporting period is FY 2025–26."

    # 3. Dossier 1 / Apex Global
    if re.search(r"\b(?:pdf\s*1|pdf\s*one|first\s*pdf|dossier\s*1)\b", q):
        d = DOSSIERS_METADATA["apex_global"]
        return (
            f"**PDF 1 — {d['name']}** ({d['pages_count']} pages · {d['state']}):\n"
            f"Gross Invoiced: ₹{d['total_invoiced']:,.2f} | Realized: ₹{d['total_collected']:,.2f} | "
            f"Net Surplus: ₹{d['net_flow']:,.2f} | Pending Receivables: ₹{d['receivables']:,.2f}."
        )

    # 4. Dossier 2 / Kavach Security
    if re.search(r"\b(?:pdf\s*2|pdf\s*two|second\s*pdf|dossier\s*2)\b", q):
        d = DOSSIERS_METADATA["kavach_security"]
        return (
            f"**PDF 2 — {d['name']}** ({d['pages_count']} pages · {d['state']}):\n"
            f"Gross Invoiced: ₹{d['total_invoiced']:,.2f} | Realized: ₹{d['total_collected']:,.2f} | "
            f"Net Surplus: ₹{d['net_flow']:,.2f} | Pending Receivables: ₹{d['receivables']:,.2f}."
        )

    # 5. Dossier 3 / Zenith Digital
    if re.search(r"\b(?:pdf\s*3|pdf\s*three|third\s*pdf|dossier\s*3)\b", q):
        d = DOSSIERS_METADATA["zenith_digital"]
        return (
            f"**PDF 3 — {d['name']}** ({d['pages_count']} pages · {d['state']}):\n"
            f"Gross Invoiced: ₹{d['total_invoiced']:,.2f} | Realized: ₹{d['total_collected']:,.2f} | "
            f"Net Surplus: ₹{d['net_flow']:,.2f} | Pending Receivables: ₹{d['receivables']:,.2f}."
        )

    # 6. List all 3 dossiers
    if any(k in q for k in ["three pdfs", "3 pdfs", "list pdfs", "all pdfs", "what pdfs", "which pdfs", "available pdfs"]):
        lines = [
            "Here are the 3 indexed statutory dossiers:",
            "• **PDF 1: Apex Global Technologies Pvt Ltd** (24 pages, Bengaluru) — Invoiced: ₹29.26L, Surplus: ₹10.10L",
            "• **PDF 2: Kavach Security Solutions Pvt Ltd** (25 pages, Hyderabad) — Invoiced: ₹45.43L, Surplus: ₹14.80L",
            "• **PDF 3: Zenith Digital Media Pvt Ltd** (22 pages, Mumbai) — Invoiced: ₹18.95L, Surplus: ₹6.85L",
        ]
        return "\n".join(lines)

    # 7. What is this/that pdf / Dossier explanation
    if any(k in q for k in ["what is that pdf", "what is this pdf", "what is the pdf", "explain pdf", "about this pdf", "dossier about"]):
        return (
            f"The active dossier is **{meta['name']}** ({meta['subtitle']}, {meta['pages_count']} pages).\n"
            f"It reconciles gross invoiced revenue of ₹{total_invoiced:,.2f}, realized collections of ₹{total_collected:,.2f}, "
            f"and a certified net liquid surplus of ₹{float(meta['net_flow']):,.2f}."
        )

    # 8. Loss / Profit / Financial health
    if any(k in q for k in ["loss", "what is the loss", "any loss", "profit", "surplus"]):
        surplus_val = float(meta['net_flow'])
        if surplus_val >= 0:
            return (
                f"**{meta['name']}** reported no statutory net loss for this period.\n"
                f"The business generated a net liquid surplus of ₹{surplus_val:,.2f} against ₹{float(meta['expenses']):,.2f} in operating expenses, "
                f"with ₹{total_due:,.2f} remaining in outstanding receivables."
            )
        else:
            return f"**{meta['name']}** reflects an operating deficit of ₹{abs(surplus_val):,.2f}."

    # 9. Receivables / Who owes money / Overdue
    if any(k in q for k in ["who owes", "owes money", "overdue", "pending payment", "unpaid", "receivables", "debtor"]):
        if overdue_invoices:
            top_overdue = meta.get("overdue_client", "Primary debtor")
            return (
                f"Outstanding receivables stand at ₹{total_due:,.2f}, with ₹{overdue_sum:,.2f} critically overdue ({len(overdue_invoices)} invoices).\n"
                f"The primary pending debtor is **{top_overdue}**."
            )
        return f"Outstanding receivables stand at ₹{total_due:,.2f} across current active clients. No overdue alerts recorded."

    # 10. GST / Tax compliance
    if any(k in q for k in ["gst", "tax", "igst", "cgst", "sgst", "hsn", "sac"]):
        return (
            f"GST reconciliation for **{meta['name']}** (GSTIN: {meta['gstin']}):\n"
            f"All invoices comply with 18% GST (CGST 9% + SGST 9% intra-state or IGST 18% inter-state) mapped to SAC codes 998311 and 998313."
        )

    # 11. Revenue / Collections
    if any(k in q for k in ["revenue", "invoiced", "collection", "how much billed", "billed"]):
        return (
            f"**{meta['name']} Revenue Summary:**\n"
            f"Total Gross Invoiced: ₹{total_invoiced:,.2f} | Total Collected: ₹{total_collected:,.2f} | Outstanding: ₹{total_due:,.2f}."
        )

    # 12. If chunks matched well from TF-IDF, extract the most relevant sentence
    if top_chunks:
        best_chunk = top_chunks[0]
        # Clean text
        raw_text = best_chunk["text"].replace("\n", " ").strip()
        # Find sentence containing query terms
        words = [w for w in q.split() if len(w) > 3]
        sentences = [s.strip() for s in raw_text.split(".") if s.strip()]
        matched_sentences = [s for s in sentences if any(w in s.lower() for w in words)]
        if matched_sentences:
            return f"From {meta['name']} (Page {best_chunk['page']}):\n" + ". ".join(matched_sentences[:2]) + "."
        else:
            return f"From {meta['name']} ({best_chunk['section']}, Page {best_chunk['page']}):\n{raw_text[:280]}..."

    # Fallback
    return (
        f"**{meta['name']}** — Invoiced: ₹{total_invoiced:,.2f}, Collected: ₹{total_collected:,.2f}, Surplus: ₹{float(meta['net_flow']):,.2f}.\n"
        f"Let me know if you would like details on GST, overdue debtors, or specific ledger schedules."
    )


class DossierRAGService:
    _index_cache: dict[str, dict[str, Any]] = {}

    @classmethod
    def get_or_build_index(cls, dossier_id: str) -> dict[str, Any]:
        if dossier_id in cls._index_cache:
            return cls._index_cache[dossier_id]

        file_path = DOSSIER_FILES.get(dossier_id)
        if not file_path or not os.path.exists(file_path):
            return {"chunks": [], "vectorizer": None, "tfidf": None}

        chunks = []
        try:
            reader = pypdf.PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = (page.extract_text() or "").strip()
                if not text:
                    continue
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                sec_title = lines[0] if lines else f"Page {page_idx + 1}"
                if len(sec_title) > 60:
                    sec_title = sec_title[:60] + "..."
                chunks.append({"page": page_idx + 1, "section": sec_title, "text": text})

            if chunks:
                vec = TfidfVectorizer(ngram_range=(1, 3), stop_words="english", sublinear_tf=True)
                tfidf_mat = vec.fit_transform([c["text"] for c in chunks])
            else:
                vec, tfidf_mat = None, None

            index_obj = {"chunks": chunks, "vectorizer": vec, "tfidf": tfidf_mat, "pages_count": len(chunks)}
            cls._index_cache[dossier_id] = index_obj
            return index_obj
        except Exception as e:
            print(f"Failed to build RAG index for {dossier_id}: {e}")
            return {"chunks": [], "vectorizer": None, "tfidf": None}

    @classmethod
    def search_chunks(cls, dossier_id: str, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        index = cls.get_or_build_index(dossier_id)
        chunks = index["chunks"]
        vec = index["vectorizer"]
        tfidf = index["tfidf"]
        if not chunks or vec is None or tfidf is None:
            return []

        q_vec = vec.transform([query])
        sims = cosine_similarity(q_vec, tfidf).flatten()
        scored = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)
        return [chunks[idx] for idx, _ in scored[:top_k]]

    @classmethod
    def _detect_dossier_id(cls, q_lower: str, clients: list) -> str:
        """Detect which corporate dossier the query is about."""
        if re.search(r"\b(?:pdf\s*1|pdf\s*one|first\s*pdf|dossier\s*1)\b", q_lower) or "apex" in q_lower:
            return "apex_global"
        if re.search(r"\b(?:pdf\s*2|pdf\s*two|second\s*pdf|dossier\s*2)\b", q_lower) or "kavach" in q_lower:
            return "kavach_security"
        if re.search(r"\b(?:pdf\s*3|pdf\s*three|third\s*pdf|dossier\s*3)\b", q_lower) or "zenith" in q_lower:
            return "zenith_digital"
        # Infer from active database clients
        cnames = [c.company_name or c.name for c in clients]
        if any("Defense" in n or "CyberShield" in n or "HDFC" in n for n in cnames):
            return "kavach_security"
        if any("Nykaa" in n or "Swiggy" in n or "Cult.fit" in n for n in cnames):
            return "zenith_digital"
        return "apex_global"

    @classmethod
    async def answer_dossier_query(
        cls,
        session: AsyncSession,
        business_id: uuid.UUID,
        query: str,
        conversation_context: list[str] | None = None
    ) -> dict[str, Any]:
        """Use Gemini Flash to answer any question, grounded in database + PDF chunks."""
        q_lower = query.lower().strip()

        # --- Gather grounding context ---
        clients = await list_clients(session, business_id, limit=20)
        invoices = await list_invoices(session, business_id, limit=50)

        dossier_id = cls._detect_dossier_id(q_lower, clients)
        meta = DOSSIERS_METADATA.get(dossier_id, DOSSIERS_METADATA["apex_global"])

        total_invoiced = sum((inv.grand_total for inv in invoices if inv.status != "cancelled"), Decimal("0.00"))
        total_collected = sum((inv.amount_paid for inv in invoices if inv.status != "cancelled"), Decimal("0.00"))
        total_due = sum((inv.amount_due for inv in invoices if inv.status != "cancelled"), Decimal("0.00"))
        today = date.today()
        overdue_invoices = [inv for inv in invoices if inv.status in ("issued", "partially_paid", "overdue") and inv.due_date < today]
        overdue_sum = sum((inv.amount_due for inv in overdue_invoices), Decimal("0.00"))

        # Check if query is about all PDFs
        is_all_pdfs = any(k in q_lower for k in [
            "three pdfs", "3 pdfs", "list pdfs", "all pdfs", "what pdfs", "which pdfs",
            "available pdfs", "how many pdfs", "list dossiers"
        ])

        # Vector search for relevant chunks (skip for very short / off-topic queries)
        chunks_text = ""
        if len(q_lower) > 2:
            top_chunks = cls.search_chunks(dossier_id, query, top_k=3)
            if top_chunks:
                chunks_text = "\n\n".join(
                    f"[Page {c['page']}: {c['section']}]\n{c['text'][:500]}"
                    for c in top_chunks
                )

        # Build all-dossiers summary for context
        all_dossiers_summary = "\n".join(
            f"- PDF {i+1}: {d['name']} ({d['pages_count']} pages, {d['state']}, {d['industry']}, "
            f"GSTIN: {d['gstin']}, Invoiced: ₹{d['total_invoiced']:,.2f}, Collected: ₹{d['total_collected']:,.2f}, "
            f"Surplus: ₹{d['net_flow']:,.2f}, Top Client: {d['top_client']}, Overdue: {d['overdue_client']})"
            for i, d in enumerate(DOSSIERS_METADATA.values())
        )

        # Active ledger state
        client_names = [c.company_name or c.name for c in clients[:10]]
        overdue_names = [
            f"{inv.client.company_name or inv.client.name}: ₹{inv.amount_due}"
            for inv in overdue_invoices[:5]
            if inv.client
        ]

        context_block = f"""=== ACTIVE DOSSIER (currently loaded in database) ===
Entity: {meta['name']}
Industry: {meta['industry']}
State: {meta['state']}
GSTIN: {meta['gstin']}
Dossier: {meta['subtitle']} ({meta['pages_count']} pages)
PDF URL: {meta['pdf_url']}

=== LIVE DATABASE STATE ===
Total Invoiced: ₹{total_invoiced:,.2f}
Total Collected: ₹{total_collected:,.2f}
Outstanding Receivables: ₹{total_due:,.2f}
Overdue Balance: ₹{overdue_sum:,.2f} ({len(overdue_invoices)} invoices past due)
Operating Expenses: ₹{float(meta['expenses']):,.2f}
Net Liquid Surplus: ₹{float(meta['net_flow']):,.2f}
Active Clients ({len(clients)}): {', '.join(client_names)}
Top Client: {meta['top_client']}
Top Overdue Debtor: {meta['overdue_client']}
{('Overdue Details: ' + '; '.join(overdue_names)) if overdue_names else ''}

=== ALL 3 AVAILABLE DOSSIERS ===
{all_dossiers_summary}

=== RELEVANT PDF EXCERPTS (from vector search) ===
{chunks_text if chunks_text else '(No relevant excerpts for this query)'}
"""

        # --- Call Gemini ---
        system = SYSTEM_PROMPT.format(today=today.strftime("%d %B %Y"))
        prompt = f"{system}\n\nCONTEXT:\n{context_block}\n\nUSER QUESTION: {query}\n\nYour concise response:"

        try:
            model = _get_gemini_model()
            response = model.generate_content(prompt)
            response_text = response.text.strip()
        except Exception as e:
            # Intelligent fallback engine
            response_text = _generate_smart_fallback(
                query=query,
                meta=meta,
                total_invoiced=total_invoiced,
                total_collected=total_collected,
                total_due=total_due,
                overdue_sum=overdue_sum,
                overdue_invoices=overdue_invoices,
                clients=clients,
                today=today,
                top_chunks=top_chunks if len(q_lower) > 2 else [],
            )

        # Decide whether to show the dossier summary card
        show_card = any(term in q_lower for term in [
            "explain", "summary", "walk me through", "what is in", "about the pdf",
            "pdf summary", "dossier summary", "break down"
        ]) and not is_all_pdfs

        card_data = {
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
            "top_client": meta["top_client"],
            "overdue_client": meta["overdue_client"],
        }

        return {
            "text": response_text,
            "card_type": "dossier_summary" if show_card else None,
            "card_data": card_data if show_card else None,
        }
