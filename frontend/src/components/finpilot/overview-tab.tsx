"use client";

import React, { useEffect, useState } from "react";
import {
  TrendingUp,
  CreditCard,
  AlertCircle,
  FileText,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  ShieldCheck,
  Sparkles,
  RefreshCw,
  Clock,
  CheckCircle2,
  Upload,
  Eye,
  ExternalLink,
  ChevronRight,
  BookOpen
} from "lucide-react";
import {
  getOverview,
  getAuditEvents,
  activateDossier,
  uploadDossierDocument,
  type OverviewMetricsData,
  type AuditEventData,
} from "@/lib/api";
import { formatINR, formatDate } from "./utils";

interface OverviewTabProps {
  onNavigateTab: (tab: string) => void;
  onOpenCreateInvoice?: () => void;
  onOpenAddClient?: () => void;
}

const DOSSIERS = [
  {
    id: "apex_global",
    name: "Apex Global Technologies Pvt Ltd",
    badge: "PDF 1 · 24 Pages Verified",
    industry: "Enterprise Cloud & AI Systems",
    state: "Karnataka (State Code 29 · Bengaluru)",
    gstin: "29AAACA1234A1Z5",
    pdfUrl: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf",
    invoiced: "₹29,26,400.00",
    collected: "₹21,83,000.00",
    surplus: "₹10,10,000.00",
    topClient: "Titan Infrastructure Corp",
    overdueDebtor: "Kavach Security Solutions (INR 2,10,000)",
  },
  {
    id: "kavach_security",
    name: "Kavach Security Solutions Pvt Ltd",
    badge: "PDF 2 · 25 Pages Verified",
    industry: "Enterprise Cybersecurity & SOC 2",
    state: "Maharashtra (State Code 27 · Mumbai)",
    gstin: "27AABCK5678B1Z2",
    pdfUrl: "/dossiers/Kavach_Security_Solutions_Annual_Audit_2026.pdf",
    invoiced: "₹38,50,000.00",
    collected: "₹29,00,000.00",
    surplus: "₹14,80,000.00",
    topClient: "Mahindra Defense Systems",
    overdueDebtor: "CyberShield Asia Pacific (INR 2,80,000)",
  },
  {
    id: "zenith_digital",
    name: "Zenith Digital Media & Design LLP",
    badge: "PDF 3 · 22 Pages Verified",
    industry: "Performance Marketing & Growth",
    state: "New Delhi (State Code 07)",
    gstin: "07AAGFZ9012C1Z8",
    pdfUrl: "/dossiers/Zenith_Digital_Media_Q3_Financial_Review.pdf",
    invoiced: "₹19,11,600.00",
    collected: "₹15,10,400.00",
    surplus: "₹6,70,000.00",
    topClient: "Swiggy Instamart Media",
    overdueDebtor: "Cult.fit Fitness & Wellness (INR 90,000)",
  },
];

export function OverviewTab({
  onNavigateTab,
  onOpenCreateInvoice,
  onOpenAddClient,
}: OverviewTabProps) {
  const [metrics, setMetrics] = useState<OverviewMetricsData | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEventData[]>([]);
  const [activeDossierId, setActiveDossierId] = useState<string>("apex_global");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activatingId, setActivatingId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const loadData = async () => {
    try {
      const [m, a] = await Promise.all([getOverview(), getAuditEvents()]);
      setMetrics(m);
      setAuditEvents(Array.isArray(a) ? a.slice(0, 10) : []);
    } catch (err) {
      console.error("Failed to load overview data:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const handleActivateDossier = async (dossierId: string) => {
    setActivatingId(dossierId);
    try {
      await activateDossier(dossierId);
      setActiveDossierId(dossierId);
      await loadData();
    } catch (err) {
      console.error("Failed to activate dossier:", err);
    } finally {
      setActivatingId(null);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await uploadDossierDocument(formData);
      await loadData();
    } catch (err) {
      console.error("Failed to upload custom PDF:", err);
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="flex items-center gap-3 text-zinc-400 text-sm">
          <RefreshCw className="h-5 w-5 animate-spin text-rose-500" />
          Loading financial ledger &amp; statutory audit overview...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in text-zinc-100">
      {/* Top Banner - Sleek Dark Zinc with Glowing Rose/Indigo accents */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-zinc-950 via-zinc-900 to-zinc-950 p-6 sm:p-7 border border-zinc-800 shadow-2xl shadow-black/60">
        <div className="pointer-events-none absolute right-0 top-0 -mt-10 -mr-10 h-72 w-72 rounded-full bg-rose-600/10 blur-3xl" />
        <div className="pointer-events-none absolute left-1/3 bottom-0 h-40 w-40 rounded-full bg-pink-600/10 blur-2xl" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-5">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-950/80 px-3 py-1 text-xs font-semibold text-emerald-400 border border-emerald-800/80">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                Deterministic GST Engine Active (SAC 998311 / 998313)
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-950/80 px-2.5 py-1 text-xs font-medium text-rose-300 border border-rose-800/80">
                <ShieldCheck className="h-3.5 w-3.5 text-rose-400" />
                PostgreSQL ACID Verified Ledger
              </span>
            </div>
            <h1 className="mt-3 text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              Autonomous Financial Operations Dashboard
            </h1>
            <p className="mt-1 text-xs sm:text-sm text-zinc-400 max-w-2xl">
              Double-entry audit verification, sequential Indian GST invoicing, and LangGraph-supervised cash flow operations.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 rounded-xl border border-zinc-700 bg-zinc-900/90 hover:bg-zinc-800 px-4 py-2.5 text-xs font-semibold text-zinc-200 transition shadow-sm"
            >
              <RefreshCw className={`h-3.5 w-3.5 text-rose-400 ${refreshing ? "animate-spin" : ""}`} />
              <span>Refresh Ledger</span>
            </button>
            <button
              onClick={() => onNavigateTab("assistant")}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 px-4 py-2.5 text-xs font-bold text-white shadow-lg shadow-rose-600/30 border border-rose-400/40 transition"
            >
              <Sparkles className="h-4 w-4" />
              <span>Ask Neural Copilot</span>
            </button>
          </div>
        </div>
      </div>

      {/* Statutory Dossier Selector & Custom PDF Upload Section */}
      <div className="rounded-2xl border border-zinc-800 bg-zinc-900/80 p-6 shadow-xl shadow-black/40 backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-zinc-800/80">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="inline-flex items-center gap-1 rounded-full bg-rose-950/90 border border-rose-500/40 px-2.5 py-0.5 text-[11px] font-bold text-rose-300">
                <BookOpen className="h-3 w-3" />
                Statutory Dossiers &amp; PDF Ingestion
              </span>
              <span className="text-xs text-zinc-500 hidden sm:inline">
                · Switch between verified statutory audits or upload custom financial records
              </span>
            </div>
            <h2 className="text-lg font-bold text-white">
              Choose or Upload a Financial Dossier PDF
            </h2>
          </div>

          <div>
            <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 px-4 py-2 text-xs font-bold text-white shadow-md shadow-rose-600/30 border border-rose-400/40 transition">
              <Upload className="h-3.5 w-3.5" />
              <span>{uploading ? "Extracting PDF..." : "Upload Custom PDF/CSV"}</span>
              <input
                type="file"
                accept=".pdf,.csv"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>
          </div>
        </div>

        {/* 3 Dossiers Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
          {DOSSIERS.map((d) => {
            const isActive = activeDossierId === d.id;
            return (
              <div
                key={d.id}
                className={`rounded-xl border p-4 flex flex-col justify-between transition-all relative overflow-hidden ${
                  isActive
                    ? "border-rose-500/80 bg-zinc-900 shadow-lg shadow-rose-950/40 ring-1 ring-rose-500/40"
                    : "border-zinc-800/90 bg-zinc-950/60 hover:border-zinc-700 hover:bg-zinc-900/60"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="rounded-full bg-zinc-800 border border-zinc-700 px-2 py-0.5 text-[10px] font-bold text-zinc-300">
                      {d.badge}
                    </span>
                    {isActive ? (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-400">
                        <CheckCircle2 className="h-3 w-3" />
                        Active In Ledger
                      </span>
                    ) : (
                      <a
                        href={d.pdfUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-[10px] text-zinc-400 hover:text-rose-400 font-medium"
                      >
                        <Eye className="h-3 w-3" />
                        View PDF
                      </a>
                    )}
                  </div>

                  <h3 className="text-sm font-bold text-white">
                    {d.name}
                  </h3>
                  <p className="text-xs text-zinc-400 mt-0.5">
                    {d.industry}
                  </p>
                  <p className="text-[11px] text-zinc-500 font-mono mt-0.5">
                    {d.state} · {d.gstin}
                  </p>

                  <div className="grid grid-cols-3 gap-1.5 mt-3 pt-2.5 border-t border-zinc-800/80 text-center">
                    <div className="rounded bg-zinc-950/80 p-1.5 border border-zinc-800/60">
                      <span className="text-[9px] text-zinc-500 block uppercase font-bold">Invoiced</span>
                      <span className="text-xs font-bold text-white">{d.invoiced.split(".")[0]}</span>
                    </div>
                    <div className="rounded bg-zinc-950/80 p-1.5 border border-zinc-800/60">
                      <span className="text-[9px] text-zinc-500 block uppercase font-bold">Collected</span>
                      <span className="text-xs font-bold text-emerald-400">{d.collected.split(".")[0]}</span>
                    </div>
                    <div className="rounded bg-zinc-950/80 p-1.5 border border-zinc-800/60">
                      <span className="text-[9px] text-zinc-500 block uppercase font-bold">Surplus</span>
                      <span className="text-xs font-bold text-rose-300">{d.surplus.split(".")[0]}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-2 flex items-center gap-2">
                  <button
                    onClick={() => handleActivateDossier(d.id)}
                    disabled={activatingId === d.id || isActive}
                    className={`flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg py-2 text-xs font-bold transition ${
                      isActive
                        ? "bg-rose-950/80 text-rose-300 border border-rose-500/40 cursor-default"
                        : "bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700"
                    }`}
                  >
                    <Sparkles className="h-3 w-3 text-rose-400" />
                    <span>{activatingId === d.id ? "Loading..." : isActive ? "Active In Database" : "Activate Dossier"}</span>
                  </button>
                  <a
                    href={d.pdfUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="p-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white border border-zinc-700 transition"
                    title="View Official PDF"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* KPI Cards Grid - Cohesive Dark Zinc with Refined Glows */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* Total Invoiced */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/90 p-4 shadow-lg shadow-black/40 hover:border-zinc-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-400">Total Invoiced</span>
            <div className="rounded-lg bg-zinc-800 p-2 text-rose-400 border border-zinc-700">
              <FileText className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2.5">
            <p className="text-xl font-black text-white">
              {formatINR(metrics?.total_invoiced)}
            </p>
            <p className="mt-0.5 text-xs text-zinc-400">
              {metrics?.active_invoices_count ?? 0} active invoice(s)
            </p>
          </div>
        </div>

        {/* Total Collected */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/90 p-4 shadow-lg shadow-black/40 hover:border-zinc-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-400">Total Collected</span>
            <div className="rounded-lg bg-emerald-950/80 p-2 text-emerald-400 border border-emerald-800/80">
              <ArrowDownRight className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2.5">
            <p className="text-xl font-black text-emerald-400">
              {formatINR(metrics?.total_collected)}
            </p>
            <p className="mt-0.5 text-xs text-emerald-400/80 font-medium">
              Received into bank
            </p>
          </div>
        </div>

        {/* Outstanding Receivables */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/90 p-4 shadow-lg shadow-black/40 hover:border-zinc-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-400">Receivables</span>
            <div className="rounded-lg bg-amber-950/80 p-2 text-amber-400 border border-amber-800/80">
              <CreditCard className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2.5">
            <p className="text-xl font-black text-white">
              {formatINR(metrics?.outstanding_receivables)}
            </p>
            <p className="mt-0.5 text-xs text-amber-400 font-medium">
              Unpaid client balances
            </p>
          </div>
        </div>

        {/* Overdue Amount */}
        <div className="rounded-xl border border-rose-900/60 bg-rose-950/30 p-4 shadow-lg shadow-black/40 hover:border-rose-800 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-rose-300">Overdue</span>
            <div className="rounded-lg bg-rose-900/60 p-2 text-rose-300 border border-rose-700">
              <AlertCircle className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2.5">
            <p className="text-xl font-black text-rose-400">
              {formatINR(metrics?.overdue_amount)}
            </p>
            <p className="mt-0.5 text-xs text-rose-300 font-medium">
              {metrics?.overdue_invoices_count ?? 0} invoice(s) past due
            </p>
          </div>
        </div>

        {/* Total Expenses */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/90 p-4 shadow-lg shadow-black/40 hover:border-zinc-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-400">Expenses</span>
            <div className="rounded-lg bg-zinc-800 p-2 text-zinc-300 border border-zinc-700">
              <ArrowUpRight className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2.5">
            <p className="text-xl font-black text-zinc-200">
              {formatINR(metrics?.total_expenses)}
            </p>
            <p className="mt-0.5 text-xs text-zinc-400">
              Recorded operational costs
            </p>
          </div>
        </div>

        {/* Net Cash Flow */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/90 p-4 shadow-lg shadow-black/40 hover:border-zinc-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-400">Net Flow</span>
            <div className={`rounded-lg p-2 border ${
              (metrics?.net_cash_flow ?? 0) >= 0
                ? "bg-emerald-950/80 text-emerald-400 border-emerald-800/80"
                : "bg-rose-950/80 text-rose-400 border-rose-800/80"
            }`}>
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-2.5">
            <p className={`text-xl font-black ${
              (metrics?.net_cash_flow ?? 0) >= 0 ? "text-emerald-400" : "text-rose-400"
            }`}>
              {formatINR(metrics?.net_cash_flow)}
            </p>
            <p className="mt-0.5 text-xs text-zinc-400">
              Collected minus expenses
            </p>
          </div>
        </div>
      </div>

      {/* Quick Launch & Workspaces */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <button
          onClick={() => onNavigateTab("assistant")}
          className="group flex flex-col justify-between rounded-xl border border-zinc-800 bg-zinc-900/90 p-5 text-left hover:border-rose-500/50 hover:bg-zinc-900 transition-all shadow-lg shadow-black/40"
        >
          <div>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-tr from-rose-600 to-pink-600 text-white shadow-md shadow-rose-600/30">
              <Sparkles className="h-5 w-5" />
            </div>
            <h3 className="mt-3 font-bold text-white group-hover:text-rose-400 transition">
              Conversational Financial AI
            </h3>
            <p className="mt-1 text-xs text-zinc-400">
              Ask natural language queries like &ldquo;Tell me about PDF 1&rdquo;, &ldquo;Who owes money&rdquo;, or &ldquo;Show overdue&rdquo;.
            </p>
          </div>
          <span className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-rose-400 group-hover:translate-x-1 transition-transform">
            Launch Assistant &rarr;
          </span>
        </button>

        <button
          onClick={() => onNavigateTab("invoices")}
          className="group flex flex-col justify-between rounded-xl border border-zinc-800 bg-zinc-900/90 p-5 text-left hover:border-rose-500/50 hover:bg-zinc-900 transition-all shadow-lg shadow-black/40"
        >
          <div>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-800 text-rose-400 border border-zinc-700">
              <FileText className="h-5 w-5" />
            </div>
            <h3 className="mt-3 font-bold text-white group-hover:text-rose-400 transition">
              Indian GST Invoicing
            </h3>
            <p className="mt-1 text-xs text-zinc-400">
              Intra-state (CGST+SGST) and inter-state (IGST) deterministic math with branded PDF export.
            </p>
          </div>
          <span className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-zinc-300 group-hover:text-rose-400 group-hover:translate-x-1 transition-transform">
            Manage Invoices &rarr;
          </span>
        </button>

        <button
          onClick={() => onNavigateTab("clients")}
          className="group flex flex-col justify-between rounded-xl border border-zinc-800 bg-zinc-900/90 p-5 text-left hover:border-rose-500/50 hover:bg-zinc-900 transition-all shadow-lg shadow-black/40"
        >
          <div>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-800 text-emerald-400 border border-zinc-700">
              <CreditCard className="h-5 w-5" />
            </div>
            <h3 className="mt-3 font-bold text-white group-hover:text-rose-400 transition">
              Client Directory &amp; Ledger
            </h3>
            <p className="mt-1 text-xs text-zinc-400">
              15-char GSTIN syntax validation, state code lookup, client lifetime invoiced and overdue tracking.
            </p>
          </div>
          <span className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-zinc-300 group-hover:text-rose-400 group-hover:translate-x-1 transition-transform">
            View Clients &rarr;
          </span>
        </button>

        <button
          onClick={() => onNavigateTab("tax-compliance")}
          className="group flex flex-col justify-between rounded-xl border border-zinc-800 bg-zinc-900/90 p-5 text-left hover:border-rose-500/50 hover:bg-zinc-900 transition-all shadow-lg shadow-black/40"
        >
          <div>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-800 text-teal-400 border border-zinc-700">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <h3 className="mt-3 font-bold text-white group-hover:text-rose-400 transition">
              Tax &amp; GST Compliance
            </h3>
            <p className="mt-1 text-xs text-zinc-400">
              GSTR-1 outward supplies, SAC 998311 service breakdown, and 1-click JSON export for portal filing.
            </p>
          </div>
          <span className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-zinc-300 group-hover:text-rose-400 group-hover:translate-x-1 transition-transform">
            View Compliance &rarr;
          </span>
        </button>
      </div>

      {/* Immutable Audit Trail Section - Sleek Zinc Theme with Fixed Badges */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900/90 shadow-xl shadow-black/40 overflow-hidden">
        <div className="flex items-center justify-between border-b border-zinc-800 bg-zinc-950/70 px-6 py-4">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="h-5 w-5 text-rose-500" />
            <div>
              <h2 className="text-sm font-bold text-white">
                Immutable Audit Log &amp; Financial Ledger Events
              </h2>
              <p className="text-xs text-zinc-400">
                PostgreSQL append-only record tracking all invoice creation, issuance, payments, and approvals
              </p>
            </div>
          </div>
          <span className="rounded-full bg-zinc-800 border border-zinc-700 px-2.5 py-1 text-xs font-semibold text-zinc-300">
            {auditEvents.length} Recent Event(s)
          </span>
        </div>

        {auditEvents.length === 0 ? (
          <div className="py-8 text-center text-xs text-zinc-500">
            No audit records yet. Create an invoice or perform an action to populate the immutable log.
          </div>
        ) : (
          <div className="divide-y divide-zinc-800/80 max-h-96 overflow-y-auto">
            {auditEvents.map((evt) => {
              const actionLabel = evt.action || evt.event_type || "audit.event";
              const actorLabel = evt.actor || evt.actor_name || "system:web";
              const entityLabel = `${evt.entity_type || "ledger"}:${evt.entity_id ? evt.entity_id.slice(0, 8) : "ledger"}`;
              const desc = evt.description || (evt.action ? `Action logged: ${evt.action}` : "Transaction recorded in ledger");

              return (
                <div
                  key={evt.id}
                  className="flex items-start justify-between p-4 hover:bg-zinc-800/40 transition"
                >
                  <div className="flex items-start gap-3">
                    <span className="mt-0.5 rounded-md bg-rose-950/80 border border-rose-500/30 px-2 py-0.5 text-rose-300 font-mono text-[10px] font-bold">
                      {actionLabel}
                    </span>
                    <div>
                      <p className="text-xs font-semibold text-zinc-200">
                        {desc}
                      </p>
                      <div className="mt-1 flex items-center gap-3 text-[11px] text-zinc-500">
                        <span>Actor: <strong className="text-zinc-300 font-normal">{actorLabel}</strong></span>
                        <span>Entity: <span className="font-mono text-zinc-400">{entityLabel}</span></span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 text-[11px] text-zinc-400">
                    <Clock className="h-3.5 w-3.5 text-zinc-500" />
                    <span>{formatDate(evt.created_at)}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
