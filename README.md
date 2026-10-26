# Neural Noise

> **Build intelligent financial operations & experiences. Orchestrate AI. Measure what works.**

[![PostgreSQL 18](https://img.shields.io/badge/PostgreSQL-18.0-blue.svg)](https://www.postgresql.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15.5+-black.svg)](https://nextjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Tests Passing](https://img.shields.io/badge/Tests-17%20Passed%20(100%25)-brightgreen.svg)]()

Neural Noise is a production-grade full-stack AI agent platform engineered to demonstrate high-level technical capability across two complementary industry domains:

1. **AI Product Engineer** (*Fibr AI Focus*): AI-native website personalization, audience intent synthesis, LangGraph multi-step workflows, brand safety guardrails, comparative preview diffs, and controlled A/B experimentation with statistical hypothesis testing.
2. **Full-Stack Engineer (AI)** (*Variabl Focus*): End-to-end web architecture, PostgreSQL 18 relational persistence (39 normalized tables), typed REST APIs, deterministic Indian GST calculation engines, ReportLab PDF rendering, and double-entry client ledgers.

---

## Architecture Overview

```
                        ┌──────────────────────────────────────────────┐
                        │                IntentFlow AI                 │
                        │            Unified Web Application           │
                        └──────────────────────┬───────────────────────┘
                                               │
             ┌─────────────────────────────────┴─────────────────────────────────┐
             ▼                                                                   ▼
┌──────────────────────────────────────┐                   ┌──────────────────────────────────────┐
│  PRIMARY EXPERIENCE (75% PRIORITY)   │                   │ SECONDARY EXPERIENCE (25% PRIORITY)  │
│    AI Website Experience Studio      │                   │    AI Finance Operations Studio      │
├──────────────────────────────────────┤                   ├──────────────────────────────────────┤
│ • Safe SSRF Web Ingestion            │                   │ • Indian GST Invoicing (CGST/SGST)   │
│ • DOM Element & Intent Extraction    │                   │ • Double-Entry Client Ledgers        │
│ • LangGraph Variant Synthesis        │                   │ • Payment Allocation & Tracking      │
│ • Deterministic Brand Guardrails     │                   │ • Deterministic Runway Forecasting   │
│ • Comparative Previews & Diff        │                   │ • Human-in-the-Loop Invoice Drafting │
│ • A/B Experimentation Engine         │                   │ • Vector RAG Financial Assistant     │
│ • Two-Proportion Pooled Z-Tests      │                   │ • Audit Trail & Reconciliation       │
└──────────────────┬───────────────────┘                   └──────────────────┬───────────────────┘
                   │                                                          │
                   └───────────────────────────┬──────────────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │               Shared Platform                │
                        ├──────────────────────────────────────────────┤
                        │ • LangGraph Multi-Step StateGraphs           │
                        │ • PostgreSQL 18 ACID Persistence (39 Tables) │
                        │ • Agent Execution Tracing & Observability    │
                        │ • Automated AI Safety & Accuracy Evaluations │
                        │ • Human-in-the-Loop Approval Checkpoints     │
                        └──────────────────────────────────────────────┘
```

---

## Key Modules & Technical Implementation

### 1. Primary: AI Website Experience Studio
- **Safe Web Ingestion (`services/page_ingestion_service.py`)**: Multi-layered Server-Side Request Forgery (SSRF) defense. Hostnames are pre-resolved and filtered against blocked CIDR blocks (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, and cloud metadata `169.254.169.254`). Maximum 2MB payload streaming cap and 10s socket timeout.
- **Audience Intent Modeling**: Maps customer personas to behavioral hypotheses and value proposition vectors.
- **LangGraph Multi-Step Agent (`agents/website_optimizer_agent.py`)**: Compiles a 6-node `StateGraph`:
  `validate_request` $\to$ `ingest_page_context` $\to$ `analyze_audience_intent` $\to$ `generate_variants` $\to$ `validate_guardrails` $\to$ `prepare_approval_checkpoint`.
- **Deterministic Brand Guardrails (`services/brand_validator_service.py`)**: Substring scanning for prohibited marketing claims (e.g. "100% guaranteed ROI"), character limit boundaries (Headline $\le 85$, CTA $\le 35$), and brand compliance scoring ($0–100\%$).
- **Comparative Experience Preview**: Side-by-side comparison of Baseline Control vs AI-synthesized variants with Desktop vs Mobile (375px) responsive frames and copy diff inspection.
- **Human-in-the-Loop (HITL) Checkpoint**: Variants enter `needs_review` status; require explicit human sign-off before entering experimentation.

### 2. A/B Experimentation & Statistical Metric Engine (`services/experiment_service.py`)
- **Deterministic Traffic Allocation**: MD5 hash visitor partitioning (`MD5(experiment_id:visitor_id)`) guarantees sticky, repeatable variant assignment without stateful cookies.
- **Two-Proportion Pooled Z-Test**: Calculates standard error of difference under the null hypothesis:
  $$SE_{\text{pooled}} = \sqrt{\hat{p}(1 - \hat{p})\left(\frac{1}{n_c} + \frac{1}{n_v}\right)}$$
- **Normal CDF P-Value**: Two-sided p-value approximation without heavyweight external dependencies.
- **95% Confidence Intervals**: Exact unpooled standard error intervals for absolute lift.
- **Sample Size Warnings**: Automatically flags low-power scenarios ($n < 30$) to prevent premature stopping.
- **Synthetic Traffic Simulator**: 1-click synthetic visitor stream generator for real-time demonstrations.

### 3. Secondary: AI Finance Operations Studio
- **Deterministic Indian GST Engine (`services/invoice_service.py`)**: Python fixed-point `Decimal` arithmetic. Distinguishes intra-state (9% CGST + 9% SGST) from inter-state (18% IGST) based on two-digit state codes.
- **Double-Entry Ledgers (`services/ledger_service.py`)**: ACID transactions tracking invoices, payments, and running balances.
- **ReportLab PDF Invoices**: Generates clean, production-styled PDF invoices on demand.
- **CFO Assistant**: Interactive LangGraph assistant with tool-calling capabilities and confirmation checkpoints.

### 4. Agent Lab & Continuous AI Evaluations
- **Agent Lab & Observability**: Visualized LangGraph pipeline, node transition status, execution duration in milliseconds, and token tracking.
- **AI Evaluation Suite (`services/evaluation_service.py`)**: Automated regression tests validating:
  - Brand safety and prohibited claims interception.
  - Character boundary constraints.
  - Structured output JSON schema compliance.
  - Financial GST calculation precision.

---

## Directory Structure

```
.
├── agents/                     # LangGraph StateGraph agents
│   ├── website_optimizer_agent.py  # 6-stage website optimization agent
│   └── assistant_agent.py          # CFO financial operations assistant
├── api/                        # FastAPI application & router endpoints
│   ├── main.py                 # FastAPI application mount
│   ├── intentflow_router.py    # IntentFlow REST API endpoints (15+ routes)
│   ├── models.py               # 39 SQLAlchemy database models
│   └── database.py             # PostgreSQL async connection manager
├── services/                   # Deterministic business logic services
│   ├── page_ingestion_service.py   # SSRF filter & DOM element parser
│   ├── brand_validator_service.py  # Brand safety & character boundary checks
│   ├── experiment_service.py       # Z-test statistical inference & simulator
│   ├── evaluation_service.py       # Continuous AI regression test battery
│   ├── invoice_service.py          # Indian GST calculations & ReportLab PDF
│   └── ledger_service.py           # Double-entry ledger reconciliation
├── frontend/                   # Next.js 15 Tailwind web application
│   ├── src/app/                # App router (page.tsx, layout.tsx)
│   ├── src/components/         # IntentFlow & FinPilot UI tabs
│   │   ├── intentflow/         # Experience Studio, Experiments, Lab, Evals
│   │   └── finpilot/           # Invoices, Ledgers, Runway, CFO Assistant
│   └── src/lib/api.ts          # Typed API client interfaces & endpoints
├── docs/                       # 8 In-depth engineering specifications
│   ├── ARCHITECTURE_AUDIT.md
│   ├── PRODUCT_SPECIFICATION.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── AGENT_ARCHITECTURE.md
│   ├── EXPERIMENTATION_DESIGN.md
│   ├── SECURITY_MODEL.md
│   ├── AI_EVALUATION_PLAN.md
│   └── TEST_STRATEGY.md
└── tests/                      # 17 Automated unit & integration tests
    ├── unit/
    └── integration/
```

---

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL 18+ (running on `localhost:5432`)
- Node.js 18+ and npm

### 1. Database Setup
Ensure PostgreSQL is running and database `finpilot` exists:
```sql
CREATE DATABASE finpilot;
```

### 2. Backend Setup
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run database migrations and table creation
python -c "import asyncio; from api.database import init_db; asyncio.run(init_db())"

# Start FastAPI backend
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run build   # Production compile
npm run start   # or npm run dev
```

The IntentFlow AI workspace will be available at: `http://localhost:3000`  
The FastAPI interactive documentation is at: `http://localhost:8000/docs`

---

## Automated Test Verification

Run the complete 17-test regression suite:
```bash
pytest tests/ -v
```

Expected output:
```
tests/unit/test_brand_validator.py::... PASSED
tests/unit/test_experiment_statistics.py::... PASSED
tests/unit/test_financial_calculations.py::... PASSED
tests/unit/test_page_ingestion_and_ssrf.py::... PASSED
tests/integration/test_website_optimizer_workflow.py::... PASSED
tests/integration/test_api_endpoints.py::... PASSED
tests/integration/test_vertical_workflow.py::... PASSED

======================== 17 passed in 4.82s ========================
```

---

## Author & Credits
- **Lead Engineering & Architecture**: SAIYAM Gade ([@SAIYAMgade](https://github.com/SAIYAMgade))
- **AI Agent Development Assistance**: Claude Code (Anthropic Claude)
- **License**: Open source under the MIT License.

<!-- Repository verified: SAIYAMgade -->
