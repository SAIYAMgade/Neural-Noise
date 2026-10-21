import type {
  AnalysisSummaryData,
  AgentCycleResult,
  AgentStatus,
  AnalyzeResponse,
  BenchmarkResult,
  BoardDeckStatus,
  CashFlowSectionData,
  CustomerProfile,
  DeferredRevenueSummary,
  FraudAlert,
  HealthScoreData,
  IntegrationStatus,
  MorningBriefingData,
  PipelineStatus,
  BoardPrepResponse,
  ReportData,
  CompetitorProfile,
  SavedScenarioRecord,
  VCMemoData,
  PreMortemScenario,
  ChatMessage,
} from "./types";

export function getBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "");
  }
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host !== "localhost" && host !== "127.0.0.1") {
      return "https://neural-noise.onrender.com";
    }
  }
  if (process.env.NODE_ENV === "production") {
    return "https://neural-noise.onrender.com";
  }
  return "http://localhost:8000";
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const base = getBaseUrl();
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: { Accept: "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

/** Check if API is reachable */
export async function checkHealth(): Promise<boolean> {
  try {
    const base = getBaseUrl();
    const r = await fetch(`${base}/health`, { cache: "no-store" });
    return r.ok;
  } catch {
    return false;
  }
}

/** Start demo in background → returns run_id immediately */
export async function startDemo(
  companyName = "",
  sector = "saas_productivity",
): Promise<{ run_id: string; status: string }> {
  return apiFetch("/demo/async", { method: "POST" });
}

/** Start file analysis in background → returns run_id immediately */
export async function startAnalysis(
  file: File,
  companyName = "",
  sector = "saas_productivity",
): Promise<{ run_id: string; status: string }> {
  const form = new FormData();
  form.append("file", file);
  return apiFetch("/analyze/async", { method: "POST", body: form });
}

/** Run demo synchronously (for dashboard data after pipeline done) */
export async function runDemoSync(
  companyName = "Acme SaaS Co.",
  sector = "saas_productivity",
): Promise<AnalyzeResponse> {
  const params = new URLSearchParams({ company_name: companyName, sector });
  return apiFetch(`/demo?${params}`, { method: "POST" });
}

/** Run file analysis synchronously */
export async function runAnalysisSync(
  file: File,
  companyName = "",
  sector = "saas_productivity",
): Promise<AnalyzeResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("company_name", companyName);
  form.append("sector", sector);
  return apiFetch("/analyze", { method: "POST", body: form });
}

/** Poll pipeline status */
export async function pollStatus(runId: string): Promise<PipelineStatus> {
  return apiFetch(`/runs/${runId}/status`);
}

/** Get board prep Q&A */
export async function getBoardPrep(runId: string): Promise<BoardPrepResponse> {
  return apiFetch("/board-prep", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId }),
  });
}

/** Get CFO report */
export async function getReport(runId: string): Promise<ReportData> {
  return apiFetch("/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId }),
  });
}

/** Get full KPI time series for a run (all weekly snapshots) */
export async function getKPISeries(runId: string): Promise<import("./types").KPISnapshot[]> {
  return apiFetch(`/runs/${runId}/kpis`);
}

/** Get recomputed survival + scenario outputs for a run */
export async function getAnalysisSummary(runId: string): Promise<AnalysisSummaryData> {
  return apiFetch(`/runs/${runId}/analysis-summary`);
}

/** Get backend-persisted decision scenarios for a run */
export async function getSavedScenarios(runId: string): Promise<SavedScenarioRecord[]> {
  return apiFetch(`/runs/${runId}/saved-scenarios`);
}

/** Persist a decision scenario for a run */
export async function saveScenario(
  runId: string,
  payload: {
    label: string;
    simulation_id: string;
    summary?: string | null;
    runway_months_before: number;
    runway_months_after: number;
    weekly_impact: number;
    proof_points: string[];
  },
): Promise<SavedScenarioRecord> {
  return apiFetch(`/runs/${runId}/saved-scenarios`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

/** Delete a persisted decision scenario */
export async function deleteSavedScenario(runId: string, scenarioId: string): Promise<void> {
  await apiFetch(`/runs/${runId}/saved-scenarios/${scenarioId}`, { method: "DELETE" });
}

/** Get all anomalies for a run */
export async function getAnomalies(runId: string): Promise<import("./types").Anomaly[]> {
  return apiFetch(`/runs/${runId}/anomalies`);
}

/** Get all market signals for a run */
export async function getSignals(runId: string): Promise<import("./types").MarketSignal[]> {
  return apiFetch(`/runs/${runId}/signals`);
}

/** Get competitor profiles for a sector - Wikipedia + Clearbit logos, fully free */
export async function getSectorCompetitors(sector: string): Promise<CompetitorProfile[]> {
  return apiFetch(`/sectors/${sector}/competitors`);
}

/** Generate a ready-to-send monthly investor update email - uses Claude Haiku (~$0.003/call) */
export async function getInvestorUpdate(
  runId: string,
  monthsRunway: number,
  survivalScore: number,
  companyName: string,
  sector: string,
): Promise<import("./types").InvestorUpdateData> {
  return apiFetch("/investor-update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      run_id: runId,
      company_name: companyName,
      sector,
      months_runway: monthsRunway,
      survival_score: survivalScore,
    }),
  });
}

/** Generate a VC investment committee memo - uses Claude Haiku (~$0.003/call) */
export async function getVCMemo(
  runId: string,
  monthsRunway: number,
  survivalScore: number,
  ruinProb6m: number,
  companyName: string,
  sector: string,
): Promise<VCMemoData> {
  return apiFetch("/vc-memo", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      run_id: runId,
      company_name: companyName,
      sector,
      months_runway: monthsRunway,
      survival_score: survivalScore,
      ruin_probability_6m: ruinProb6m,
    }),
  });
}

// ── Cash Flow Forecast ─────────────────────────────────────────────────────

/** Get the 13-week cash flow forecast (auto-computed from KPI + committed expenses) */
export async function getCashFlow(runId: string): Promise<CashFlowSectionData> {
  return apiFetch(`/runs/${runId}/forecast/cash-flow`);
}

/** Set current cash balance */
export async function setCashBalance(
  runId: string,
  balance: number,
  asOfDate?: string,
): Promise<void> {
  await apiFetch(`/runs/${runId}/cash-balance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ balance, as_of_date: asOfDate ?? new Date().toISOString().split("T")[0] }),
  });
}

/** Add a recurring committed expense */
export async function addCommittedExpense(
  runId: string,
  expense: {
    name: string;
    amount: number;
    frequency: "weekly" | "monthly" | "quarterly" | "annual";
    next_payment_date: string;
    category?: string;
  },
): Promise<void> {
  await apiFetch(`/runs/${runId}/committed-expenses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(expense),
  });
}

/** Refresh the 13-week forecast from latest data */
export async function refreshForecast(runId: string): Promise<CashFlowSectionData> {
  return apiFetch(`/runs/${runId}/forecast/refresh`, { method: "POST" });
}

// ── Deferred Revenue ───────────────────────────────────────────────────────

/** Get deferred revenue summary and 12-month schedule */
export async function getDeferredRevenue(runId: string): Promise<DeferredRevenueSummary> {
  return apiFetch(`/runs/${runId}/deferred-revenue`);
}

/** Create a new annual/multi-year contract */
export async function addContract(
  runId: string,
  contract: {
    customer_id: string;
    total_value: number;
    start_date: string;
    end_date: string;
    payment_terms: "annual" | "quarterly" | "monthly";
  },
): Promise<{ id: string; customer_id: string }> {
  return apiFetch(`/runs/${runId}/contracts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(contract),
  });
}

// ── Board Deck ─────────────────────────────────────────────────────────────

/** Trigger async board deck generation */
export async function generateBoardDeck(
  runId: string,
  companyName?: string,
): Promise<{ deck_id: string; run_id: string; status: string }> {
  const params = companyName ? `?company_name=${encodeURIComponent(companyName)}` : "";
  return apiFetch(`/runs/${runId}/board-deck/generate${params}`, { method: "POST" });
}

/** Poll board deck generation status */
export async function getBoardDeckStatus(runId: string): Promise<BoardDeckStatus> {
  return apiFetch(`/runs/${runId}/board-deck/status`);
}

/** Return the download URL for the generated board deck */
export function getBoardDeckDownloadUrl(runId: string): string {
  const BASE = getBaseUrl();
  return `${BASE}/runs/${runId}/board-deck/download`;
}

// ── Integrations ───────────────────────────────────────────────────────────

/** Get status of all integrations */
export async function getIntegrations(): Promise<IntegrationStatus[]> {
  return apiFetch("/integrations/status");
}

/** Get Stripe OAuth authorization URL */
export async function getStripeAuthUrl(): Promise<{ authorization_url: string; demo_mode: boolean }> {
  return apiFetch("/integrations/stripe/authorize");
}

/** Get QuickBooks OAuth authorization URL */
export async function getQuickBooksAuthUrl(): Promise<{ authorization_url: string; demo_mode: boolean }> {
  return apiFetch("/integrations/quickbooks/authorize");
}

/** Sync Stripe data for a run */
export async function syncStripe(runId: string): Promise<{ rows_synced: number; status: string; message: string }> {
  return apiFetch(`/runs/${runId}/integrations/stripe/sync`, { method: "POST" });
}

/** Sync QuickBooks data for a run */
export async function syncQuickBooks(runId: string): Promise<{ rows_synced: number; status: string; message: string }> {
  return apiFetch(`/runs/${runId}/integrations/quickbooks/sync`, { method: "POST" });
}

// ── Fraud Detection ─────────────────────────────────────────────────────────

/** Get fraud alerts for a run */
export async function getFraudAlerts(runId: string): Promise<FraudAlert[]> {
  return apiFetch(`/runs/${runId}/fraud-alerts`);
}

// ── Customer Profitability ──────────────────────────────────────────────────

/** Get customer profitability profiles for a run */
export async function getCustomerProfiles(runId: string): Promise<CustomerProfile[]> {
  return apiFetch(`/runs/${runId}/customers`);
}

// ── Pre-mortem Generator ───────────────────────────────────────────────────

/** Generate 3 failure scenarios via Claude Haiku (~$0.004/call) */
export async function getPreMortem(
  runId: string,
  monthsRunway: number,
  companyName: string,
  sector: string,
): Promise<PreMortemScenario[]> {
  return apiFetch("/pre-mortem", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId, months_runway: monthsRunway, company_name: companyName, sector }),
  });
}

// ── Industry Benchmarker ────────────────────────────────────────────────────

/** Compare this run's KPIs against anonymous industry percentile benchmarks */
export async function getBenchmarks(
  runId: string,
  sector: string,
): Promise<BenchmarkResult> {
  return apiFetch(`/benchmarks?run_id=${runId}&sector=${encodeURIComponent(sector)}`);
}

// ── Morning CFO Briefing ───────────────────────────────────────────────────

/** Generate a proactive morning CFO briefing for a run (~$0.003, Claude Haiku) */
export async function getMorningBriefing(
  runId: string,
  companyName: string,
): Promise<MorningBriefingData> {
  return apiFetch("/briefing/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId, company_name: companyName }),
  });
}

// ── Multi-turn Board Q&A Chat ──────────────────────────────────────────────

/** Send a message to the CFO board prep chat and get a response */
export async function sendBoardChatMessage(
  runId: string,
  messages: ChatMessage[],
): Promise<ChatMessage> {
  return apiFetch("/board-prep/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId, messages }),
  });
}

// ── Autonomous CFO Agent ───────────────────────────────────────────────────

/** Trigger one autonomous agent monitoring cycle */
export async function triggerAgentCycle(
  runId: string,
  companyName: string,
  sector: string,
): Promise<AgentCycleResult> {
  return apiFetch(`/agent/${runId}/cycle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ company_name: companyName, sector }),
  });
}

/** Get latest agent status: observation + pending approvals + recent actions */
export async function getAgentStatus(runId: string): Promise<AgentStatus> {
  return apiFetch(`/agent/${runId}/status`);
}

/** Get full action history for a run */
export async function getAgentActions(
  runId: string,
  limit = 50,
): Promise<{ run_id: string; actions: AgentStatus["recent_actions"] }> {
  return apiFetch(`/agent/${runId}/actions?limit=${limit}`);
}

/** Approve a pending agent action - triggers immediate execution */
export async function approveAgentAction(
  actionId: string,
): Promise<{ action_id: string; status: string; result: Record<string, unknown> }> {
  return apiFetch(`/agent/actions/${actionId}/approve`, { method: "POST" });
}

/** Reject a pending agent action */
export async function rejectAgentAction(
  actionId: string,
): Promise<{ action_id: string; status: string }> {
  return apiFetch(`/agent/actions/${actionId}/reject`, { method: "POST" });
}

/** Get financial health score (0-100) with live Claude reasoning.
 *  Cached for 2 minutes server-side. Pass forceRefresh=true to bypass cache. */
export async function getHealthScore(
  runId: string,
  forceRefresh = false,
): Promise<HealthScoreData> {
  return apiFetch<HealthScoreData>(
    `/runs/${runId}/health-score?refresh=${forceRefresh}`,
  );
}


// ---------------------------------------------------------------------------
// FinPilot AI Financial Operations APIs
// ---------------------------------------------------------------------------

export interface ClientData {
  id: string;
  name: string;
  legal_name?: string;
  gstin?: string;
  state_code?: string;
  email?: string;
  phone?: string;
  address?: string;
  is_active: boolean;
  payment_terms_days: number;
  created_at: string;
}

export interface ClientLedgerData {
  client_id: string;
  client_name: string;
  total_invoiced: number;
  total_paid: number;
  total_due: number;
  invoices_count: number;
  overdue_count: number;
  invoices: InvoiceData[];
}

export interface InvoiceLineItemData {
  id?: string;
  description: string;
  hsn_sac?: string;
  quantity: number;
  unit_price: number;
  discount_rate?: number;
  gst_rate: number;
  taxable_amount?: number;
  cgst_amount?: number;
  sgst_amount?: number;
  igst_amount?: number;
  total_amount?: number;
}

export interface InvoiceData {
  tax_type?: "intra_state" | "inter_state" | string;
  invoice_date?: string;
  cgst_amount?: string | number;
  sgst_amount?: string | number;
  igst_amount?: string | number;
  total_tax?: string | number;
  grand_total?: string | number;
  amount_due?: string | number;
  pdf_path?: string | null;
  id: string;
  invoice_number: string;
  status: "draft" | "issued" | "partially_paid" | "paid" | "overdue" | "cancelled";
  issue_date: string;
  due_date: string;
  client_id: string;
  client_name?: string;
  is_interstate: boolean;
  subtotal: number;
  discount_total: number;
  cgst_total: number;
  sgst_total: number;
  igst_total: number;
  total_amount: number;
  amount_paid: number;
  balance_due: number;
  notes?: string;
  pdf_url?: string;
  line_items: InvoiceLineItemData[];
  created_at: string;
}

export interface PaymentData {
  id: string;
  payment_number: string;
  client_id: string;
  client_name?: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  reference_number?: string;
  notes?: string;
  unallocated_amount: number;
  created_at: string;
  allocations?: {
    id: string;
    invoice_id: string;
    invoice_number?: string;
    amount: number;
  }[];
}

export interface ExpenseData {
  id: string;
  category: string;
  vendor?: string;
  amount: number;
  expense_date: string;
  payment_method?: string;
  tax_amount?: number;
  gstin?: string;
  is_tax_deductible: boolean;
  notes?: string;
  created_at: string;
}

export interface OverviewMetricsData {
  total_invoiced: number;
  total_collected: number;
  outstanding_receivables: number;
  overdue_amount: number;
  total_expenses: number;
  net_cash_flow: number;
  clients_count: number;
  active_invoices_count: number;
  overdue_invoices_count: number;
}

export interface AssistantChatResponse {
  conversation_id: string;
  message: string;
  status: "completed" | "waiting_approval" | "clarification_needed" | "error";
  structured_card?: {
    type: "invoice_draft" | "approval_gate" | "invoice_issued" | "overdue_summary" | "financial_summary" | "dossier_summary";
    data: any;
  };
  approval_request?: {
    id: string;
    action_type: string;
    parameters: any;
    status: string;
  };
}

export interface AuditEventData {
  id: string;
  action?: string;
  actor?: string;
  event_type?: string;
  entity_type: string;
  entity_id: string;
  actor_id?: string;
  actor_name?: string;
  description?: string;
  details?: any;
  created_at: string;
}

export async function getOverview(): Promise<OverviewMetricsData> {
  return apiFetch<OverviewMetricsData>("/api/v1/overview");
}

export async function getClients(search?: string): Promise<ClientData[]> {
  const q = search ? `?search=${encodeURIComponent(search)}` : "";
  return apiFetch<ClientData[]>(`/api/v1/clients${q}`);
}

export async function getClient(id: string): Promise<ClientData> {
  return apiFetch<ClientData>(`/api/v1/clients/${id}`);
}

export async function getClientLedger(id: string): Promise<ClientLedgerData> {
  return apiFetch<ClientLedgerData>(`/api/v1/clients/${id}/ledger`);
}

export async function createClient(data: Partial<ClientData>): Promise<ClientData> {
  return apiFetch<ClientData>("/api/v1/clients", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function getInvoices(params?: { client_id?: string; status?: string; overdue_only?: boolean }): Promise<InvoiceData[]> {
  const sp = new URLSearchParams();
  if (params?.client_id) sp.set("client_id", params.client_id);
  if (params?.status) sp.set("status", params.status);
  if (params?.overdue_only) sp.set("overdue_only", "true");
  const q = sp.toString() ? `?${sp.toString()}` : "";
  return apiFetch<InvoiceData[]>(`/api/v1/invoices${q}`);
}

export async function getInvoice(id: string): Promise<InvoiceData> {
  return apiFetch<InvoiceData>(`/api/v1/invoices/${id}`);
}

export async function createInvoiceDraft(data: any): Promise<InvoiceData> {
  return apiFetch<InvoiceData>("/api/v1/invoices/draft", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function previewInvoice(data: any): Promise<any> {
  return apiFetch<any>("/api/v1/invoices/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function issueInvoice(id: string, idempotencyKey?: string): Promise<InvoiceData> {
  return apiFetch<InvoiceData>(`/api/v1/invoices/${id}/issue`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ idempotency_key: idempotencyKey }),
  });
}

export async function cancelInvoice(id: string, reason?: string): Promise<InvoiceData> {
  return apiFetch<InvoiceData>(`/api/v1/invoices/${id}/cancel`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
}

export async function getPayments(clientId?: string): Promise<PaymentData[]> {
  const q = clientId ? `?client_id=${encodeURIComponent(clientId)}` : "";
  return apiFetch<PaymentData[]>(`/api/v1/payments${q}`);
}

export async function recordPayment(data: Partial<PaymentData>): Promise<PaymentData> {
  return apiFetch<PaymentData>("/api/v1/payments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function allocatePayment(data: { payment_id: string; invoice_id: string; amount_to_allocate?: number }): Promise<any> {
  return apiFetch<any>("/api/v1/payments/allocate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function getExpenses(): Promise<ExpenseData[]> {
  return apiFetch<ExpenseData[]>("/api/v1/expenses");
}

export async function createExpense(data: Partial<ExpenseData>): Promise<ExpenseData> {
  return apiFetch<ExpenseData>("/api/v1/expenses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function chatAssistant(message: string, conversationId?: string, approvalRequestId?: string): Promise<AssistantChatResponse> {
  return apiFetch<AssistantChatResponse>("/api/v1/assistant/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      approval_request_id: approvalRequestId,
    }),
  });
}

export async function approveAssistantAction(approvalRequestId: string): Promise<any> {
  return apiFetch<any>("/api/v1/assistant/approve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approval_request_id: approvalRequestId }),
  });
}

export async function getAuditEvents(): Promise<AuditEventData[]> {
  return apiFetch<AuditEventData[]>("/api/v1/audit-events");
}


// ---------------------------------------------------------------------------
// IntentFlow AI Website Personalization & Experimentation APIs
// ---------------------------------------------------------------------------

export interface WebsiteProjectData {
  id: string;
  name: string;
  url?: string;
  domain?: string;
  business_objective?: string;
  target_audience?: string;
  industry?: string;
  brand_voice?: string;
  brand_guidelines?: {
    tone?: string;
    prohibited_terms?: string[];
    required_phrases?: string[];
    headline_max_chars?: number;
    cta_max_chars?: number;
  };
  brand_rules?: any;
  pages?: PageSnapshotData[];
  audiences?: AudienceSegmentData[];
  variants?: ExperienceVariantData[];
  created_at: string;
}

export type ProjectData = WebsiteProjectData;

export interface PageSnapshotData {
  id: string;
  project_id: string;
  url?: string;
  content_hash?: string;
  http_status?: number;
  title?: string;
  meta_description?: string;
  headings?: { tag: string; text: string }[];
  value_prop?: string;
  benefits?: string[];
  calls_to_action?: { text: string; href?: string }[];
  trust_badges?: string[];
  raw_text?: string;
  extracted_elements?: Record<string, any>;
  variants?: ExperienceVariantData[];
  created_at: string;
}

export interface AudienceSegmentData {
  id: string;
  project_id: string;
  name: string;
  source?: string;
  persona_description?: string;
  hypothesis?: string;
  intent_hypotheses?: string[];
  created_at: string;
}

export interface ExperienceVariantData {
  id: string;
  project_id: string;
  page_snapshot_id: string;
  audience_segment_id?: string;
  name?: string;
  variant_name: string;
  headline: string;
  subheading?: string;
  main_copy?: string;
  body_copy?: string;
  benefits?: string[];
  cta_text: string;
  cta_url?: string;
  status: "draft" | "generated" | "needs_review" | "approved" | "rejected" | "archived";
  review_status?: string;
  guardrail_report?: any;
  validation_results?: {
    is_valid: boolean;
    brand_score: number;
    issues: { type: "error" | "warning"; field: string; message: string }[];
    prohibited_detected?: string[];
  };
  rationale?: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ExperimentVariantMetric {
  variant_id: string;
  variant_name: string;
  is_control: boolean;
  exposures: number;
  conversions: number;
  conversion_rate: number;
  relative_lift_pct: number;
  absolute_difference_pct: number;
  z_score: number;
  p_value: number;
  confidence_level_pct: number;
  is_significant: boolean;
  ci_lower: number;
  ci_upper: number;
  sample_size_warning: boolean;
}

export interface ExperimentMetricsData {
  experiment_id: string;
  experiment_name: string;
  status: string;
  primary_metric: string;
  total_exposures: number;
  total_conversions: number;
  total_visitors?: number;
  control_variant_id: string;
  control?: any;
  variants: ExperimentVariantMetric[] | Record<string, any>;
  recommendation: string;
  computed_at: string;
}

export interface ExperimentData {
  id: string;
  project_id: string;
  page_snapshot_id: string;
  name: string;
  status: "draft" | "running" | "paused" | "completed";
  primary_metric: string;
  traffic_allocation: Record<string, number>;
  start_time?: string;
  end_time?: string;
  created_at: string;
}

export interface AgentExecutionStep {
  node: string;
  status: string;
  latency_ms?: number;
  duration_ms?: number;
  details?: string;
  output_summary?: string;
}

export interface AgentExecutionTraceData {
  id: string;
  workflow_type?: string;
  workflow_name?: string;
  status: string;
  input_data?: any;
  output_data?: any;
  input_state?: any;
  output_state?: any;
  steps: AgentExecutionStep[];
  total_latency_ms?: number;
  duration_ms?: number;
  total_tokens?: number;
  created_at: string;
  completed_at?: string;
}

export interface EvaluationCaseResult {
  case_id: string;
  suite: string;
  name: string;
  passed: boolean;
  details: string;
}

export interface EvaluationRunData {
  id: string;
  suite_name: string;
  model_name?: string;
  total_cases?: number;
  total_tests?: number;
  passed_cases?: number;
  tests_passed?: number;
  failed_cases?: number;
  tests_failed?: number;
  pass_rate?: number;
  duration_ms?: number;
  metrics?: {
    accuracy_pct: number;
    total_latency_ms: number;
    brand_guardrails_passed?: number;
    financial_correctness_passed?: number;
  };
  details?: EvaluationCaseResult[];
  results?: any[];
  created_at: string;
}

export interface IntentflowSummaryData {
  projects_count: number;
  pages_analyzed_count: number;
  variants_generated_count: number;
  pending_approvals_count: number;
  running_experiments_count: number;
  agent_traces_count: number;
}

export async function getIntentflowSummary(): Promise<IntentflowSummaryData> {
  return apiFetch<IntentflowSummaryData>("/api/v1/intentflow/overview/summary");
}

export async function getProjects(): Promise<WebsiteProjectData[]> {
  return apiFetch<WebsiteProjectData[]>("/api/v1/intentflow/projects");
}

export async function createProject(data: Partial<WebsiteProjectData>): Promise<WebsiteProjectData> {
  return apiFetch<WebsiteProjectData>("/api/v1/intentflow/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: data.name,
      url: data.url || (data.domain ? 'https://' + data.domain : undefined),
      business_objective: data.business_objective || 'Website Personalization & Conversion Optimization',
      target_audience: data.target_audience || data.brand_voice || '',
      brand_guidelines: data.brand_guidelines || data.brand_rules,
    }),
  });
}

export async function getProjectDetails(projectId: string): Promise<{
  project: WebsiteProjectData;
  snapshots: PageSnapshotData[];
  audiences: AudienceSegmentData[];
  variants: ExperienceVariantData[];
  experiments: ExperimentData[];
}> {
  return apiFetch(`/api/v1/intentflow/projects/${projectId}`);
}

export async function ingestPageUrl(projectId: string, url: string): Promise<PageSnapshotData> {
  return apiFetch<PageSnapshotData>(`/api/v1/intentflow/projects/${projectId}/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
}

export const ingestPage = ingestPageUrl;

export async function createAudienceSegment(
  projectId: string,
  data: { name: string; hypothesis?: string; persona_description?: string; intent_hypotheses?: string[] }
): Promise<AudienceSegmentData> {
  return apiFetch<AudienceSegmentData>(`/api/v1/intentflow/projects/${projectId}/audiences`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: data.name,
      persona_description: data.hypothesis || data.persona_description || "",
      intent_hypotheses: data.hypothesis ? [data.hypothesis] : (data.intent_hypotheses || []),
    }),
  });
}

export async function generateVariantsWithAgent(projectId: string, data?: {
  target_url?: string;
  audience_name?: string;
  audience_persona?: string;
  page_id?: string;
  audience_id?: string;
  num_variants?: number;
}): Promise<any> {
  return apiFetch(`/api/v1/intentflow/projects/${projectId}/generate-variants`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data || {}),
  });
}

export const generateVariants = generateVariantsWithAgent;

export async function getProjectVariants(projectId: string): Promise<ExperienceVariantData[]> {
  return apiFetch<ExperienceVariantData[]>(`/api/v1/intentflow/projects/${projectId}/variants`);
}

export async function updateVariant(variantId: string, data: Partial<ExperienceVariantData>): Promise<ExperienceVariantData> {
  return apiFetch<ExperienceVariantData>(`/api/v1/intentflow/variants/${variantId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function approveVariant(variantId: string, status?: string, feedback?: string): Promise<any> {
  return apiFetch(`/api/v1/intentflow/variants/${variantId}/approve`, {
    method: "POST",
  });
}

export async function rejectVariant(variantId: string): Promise<any> {
  return apiFetch(`/api/v1/intentflow/variants/${variantId}/reject`, {
    method: "POST",
  });
}

export async function getExperiments(projectId?: string): Promise<ExperimentData[]> {
  const url = projectId ? `/api/v1/intentflow/experiments?project_id=${projectId}` : "/api/v1/intentflow/experiments";
  return apiFetch<ExperimentData[]>(url);
}

export async function createExperiment(data: {
  project_id: string;
  page_snapshot_id: string;
  name: string;
  traffic_allocation: Record<string, number>;
  primary_metric?: string;
}): Promise<ExperimentData> {
  return apiFetch<ExperimentData>("/api/v1/intentflow/experiments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function getExperimentMetrics(experimentId: string): Promise<ExperimentMetricsData> {
  return apiFetch<ExperimentMetricsData>(`/api/v1/intentflow/experiments/${experimentId}/metrics`);
}

export async function simulateTraffic(experimentId: string, data?: {
  total_visitors?: number;
  control_cr?: number;
  variant_cr?: number;
}): Promise<any> {
  return apiFetch(`/api/v1/intentflow/experiments/${experimentId}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data || {}),
  });
}

export async function getAgentTraces(limit: number = 20): Promise<AgentExecutionTraceData[]> {
  return apiFetch<AgentExecutionTraceData[]>(`/api/v1/intentflow/traces?limit=${limit}`);
}

export async function getEvaluations(limit: number = 15): Promise<EvaluationRunData[]> {
  return apiFetch<EvaluationRunData[]>(`/api/v1/intentflow/evaluations?limit=${limit}`);
}

export async function runEvaluationSuite(): Promise<EvaluationRunData> {
  return apiFetch<EvaluationRunData>("/api/v1/intentflow/evaluations/run", {
    method: "POST",
  });
}


// ── Corporate Dossiers & Multi-Page Document Ingestion ────────────────────────

export interface DossierData {
  id: string;
  name: string;
  subtitle: string;
  industry: string;
  state: string;
  gstin: string;
  pages_count: number;
  pdf_url: string;
  total_invoiced: number;
  total_collected: number;
  receivables: number;
  overdue: number;
  expenses: number;
  net_flow: number;
  active_invoices_count: number;
  clients_count: number;
  top_client: string;
  overdue_client: string;
}

export async function getDossiers(): Promise<DossierData[]> {
  return apiFetch<DossierData[]>("/api/v1/intentflow/dossiers");
}

export async function activateDossier(dossierId: string): Promise<any> {
  return apiFetch("/api/v1/intentflow/dossiers/activate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dossier_id: dossierId }),
  });
}

export async function uploadDossierDocument(formData: FormData): Promise<any> {
  const baseUrl = getBaseUrl();
  const res = await fetch(`${baseUrl}/api/v1/intentflow/dossiers/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || "Failed to upload document");
  }
  return res.json();
}
