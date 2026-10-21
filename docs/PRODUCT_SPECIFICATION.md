# IntentFlow AI — Product Specification

## 1. Product Identity & Vision

**Product Name**: IntentFlow AI  
**Tagline**: *Build intelligent experiences. Orchestrate AI. Measure what works.*  
**Target Roles**:
- **Fibr AI — AI Product Engineer**: AI-native website experience personalization, audience intent synthesis, LangGraph agent workflows, brand guardrails, and A/B statistical experimentation.
- **Variabl — Full-Stack Engineer (AI)**: Full-stack Next.js/FastAPI product architecture, PostgreSQL 18 persistence, typed APIs, ReportLab PDF generation, and deterministic Indian financial operations.

---

## 2. Platform Architecture: Two Connected Experiences

IntentFlow AI pairs a high-impact website optimization engine with a precision financial operations studio, sharing a unified platform core (LangGraph orchestration, tool execution, PostgreSQL persistence, and observability).

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
                        │ • PostgreSQL 18 ACID Persistence             │
                        │ • Agent Execution Tracing & Observability    │
                        │ • Automated AI Safety & Accuracy Evaluations │
                        │ • Human-in-the-Loop Approval Checkpoints     │
                        └──────────────────────────────────────────────┘
```

---

## 3. Primary Experience: AI Website Experience Studio

### 3.1 Safe Page Ingestion & Component Extraction
- Accepts target URLs or manual HTML paste.
- Blocks SSRF attacks by resolving DNS and filtering against private/reserved IP subnets (including AWS/GCP metadata `169.254.169.254`).
- Parses DOM into structured components: Page Title, Meta Description, H1 Headline, Subheadings, Primary CTA, Value Propositions, Trust Badges, and Social Proof.

### 3.2 Audience Intent & Behavioral Hypotheses
- Configures target buyer personas (e.g. Enterprise Security Architect, Cost-Conscious Startup Founder).
- Formulates behavioral conversion hypotheses to guide LLM reasoning.

### 3.3 LangGraph Optimization Pipeline
- Compiles a 6-stage StateGraph:
  1. `validate_request`
  2. `ingest_page_context`
  3. `analyze_audience_intent`
  4. `generate_variants`
  5. `validate_guardrails`
  6. `prepare_approval_checkpoint`

### 3.4 Brand Guardrails & Quality Scoring
- Deterministically scans candidate copy for banned phrases (e.g. "100% guaranteed ROI", "risk-free guarantee").
- Validates headline ($\le 85$ chars) and CTA ($\le 35$ chars) length boundaries.
- Assigns a 0–100% Brand Compliance Score.

### 3.5 Comparative Experience Preview
- Visualizes Control vs Variant A vs Variant B side-by-side.
- Desktop and Mobile (375px) responsive viewport toggling.
- Content diff inspector showing character counts and copy changes.

### 3.6 Controlled A/B Experimentation & Statistical Engine
- Deterministic MD5 hash partitioning assigns visitors to variants repeatably without cross-device cookie sync requirements.
- Real-time calculation of:
  - Conversion rates (CR %)
  - Absolute lift ($\hat{p}_v - \hat{p}_c$)
  - Relative lift %
  - Two-proportion pooled z-score
  - Two-sided p-value via normal CDF approximation
  - 95% Confidence Interval
  - Sample size warnings ($n < 30$) to prevent premature stopping.

### 3.7 Synthetic Traffic Simulator
- Generates realistic binomial visitor streams on demand to demonstrate live metrics updating and statistical significance convergence.

---

## 4. Secondary Experience: AI Finance Operations Studio

- **Indian GST Engine**: Calculates intra-state (CGST 9% + SGST 9%) vs inter-state (IGST 18%) taxes deterministically using Python `Decimal`.
- **Client Ledgers**: Double-entry style running balances tracking billed vs received amounts.
- **Invoice Generation**: Automated ReportLab PDF generation with clean corporate styling.
- **CFO Assistant**: LangGraph agent that answers financial queries, creates draft invoices, and halts at approval checkpoints before persisting state changes.
