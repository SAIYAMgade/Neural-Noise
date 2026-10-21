from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SignalType = Literal["pricing_change", "job_posting", "news"]
SeverityType = Literal["LOW", "MEDIUM", "HIGH"]
AnomalySource = Literal["isolation_forest", "chronos2"]


class HealthScoreComponents(BaseModel):
    runway: int
    burn_stability: int
    revenue_growth: int
    unit_economics: int
    risk_factors: int


class HealthScoreResponse(BaseModel):
    score: int
    status: Literal["healthy", "warning", "critical"]
    reasoning: str
    components: HealthScoreComponents
    cached: bool
    timestamp: str


class RawFinancialRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date
    category: str = Field(min_length=1, max_length=100)
    amount: Decimal
    source_file: str | None = Field(default=None, max_length=255)
    customer_id: str | None = Field(default=None, max_length=255)
    run_id: uuid.UUID


class KPISnapshotRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: uuid.UUID
    week_start: date
    mrr: Decimal | None = None
    arr: Decimal | None = None
    churn_rate: Decimal | None = None
    burn_rate: Decimal | None = None
    gross_margin: Decimal | None = None
    cac: Decimal | None = None
    ltv: Decimal | None = None
    wow_delta: dict[str, Any] | None = None
    mom_delta: dict[str, Any] | None = None


class AnomalyRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: uuid.UUID
    metric: str = Field(min_length=1, max_length=100)
    actual_value: Decimal
    expected_range: dict[str, float]
    severity: SeverityType
    source: AnomalySource
    description: str | None = None


class MarketSignalRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: uuid.UUID
    competitor_name: str = Field(min_length=1, max_length=255)
    signal_type: SignalType
    summary: str = Field(min_length=1)
    raw_source_url: str | None = None
    date: date


class ReportRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: uuid.UUID
    week_start: date
    executive_summary: str
    full_text: str
    distribution_status: str = "pending"
    slack_message_ts: str | None = None
    email_sent_at: datetime | None = None


# ---------------------------------------------------------------------------
# WOW feature schemas
# ---------------------------------------------------------------------------

class SurvivalAnalysis(BaseModel):
    """Monte Carlo runway survival output - probability of financial ruin at each horizon."""

    score: int = Field(ge=0, le=100, description="Survival score 0-100 (100 = no risk of ruin in 365 days)")
    label: Literal["SAFE", "LOW_RISK", "MODERATE_RISK", "HIGH_RISK", "CRITICAL"]
    probability_ruin_90d: float = Field(ge=0.0, le=1.0)
    probability_ruin_180d: float = Field(ge=0.0, le=1.0)
    probability_ruin_365d: float = Field(ge=0.0, le=1.0)
    expected_zero_cash_day: int = Field(description="Median simulated days until cash hits zero")
    fundraising_deadline: str | None = Field(
        default=None,
        description="ISO date by which fundraising must start (expected_zero_cash_day minus 180 days)",
    )


class ScenarioResult(BaseModel):
    """Financial outcome for a single stress-test scenario."""

    scenario: Literal["bear", "base", "bull"]
    months_runway: float
    projected_mrr_6mo: float = Field(default=0.0, description="Projected MRR 6 months forward")
    series_a_readiness: Literal["READY", "6_MONTHS", "NOT_READY"]
    key_risks: list[str]
    recommended_actions: list[str]


class BoardQuestion(BaseModel):
    """A single adversarial board interrogation question with pre-drafted CFO answer."""

    question: str
    danger: Literal["RED", "YELLOW", "GREEN"]
    answer: str
    follow_up: str


# ---------------------------------------------------------------------------
# API request / response schemas
# ---------------------------------------------------------------------------

class AnalyzeResponse(BaseModel):
    run_id: uuid.UUID
    kpis: dict[str, Any]
    anomalies: list[dict[str, Any]]
    survival_analysis: dict[str, Any] | None = None
    scenario_analysis: list[dict[str, Any]] | None = None
    status: Literal["complete"]


class ReportRequest(BaseModel):
    run_id: uuid.UUID


class ReportResponse(BaseModel):
    run_id: uuid.UUID
    executive_summary: str
    full_report_markdown: str
    looker_url: str


class BoardPrepRequest(BaseModel):
    run_id: uuid.UUID


class BoardPrepResponse(BaseModel):
    run_id: uuid.UUID
    questions: list[dict[str, Any]]


class CFOInsightPayload(BaseModel):
    executive_summary: list[str] = Field(min_length=3, max_length=3)
    deep_dive: dict[str, str]
    risk_flags: list[dict[str, str]]
    market_snapshot: str
    recommendations: list[str]

    @field_validator("risk_flags")
    @classmethod
    def normalize_risk_flags(cls, value: list[dict[str, str]]) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        for item in value:
            severity = item.get("severity", "MEDIUM").upper()
            if severity not in {"LOW", "MEDIUM", "HIGH"}:
                severity = "MEDIUM"
            normalized.append(
                {
                    "metric": item.get("metric", "unknown"),
                    "description": item.get("description", ""),
                    "severity": severity,
                }
            )
        return normalized


class VCMemoRequest(BaseModel):
    run_id: uuid.UUID
    company_name: str = ""
    sector: str = "saas"
    months_runway: float = 0.0
    survival_score: int = 0
    ruin_probability_6m: float = 0.0


class VCMemoResponse(BaseModel):
    recommendation: Literal["PASS", "WATCH", "INVEST"]
    headline: str
    memo: str
    red_flags: list[str]
    what_would_change_our_mind: list[str]


class InvestorUpdateRequest(BaseModel):
    run_id: uuid.UUID
    company_name: str = ""
    sector: str = "saas"
    months_runway: float = 0.0
    survival_score: int = 0


class InvestorUpdateResponse(BaseModel):
    subject: str
    greeting: str
    metrics_block: str
    wins: list[str]
    challenges: list[str]
    next_30_days: list[str]
    asks: list[str]
    closing: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    db: Literal["connected", "disconnected"]
    models: list[str]


# ---------------------------------------------------------------------------
# Cash Flow Forecast schemas
# ---------------------------------------------------------------------------

class CashBalanceRequest(BaseModel):
    balance: Decimal = Field(gt=0, description="Current cash balance in USD")
    as_of_date: date = Field(default_factory=date.today)
    source: str = Field(default="manual", max_length=50)


class CommittedExpenseRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0, description="Amount per payment period in USD")
    frequency: Literal["weekly", "monthly", "quarterly", "annual"]
    next_payment_date: date
    category: str = Field(default="other", max_length=100)


class CashFlowForecastWeek(BaseModel):
    week_offset: int
    week_start: date
    predicted_balance_p10: float
    predicted_balance_p50: float
    predicted_balance_p90: float
    expected_inflows: float
    expected_outflows: float


class CashFlowForecastResponse(BaseModel):
    run_id: uuid.UUID
    current_cash: float
    total_committed_weekly: float
    weeks_until_zero_p50: int | None
    forecast: list[CashFlowForecastWeek]
    committed_expenses: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Deferred Revenue / Contract schemas
# ---------------------------------------------------------------------------

class ContractRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=255)
    total_value: Decimal = Field(gt=0)
    start_date: date
    end_date: date
    payment_terms: Literal["annual", "quarterly", "monthly"] = "annual"
    payment_received_at: datetime | None = None


class ContractResponse(BaseModel):
    id: uuid.UUID
    run_id: uuid.UUID
    customer_id: str
    total_value: float
    start_date: date
    end_date: date
    payment_terms: str


class DeferredRevenueMonth(BaseModel):
    month_start: date
    recognized_revenue: float
    deferred_balance: float


class DeferredRevenueResponse(BaseModel):
    run_id: uuid.UUID
    total_deferred_balance: float
    current_month_recognized: float
    contract_count: int
    schedule_next_12_months: list[DeferredRevenueMonth]
    contracts: list[ContractResponse]


# ---------------------------------------------------------------------------
# Board Deck schemas
# ---------------------------------------------------------------------------

class BoardDeckStatusResponse(BaseModel):
    deck_id: uuid.UUID
    run_id: uuid.UUID
    status: Literal["generating", "ready", "failed"]
    generated_at: datetime | None = None
    download_url: str | None = None


# ---------------------------------------------------------------------------
# Decision Engine / Saved Scenarios
# ---------------------------------------------------------------------------

class SavedScenarioCreateRequest(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    simulation_id: str = Field(min_length=1, max_length=50)
    summary: str | None = None
    runway_months_before: float = Field(ge=0)
    runway_months_after: float = Field(ge=0)
    weekly_impact: float
    proof_points: list[str] = Field(default_factory=list, max_length=4)


class SavedScenarioResponse(BaseModel):
    id: uuid.UUID
    run_id: uuid.UUID
    label: str
    simulation_id: str
    summary: str | None = None
    runway_months_before: float
    runway_months_after: float
    weekly_impact: float
    proof_points: list[str] = Field(default_factory=list)
    created_at: datetime


# ---------------------------------------------------------------------------
# Integration schemas
# ---------------------------------------------------------------------------

class IntegrationStatusResponse(BaseModel):
    platform: Literal["stripe", "quickbooks"]
    status: Literal["active", "pending", "error", "not_connected"]
    company_name: str | None = None
    last_sync_at: datetime | None = None
    rows_synced: int = 0


class OAuthAuthorizeResponse(BaseModel):
    authorization_url: str
    demo_mode: bool = False


class SyncResponse(BaseModel):
    run_id: uuid.UUID
    platform: str
    rows_synced: int
    status: Literal["success", "error"]
    message: str = ""


# ---------------------------------------------------------------------------
# Fraud Detection schemas
# ---------------------------------------------------------------------------

class FraudAlertRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: uuid.UUID
    week_start: date
    category: str = Field(min_length=1, max_length=100)
    pattern: str = Field(min_length=1, max_length=50)
    severity: SeverityType
    amount: Decimal
    description: str | None = None


# ---------------------------------------------------------------------------
# Customer Profitability schemas
# ---------------------------------------------------------------------------

class CustomerProfileRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: uuid.UUID
    customer_id: str = Field(min_length=1, max_length=255)
    total_revenue: Decimal
    weeks_active: int
    avg_weekly_revenue: Decimal
    first_seen: date
    last_seen: date
    churn_flag: bool = False
    segment: str = Field(min_length=1, max_length=20)
    revenue_pct: Decimal


# ---------------------------------------------------------------------------
# Autonomous Agent schemas
# ---------------------------------------------------------------------------

class AgentObservationResponse(BaseModel):
    id: uuid.UUID
    observed_at: datetime
    runway_months: float
    burn_rate: float
    mrr: float
    burn_change_pct: float
    mrr_change_pct: float
    active_anomalies_count: int
    fraud_alerts_count: int


class AgentActionResponse(BaseModel):
    id: uuid.UUID
    plan_id: uuid.UUID
    action_type: str
    status: str
    requires_approval: bool
    approval_message: str | None
    result: dict[str, Any] | None
    created_at: datetime
    executed_at: datetime | None


class AgentStatusResponse(BaseModel):
    run_id: uuid.UUID
    latest_observation: AgentObservationResponse | None = None
    pending_approvals: list[AgentActionResponse] = []
    recent_actions: list[AgentActionResponse] = []
    agent_running: bool = False


class AgentCycleResponse(BaseModel):
    run_id: uuid.UUID
    decision_tool: str
    decision_reasoning: str
    plan_type: str
    plan_goal: str
    actions_executed: int
    actions_pending_approval: int
    actions_failed: int
    error: str = ""


# ---------------------------------------------------------------------------
# FinPilot AI Financial Operations Schemas
# ---------------------------------------------------------------------------

class ClientCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    company_name: str | None = None
    phone: str | None = None
    billing_address: str | None = None
    state_code: str = Field(default="27", min_length=2, max_length=2)
    gstin: str | None = None
    currency: str = Field(default="INR", min_length=3, max_length=3)
    payment_terms_days: int = Field(default=15, ge=0, le=180)
    notes: str | None = None


class ClientResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    name: str
    company_name: str | None
    email: str
    phone: str | None
    billing_address: str | None
    state_code: str
    gstin: str | None
    currency: str
    payment_terms_days: int
    status: str
    notes: str | None
    created_at: datetime


class ClientLedgerResponse(BaseModel):
    client: ClientResponse
    total_invoiced: Decimal
    total_paid: Decimal
    total_due: Decimal
    overdue_invoices_count: int
    invoices_count: int
    payments_count: int


class InvoiceLineItemInput(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    hsn_sac_code: str | None = None
    quantity: Decimal = Field(default=Decimal("1.0"), ge=0)
    unit_price: Decimal = Field(ge=0)
    discount_pct: Decimal = Field(default=Decimal("0.0"), ge=0, le=100)
    tax_rate_pct: Decimal = Field(default=Decimal("18.0"), ge=0)


class InvoiceLineItemResponse(BaseModel):
    id: uuid.UUID
    description: str
    hsn_sac_code: str | None
    quantity: Decimal
    unit_price: Decimal
    discount_pct: Decimal
    tax_rate_pct: Decimal
    line_total: Decimal
    tax_amount: Decimal


class InvoiceDraftRequest(BaseModel):
    client_id: uuid.UUID
    line_items: list[InvoiceLineItemInput]
    invoice_date: date | None = None
    due_date: date | None = None
    due_days: int | None = 15
    notes: str | None = None
    is_export: bool = False


class InvoiceIssueRequest(BaseModel):
    idempotency_key: str | None = None


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    client_id: uuid.UUID
    client_name: str | None = None
    invoice_number: str
    invoice_date: date
    due_date: date
    status: str
    currency: str
    subtotal: Decimal
    discount_total: Decimal
    tax_type: str
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_tax: Decimal
    grand_total: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    notes: str | None
    pdf_path: str | None
    created_at: datetime
    issued_at: datetime | None
    line_items: list[InvoiceLineItemResponse] = []


class InvoiceCalculationPreviewRequest(BaseModel):
    client_id: uuid.UUID
    line_items: list[InvoiceLineItemInput]
    is_export: bool = False


class InvoiceCalculationPreviewResponse(BaseModel):
    subtotal: Decimal
    discount_total: Decimal
    taxable_amount: Decimal
    tax_type: str
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_tax: Decimal
    grand_total: Decimal


class PaymentCreateRequest(BaseModel):
    client_id: uuid.UUID
    amount: Decimal = Field(gt=0)
    payment_date: date | None = None
    payment_method: str = "bank_transfer"
    reference_number: str | None = None
    notes: str | None = None
    allocate_to_invoice_id: uuid.UUID | None = None


class PaymentAllocationRequest(BaseModel):
    payment_id: uuid.UUID
    invoice_id: uuid.UUID
    amount_to_allocate: Decimal | None = None


class PaymentResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    client_id: uuid.UUID
    client_name: str | None = None
    payment_number: str
    payment_date: date
    amount: Decimal
    currency: str
    payment_method: str
    reference_number: str | None
    status: str
    notes: str | None
    allocated_amount: Decimal
    unallocated_amount: Decimal
    created_at: datetime


class ExpenseCreateRequest(BaseModel):
    date: date
    category: str
    merchant: str
    amount: Decimal = Field(gt=0)
    tax_amount: Decimal = Decimal("0.00")
    gstin: str | None = None
    payment_method: str = "bank_transfer"
    notes: str | None = None


class ExpenseResponse(BaseModel):
    id: uuid.UUID
    business_id: uuid.UUID
    date: date
    category: str
    merchant: str
    amount: Decimal
    currency: str
    tax_amount: Decimal
    gstin: str | None
    payment_method: str
    notes: str | None
    receipt_path: str | None
    is_verified: bool
    created_at: datetime


class AssistantChatRequest(BaseModel):
    message: str
    conversation_id: uuid.UUID | None = None
    approval_request_id: uuid.UUID | None = None


class AssistantChatResponse(BaseModel):
    response: str
    message: str | None = None
    reply: str | None = None
    conversation_id: uuid.UUID
    intent: str
    tool_name: str | None = None
    card_type: str | None = None
    card_data: dict[str, Any] | None = None
    structured_card: dict[str, Any] | None = None
    requires_approval: bool = False
    approval_request_id: uuid.UUID | None = None


class ApprovalConfirmRequest(BaseModel):
    approval_request_id: uuid.UUID
