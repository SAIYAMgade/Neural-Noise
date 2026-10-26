# FinPilot AI — Recruiter & Technical Interview Demonstration Guide

## 1. Executive Summary

**FinPilot AI** ("Your business finances, connected. Your AI assistant, in control.") is an end-to-end, production-style AI financial operations platform designed for Indian freelancers, consultants, independent professionals, creators, and SMBs.

The platform demonstrates how to build production AI applications where **deterministic business rules and transactional databases maintain accurate financial records**, while **stateful AI agents (LangGraph) safely interpret intent, execute typed tools, and require explicit human-in-the-loop confirmation** before executing irreversible financial actions.

Derived and elevated from the open-source foundation `SAIYAMgade/Neural-Noise`, FinPilot AI retains the full suite of multi-agent deep analytics (Monte Carlo runway simulations, IsolationForest anomaly detection, scenario forecasting) while introducing an enterprise-grade financial ledger, Indian GST tax engine, sequential invoice numbering, payment allocation, and MCP server.

---

## 2. Technical Capabilities Demonstrated

| Domain | Engineering Implementation |
|---|---|
| **Deterministic Financial Engine** | Python `Decimal` arithmetic with `ROUND_HALF_UP` to prevent IEEE 754 floating-point errors. Syntactic 15-char Indian GSTIN validation (2-digit state code + 10 PAN chars + entity + 'Z' + checksum). Automatic routing of Intra-state (CGST 50% + SGST 50%) vs Inter-state (IGST 100%). |
| **Relational Database & Integrity** | PostgreSQL 18 with 30 tables, `asyncpg` + SQLAlchemy 2.0 ORM. Strict foreign keys, `CheckConstraint` on monetary balances, monotonic sequential invoice numbering (`INV-YYYY-NNNN`) with PostgreSQL `SELECT FOR UPDATE` transaction locking. |
| **AI Agent Orchestration** | LangGraph state graph (`parse_intent` &rarr; `execute_tool` &rarr; `synthesize_response`). Typed tools for invoice drafting, overdue querying, and financial summarization. |
| **Human-in-the-Loop (HITL) Safeguards** | The AI assistant cannot issue invoices or move money unilaterally. It generates a structured draft preview and halts at an `approval_gate`. The user must review and click "Approve & Officially Issue" to commit the state transition. |
| **Idempotency & Audit Logging** | Idempotency keys (`idempotency_key`) prevent duplicate invoice issuance or payment recording on network retries. Every action writes an immutable event to the `audit_events` ledger table. |
| **Branded Document Generation** | Deterministic ReportLab PDF generator rendering Indian GST tax invoices with business details, client details, HSN/SAC line items, tax splits, and bank/UPI payment instructions. |
| **Model Context Protocol (MCP)** | Native MCP server (`services/mcp_server.py`) exposing typed financial tools to Claude Desktop, Cursor, or external IDEs. |
| **Full-Stack Architecture** | Next.js 15 (App Router, React 19, TypeScript, Tailwind CSS) frontend with responsive tabs, real-time WebSocket progress streaming, and zero compilation warnings. |

---

## 3. Quick Start & Prerequisites

### Prerequisites
- Python 3.11+ (tested on Python 3.14.7)
- Node.js 18+ (tested on Node.js 22)
- PostgreSQL running locally on port `5432` (`finpilot` database)

### Backend Launch
```bash
# Activate virtual environment
.venv\Scripts\activate

# Launch FastAPI application
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at: `http://localhost:8000/docs`

### Frontend Launch
```bash
cd frontend
npm run dev
```
Frontend will be live at: `http://localhost:3000`

---

## 4. End-to-End Recruiter Walk-Through Script

Follow this 5-minute walkthrough during a live technical screen or system architecture review.

### Step 1: System Overview & Live PostgreSQL Health Check
1. Open `http://localhost:3000`.
2. Point out the top header:
   - Green status pill: **PostgreSQL 18 API Online**.
   - Engineering badge: **ACID · Decimal Math · LangGraph HITL**.
3. Point out the Overview metric cards:
   - Total Invoiced, Collected, Receivables, Overdue, Expenses, Net Flow.
   - The live **Immutable Audit Log** at the bottom displaying past transaction events.

---

### Step 2: Conversational AI Invoice Creation (Deterministic Invoicing)
1. Navigate to the **FinPilot Assistant** tab.
2. Click on the first suggestion chip or type:
   > *"Create an invoice for Acme Consulting for ₹50,000 plus 18% GST, due in 15 days."*
3. **What to highlight to the interviewer**:
   - The AI identifies the client (`Acme Consulting`), fetches their state code from PostgreSQL (`27 - Maharashtra`), compares it with the business state (`27 - Maharashtra`), and deterministically recognizes this as an **Intra-State transaction**.
   - The calculation is **NOT** performed by the LLM prompt. The agent calls the backend tool `calculate_invoice_totals`, which uses Python `Decimal` math:
     - Subtotal: ₹50,000.00
     - CGST (9%): ₹4,500.00
     - SGST (9%): ₹4,500.00
     - Total Amount: ₹59,000.00
   - The assistant outputs an **Invoice Draft Preview Card** and halts at a **Human-in-the-Loop Confirmation Gate**.

---

### Step 3: Human-in-the-Loop Confirmation Gate & PDF Generation
1. In the chat card, point out the green button: **"Approve & Officially Issue Invoice"**.
2. Click the button.
3. **What to highlight to the interviewer**:
   - The frontend triggers `POST /api/v1/assistant/approve` with the `approval_request_id`.
   - The backend runs a PostgreSQL transaction:
     - Promotes the status from `draft` to `issued`.
     - Allocates the next monotonic sequential number (e.g. `INV-2026-0001`) using row-level locking.
     - Commits tax liability and records an immutable audit event (`invoice_issued`).
   - An **Official Invoice Issued** card appears in the chat with a direct link: **"Download Branded Indian GST PDF"**.
4. Click the download link or navigate to `/api/v1/invoices/<id>/pdf` to show the clean ReportLab invoice with GSTIN headers and tax breakdowns.

---

### Step 4: Client Ledgers & GSTIN Validation
1. Click the **Clients** tab.
2. Search for `Acme Consulting` and click **View Ledger**.
3. Show the real-time client ledger displaying:
   - Total lifetime invoiced
   - Total paid
   - Outstanding balance
   - History of all invoices with status pills
4. Click **Add Client**:
   - Show how entering a GSTIN like `29ABCDE1234F1Z5` automatically parses state code `29` (Karnataka) and enforces the 15-character statutory format.

---

### Step 5: Inbound Payment Recording & Automated Allocation
1. Click the **Payments** tab.
2. Click **Record Payment**.
3. Select `Acme Consulting`, enter Amount `₹59,000.00`, Method `UPI`, and select the issued invoice in the **Directly Allocate to Invoice** dropdown.
4. Click **Record Payment**.
5. **What to highlight**:
   - The backend assigns a sequential payment number `PAY-2026-0001`.
   - The payment allocation service creates a `PaymentAllocation` record.
   - The invoice balance due decrements from `₹59,000.00` to `₹0.00`, and its status automatically flips to **paid**.
   - Navigate back to the **Invoices** tab to confirm the invoice is now marked `paid` with `₹0.00` balance due.

---

### Step 6: Querying Overdue Invoices with Conversational AI
1. Return to the **FinPilot Assistant** tab.
2. Type or click:
   > *"Which invoices are currently overdue and what is the balance?"*
3. The LangGraph agent executes `query_overdue_invoices`, queries PostgreSQL, and renders an interactive **Overdue Receivables Summary** card listing overdue clients, days past due, and total overdue liability.

---

### Step 7: Deep Analytics, Runway Simulations & Anomaly Detection
1. Click the **Deep Analytics** tab.
2. Point out that the legacy data science pipeline from `SAIYAMgade/Neural-Noise` is fully preserved:
   - **Monte Carlo Survival Simulations** (1,000+ stochastic iterations predicting cash runway).
   - **IsolationForest Anomaly AI** (unsupervised transaction anomaly detection).
   - **Bear / Base / Bull scenario models**.
3. Click **"Launch Interactive Demo Pipeline"**:
   - The system initiates `/demo/async` and navigates to `/run/[runId]`, where live WebSocket events stream each agent step into the dashboard.

---

### Step 8: Immutable Audit Verification
1. Return to the **Overview** tab.
2. Inspect the **Immutable Audit Log & Financial Ledger Events**:
   - Note the entries: `client_created`, `invoice_draft_created`, `approval_executed`, `invoice_issued`, `payment_recorded`, `payment_allocated`.
   - Explain how this guarantees auditability, SOC-2 readiness, and zero untracked database modifications.

---

## 5. Automated Verification & Testing Commands

To run the automated verification suite:

```bash
# Run all backend unit & integration tests
.venv\Scripts\python.exe -m pytest

# Run frontend production build
npm run build --prefix frontend
```

All 8 tests pass with 100% green status across unit calculation formulas, integration lifecycles, and FastAPI endpoints.
