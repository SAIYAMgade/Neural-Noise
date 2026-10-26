# IntentFlow AI — Agent Architecture & LangGraph Orchestration

## 1. System Overview
IntentFlow AI coordinates autonomous agent execution through compiled **LangGraph StateGraphs**, ensuring all non-deterministic generative actions are bounded by deterministic checkpoints, type-safe tools, and human-in-the-loop (HITL) approval gates.

Both the primary experience (**AI Website Experience Studio**) and the secondary experience (**AI Financial Operations Studio**) share this foundational agent infrastructure.

---

## 2. Website Optimizer Agent Workflow

### 2.1 State Graph Topology
```
[Start]
   │
   ▼
1. validate_request
   │ (Validates Project, Snapshot, and Target Audience in DB)
   ▼
2. ingest_page_context
   │ (Checks SSRF clean status, extracts DOM elements: Title, H1, CTA, Badges)
   ▼
3. analyze_audience_intent
   │ (Formulates conversion hypotheses and value-proposition alignment)
   ▼
4. generate_variants
   │ (Synthesizes tailored headlines, subheadings, and CTAs)
   ▼
5. validate_guardrails
   │ (Deterministic inspection for prohibited claims, character lengths, brand score)
   ▼
6. prepare_approval_checkpoint
   │ (Persists variants with status="needs_review" & records execution trace)
   ▼
[Human-in-the-Loop Review] ──(Approved)──► [A/B Experimentation Engine]
```

### 2.2 Node Responsibilities & Determinism

| Stage | Node Function | Nature | Deterministic Logic / Fallback |
| :--- | :--- | :--- | :--- |
| **1** | `validate_request` | Deterministic | Queries PostgreSQL for project and snapshot existence. Fails fast with descriptive error if records are missing. |
| **2** | `ingest_page_context` | Deterministic | Validates snapshot content hash and ensures URL passed SSRF IP filtering. Fallback loads pre-parsed DOM elements. |
| **3** | `analyze_audience_intent` | Generative / Structured | Formulates audience-specific optimization hypotheses based on buyer persona. |
| **4** | `generate_variants` | Generative / Structured | Generates tailored copy variants. Fallback generates structured enterprise copy if external LLM times out. |
| **5** | `validate_guardrails` | Deterministic | Evaluates variants against project brand rules using `BrandValidatorService`. Strips banned claims and scores adherence. |
| **6** | `prepare_approval_checkpoint` | Deterministic | Commits variants to DB with `review_status="needs_review"`, updates trace latency, and awaits human sign-off. |

---

## 3. LangGraph State Machine Specification

```python
class WebsiteOptimizerState(TypedDict):
    project_id: str
    target_url: str | None
    audience_name: str | None
    audience_persona: str | None
    page_snapshot: dict[str, Any] | None
    hypotheses: list[str]
    raw_variants: list[dict[str, Any]]
    validated_variants: list[dict[str, Any]]
    validation_reports: list[dict[str, Any]]
    execution_steps: list[dict[str, Any]]
    error: str | None
```

---

## 4. Human-in-the-Loop (HITL) Checkpoint Gate
No AI-generated variant can be launched into live customer traffic automatically:
1. All variants emerge from the graph with `status = "needs_review"`.
2. The user inspects the variant in the **Experience Studio** with a live side-by-side diff against the control and reviews the brand guardrail score.
3. Only upon explicit user confirmation (`POST /api/v1/intentflow/variants/{id}/approve`) does the variant transition to `approved`, enabling A/B experiment creation.

---

## 5. Observability & Execution Traces
Every agent invocation records an immutable trace in the `agent_execution_traces` table:
- **Trace ID**: Unique UUID
- **Workflow Type**: `website_optimizer` or `financial_assistant`
- **Latency**: Granular timing per node in milliseconds (`duration_ms`)
- **Token Metrics**: Total prompt and completion tokens tracked
- **Step Transitions**: Chronological execution timeline visible in the **Agent Lab** UI.
