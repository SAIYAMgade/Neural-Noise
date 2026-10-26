# IntentFlow AI — Full-Stack Implementation Plan & Execution Milestones

## 1. Architectural Phases & Deliverables

```
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Database Schema & Migration (PostgreSQL 18 - 39 Tables)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 2: Security & Guardrails (SSRF Filter & Brand Validator)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 3: LangGraph Multi-Step Orchestration (WebsiteOptimizerAgent)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 4: A/B Experimentation & Statistical Inference Engine            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 5: Continuous AI Evaluations & Observability Tracing             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 6: IntentFlow Web Experience Studio UI (Next.js 15)              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 7: Verification & Testing Battery (100% Green Assertions)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Phase-by-Phase Execution Details

### Phase 1: PostgreSQL 18 Database Architecture
- Engineered 9 primary IntentFlow entities in `api/models.py`:
  - `WebsiteProject`, `PageSnapshot`, `AudienceSegment`, `ExperienceVariant`, `Experiment`, `ExperimentAssignment`, `ExperimentEvent`, `AgentExecutionTrace`, `EvaluationRun`.
- Retained and normalized all 30 financial operations models (Invoices, Clients, Payments, Ledgers, Expenses, Audit Events).
- Verified relational foreign key integrity, cascade deletion, and indexing.

### Phase 2: Security, SSRF Defenses & Brand Guardrails
- Implemented `services/page_ingestion_service.py` with multi-layered SSRF filtering:
  - Protocol whitelist (`http`, `https`).
  - Pre-request DNS resolution with IP evaluation against blocked private CIDR blocks (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `169.254.169.254`).
  - Streaming payload buffer limit of 2MB and 10s socket timeout.
  - DOM semantic extraction of Title, Headings, Value Proposition, CTAs, and Trust Badges.
- Implemented `services/brand_validator_service.py`:
  - Prohibited claims interception (e.g., "100% guaranteed ROI").
  - Copy character boundaries (Headline $\le 85$, CTA $\le 35$).
  - Brand compliance scoring ($0–100\%$).

### Phase 3: LangGraph Agent Workflows
- Built `agents/website_optimizer_agent.py` using compiled `StateGraph`:
  - 6-step state machine: `validate_request` $\to$ `ingest_page_context` $\to$ `analyze_audience_intent` $\to$ `generate_variants` $\to$ `validate_guardrails` $\to$ `prepare_approval_checkpoint`.
  - State persistence in PostgreSQL.
  - Human-in-the-Loop approval gate requiring user sign-off before variant eligibility in experiments.

### Phase 4: A/B Experimentation & Statistical Inference Engine
- Built `services/experiment_service.py`:
  - Deterministic MD5 hash visitor allocation (`MD5(experiment_id:visitor_id)`).
  - Event ingestion for exposures, CTA clicks, and conversions.
  - Two-proportion pooled z-tests, normal CDF p-values, 95% confidence intervals, and low-sample guards ($n < 30$).
  - Synthetic binomial traffic simulator for real-time demonstrations.

### Phase 5: Continuous AI Evaluations & Observability
- Built `services/evaluation_service.py`:
  - Automated test cases covering brand safety, character bounds, JSON schema compliance, and financial GST decimal math.
  - Trace logging capturing node latencies, steps, and token counts.

### Phase 6: Next.js 15 Full-Stack UI
- Engineered responsive React workspace in `frontend/src/components/intentflow/`:
  - `OverviewTab`: Executive KPIs, live experiments, recent traces.
  - `ExperienceStudioTab`: Safe URL ingestion, DOM extraction, audience targeting, LangGraph generation, comparative Desktop/Mobile preview with copy diff, brand guardrail card, and HITL action bar.
  - `ExperimentsTab`: A/B experiment metrics, statistical significance breakdown, and 1-click synthetic traffic simulator.
  - `AgentLabTab`: Visualized LangGraph pipeline, step timeline, and raw trace inspector.
  - `EvaluationsTab`: AI regression evaluation runner and test case breakdown.
  - `FinanceTab`: Seamless embedding of AI Finance Operations Studio (Invoices, Ledgers, GST, Runway, CFO Assistant).

### Phase 7: Verification & Testing
- 17 unit and integration tests passing (100% green).
- Clean Next.js 15 production build with zero TypeScript errors.
