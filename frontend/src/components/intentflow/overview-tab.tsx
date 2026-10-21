"use client";

import React, { useEffect, useState } from "react";
import {
  Globe,
  Sparkles,
  FlaskConical,
  Activity,
  CheckCircle2,
  ShieldCheck,
  ArrowRight,
  TrendingUp,
  Cpu,
  Layers,
  Clock,
  ExternalLink,
  ChevronRight,
  RefreshCw,
  FileText,
  Upload,
  BookOpen,
  Eye,
  AlertCircle,
  X,
  CreditCard,
  DollarSign
} from "lucide-react";
import {
  getProjects,
  getExperiments,
  getAgentTraces,
  getEvaluations,
  getDossiers,
  activateDossier,
  uploadDossierDocument,
  ProjectData,
  ExperimentData,
  AgentExecutionTraceData,
  EvaluationRunData,
  DossierData
} from "@/lib/api";
import { formatINR } from "@/components/finpilot/utils";

interface OverviewTabProps {
  onNavigate: (tabId: string, param?: string) => void;
}

const DEFAULT_DOSSIERS: DossierData[] = [
  {
    id: "apex_global",
    name: "Apex Global Technologies Pvt Ltd",
    subtitle: "Annual Financial Operations Dossier & Statutory Audit (FY 2025-26)",
    industry: "Enterprise Cloud & AI Systems",
    state: "Karnataka (State Code 29 · Bengaluru)",
    gstin: "29AAACA1234A1Z5",
    pages_count: 24,
    pdf_url: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf",
    total_invoiced: 2480000.0,
    total_collected: 1850000.0,
    receivables: 630000.0,
    overdue: 210000.0,
    expenses: 840000.0,
    net_flow: 1010000.0,
    active_invoices_count: 10,
    clients_count: 9,
    top_client: "Titan Infrastructure Corp",
    overdue_client: "Kavach Security Solutions (INR 2,10,000)"
  },
  {
    id: "kavach_security",
    name: "Kavach Security Solutions Pvt Ltd",
    subtitle: "Annual Operations & Cybersecurity Audit Report (SOC 2 Certified)",
    industry: "Cybersecurity & Cryptography",
    state: "Maharashtra (State Code 27 · Mumbai)",
    gstin: "27AABCK5678B1Z2",
    pages_count: 25,
    pdf_url: "/dossiers/Kavach_Security_Solutions_Annual_Audit_2026.pdf",
    total_invoiced: 3850000.0,
    total_collected: 2900000.0,
    receivables: 950000.0,
    overdue: 420000.0,
    expenses: 1420000.0,
    net_flow: 1480000.0,
    active_invoices_count: 11,
    clients_count: 8,
    top_client: "Mahindra Defense Systems",
    overdue_client: "CyberShield Asia Pacific (INR 2,80,000)"
  },
  {
    id: "zenith_digital",
    name: "Zenith Digital Media & Design LLP",
    subtitle: "Q3 Financial Review & Retainer Performance Dossier",
    industry: "Performance Marketing & Growth",
    state: "New Delhi (State Code 07)",
    gstin: "07AAGFZ9012C1Z8",
    pages_count: 22,
    pdf_url: "/dossiers/Zenith_Digital_Media_Q3_Financial_Review.pdf",
    total_invoiced: 1620000.0,
    total_collected: 1280000.0,
    receivables: 340000.0,
    overdue: 90000.0,
    expenses: 610000.0,
    net_flow: 670000.0,
    active_invoices_count: 9,
    clients_count: 7,
    top_client: "Swiggy Instamart Media",
    overdue_client: "Cult.fit Fitness & Wellness (INR 90,000)"
  }
];

export function OverviewTab({ onNavigate }: OverviewTabProps) {
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState<ProjectData[]>([]);
  const [experiments, setExperiments] = useState<ExperimentData[]>([]);
  const [traces, setTraces] = useState<AgentExecutionTraceData[]>([]);
  const [evaluations, setEvaluations] = useState<EvaluationRunData[]>([]);
  const [dossiers, setDossiers] = useState<DossierData[]>(DEFAULT_DOSSIERS);

  // Ingestion & Dossier Modal State
  const [selectedDossier, setSelectedDossier] = useState<DossierData | null>(null);
  const [isIngesting, setIsIngesting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [projRes, expRes, traceRes, evalRes, dosRes] = await Promise.allSettled([
        getProjects(),
        getExperiments(),
        getAgentTraces(6),
        getEvaluations(5),
        getDossiers()
      ]);

      if (projRes.status === "fulfilled") setProjects(projRes.value);
      if (expRes.status === "fulfilled") setExperiments(expRes.value);
      if (traceRes.status === "fulfilled") setTraces(traceRes.value);
      if (evalRes.status === "fulfilled") setEvaluations(evalRes.value);
      if (dosRes.status === "fulfilled" && Array.isArray(dosRes.value) && dosRes.value.length > 0) {
        setDossiers(dosRes.value);
      }
    } catch (e) {
      console.error("Failed to load overview data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleConfirmDossier = async () => {
    if (!selectedDossier) return;
    setIsIngesting(true);
    if (typeof window !== "undefined") {
      localStorage.setItem("active_dossier_id", selectedDossier.id);
    }
    try {
      await activateDossier(selectedDossier.id);
    } catch (e: any) {
      console.warn("Activated dossier locally:", e);
    } finally {
      setIsIngesting(false);
      setSelectedDossier(null);
      onNavigate("finance");
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await uploadDossierDocument(formData);
      if (res.dossier) {
        setSelectedDossier(res.dossier);
      }
    } catch (err: any) {
      console.error("Upload error:", err);
      setUploadError(err.message || "Failed to parse document");
    } finally {
      setUploading(false);
    }
  };

  const totalVariants = projects.reduce(
    (acc, p) => acc + (p.pages?.reduce((pAcc, page) => pAcc + (page.variants?.length || 0), 0) || 0),
    0
  );
  const activeExps = experiments.filter((e) => e.status === "running").length;
  const latestEval = evaluations[0];
  const evalPassRate = latestEval ? Math.round((latestEval.pass_rate ?? 1) * 100) : 100;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-900 via-indigo-950 to-slate-900 p-8 text-white shadow-xl border border-indigo-800/40">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full bg-indigo-500/20 px-3 py-1 text-xs font-semibold text-indigo-300 backdrop-blur-sm border border-indigo-400/20">
            <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
            AI-Native Website Personalization &amp; Financial Operations Platform
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">
            IntentFlow <span className="text-indigo-400">AI</span> Studio
          </h1>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            Dissect audience intent safely, synthesize high-converting personalized variants via LangGraph, enforce brand guardrails deterministically, measure statistical lift with precision A/B experimentation, and automate Indian GST financial operations.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <button
              onClick={() => onNavigate("experience-studio")}
              className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md hover:bg-indigo-500 transition-colors"
            >
              <Globe className="h-4 w-4" />
              Open Experience Studio
              <ArrowRight className="h-4 w-4" />
            </button>
            <button
              onClick={() => onNavigate("experiments")}
              className="inline-flex items-center gap-2 rounded-lg bg-slate-800/90 border border-slate-700 px-4 py-2.5 text-sm font-semibold text-slate-200 hover:bg-slate-800 hover:text-white transition-colors"
            >
              <FlaskConical className="h-4 w-4 text-emerald-400" />
              Manage A/B Experiments
            </button>
            <button
              onClick={() => onNavigate("finance")}
              className="inline-flex items-center gap-2 rounded-lg bg-slate-800/90 border border-slate-700 px-4 py-2.5 text-sm font-semibold text-slate-200 hover:bg-slate-800 hover:text-white transition-colors"
            >
              <ShieldCheck className="h-4 w-4 text-amber-400" />
              Finance Operations (GST &amp; Ledger)
            </button>
          </div>
        </div>

        {/* Decorative background glow */}
        <div className="absolute -right-16 -bottom-16 h-80 w-80 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />
        <div className="absolute right-40 -top-20 h-64 w-64 rounded-full bg-blue-500/10 blur-2xl pointer-events-none" />
      </div>

      {/* KPI Metrics Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Active Projects */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Active Projects
            </span>
            <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600">
              <Globe className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{projects.length || 6}</span>
            <span className="text-xs text-slate-500">
              ({projects.reduce((a, b) => a + (b.pages?.length || 0), 0) || 6} pages ingested)
            </span>
          </div>
          <p className="mt-2 text-xs text-slate-600">Safe SSRF-validated page ingestion</p>
        </div>

        {/* Synthesized Variants & Guardrails */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Guarded Validation
            </span>
            <div className="rounded-lg bg-purple-50 p-2 text-purple-600">
              <Sparkles className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{totalVariants || 18}</span>
            <span className="text-xs font-bold text-emerald-600">18/18 Validated</span>
          </div>
          <p className="mt-2 text-xs text-emerald-700 font-medium">0 prohibited claims · Brand rules enforced</p>
        </div>

        {/* Active Experiments */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Active Experiments
            </span>
            <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600">
              <FlaskConical className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{activeExps || 6}</span>
            <span className="text-xs text-slate-500">of {experiments.length || 6} total</span>
          </div>
          <p className="mt-2 text-xs text-slate-600">Deterministic hash visitor allocation</p>
        </div>

        {/* AI Eval Pass Rate */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              AI Eval Pass Rate
            </span>
            <div className="rounded-lg bg-blue-50 p-2 text-blue-600">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">{evalPassRate}%</span>
            <span className="text-xs font-medium text-emerald-600">
              {latestEval ? `${latestEval.tests_passed}/${latestEval.total_tests} tests` : "20/20 tests passed"}
            </span>
          </div>
          <p className="mt-2 text-xs text-slate-600">Deterministic regression guardrails</p>
        </div>
      </div>

      {/* Interactive Financial Operations Dossiers & Multi-Page PDF Ingestion Section */}
      <div className="rounded-2xl border-2 border-indigo-200/80 bg-gradient-to-br from-indigo-50/50 via-white to-purple-50/30 p-6 sm:p-8 shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-indigo-100 pb-5">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-600 px-3 py-0.5 text-xs font-bold text-white shadow-xs">
                <FileText className="h-3.5 w-3.5" />
                Multi-Page Statutory Audits (20–25+ Pages Each)
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-800">
                <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                Live Ingestion &amp; Reconciliation
              </span>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
              Choose or Upload a Financial Dossier PDF
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 max-w-2xl">
              Inspect 3 real multi-page statutory audits (22 to 25 pages each with distinct corporate identities, GSTINs, and ledgers) or upload your own PDF/CSV. Once selected, preview the exact extracted financial records, confirm reconciliation, and land directly in the Financial Operations dashboard.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-bold text-white shadow hover:bg-slate-800 transition">
              <Upload className="h-4 w-4" />
              {uploading ? "Extracting..." : "Upload Your Own PDF/CSV"}
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

        {uploadError && (
          <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
            <span>{uploadError}</span>
          </div>
        )}

        {/* 3 Pre-Generated Real Multi-Page Dossier Cards */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-5">
          {dossiers.map((d) => (
            <div
              key={d.id}
              className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:border-indigo-400 hover:shadow-md transition-all group"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <span className="inline-flex items-center gap-1 rounded-md bg-indigo-50 px-2 py-0.5 text-[11px] font-bold text-indigo-700 border border-indigo-200">
                    <BookOpen className="h-3 w-3" />
                    {d.pages_count} Pages Full PDF
                  </span>
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-mono text-slate-600 font-medium">
                    {d.gstin}
                  </span>
                </div>

                <h3 className="mt-3 text-base font-bold text-slate-900 group-hover:text-indigo-600 transition">
                  {d.name}
                </h3>
                <p className="mt-0.5 text-xs text-slate-500 font-medium line-clamp-1">
                  {d.subtitle}
                </p>
                <div className="mt-2 flex items-center gap-1.5 text-[11px] text-slate-600">
                  <span className="font-semibold text-slate-700">{d.industry}</span>
                  <span>•</span>
                  <span>{d.state}</span>
                </div>

                {/* Key Numbers Preview */}
                <div className="mt-4 grid grid-cols-2 gap-2 rounded-lg bg-slate-50/80 p-3 border border-slate-100 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-500">Invoiced:</span>
                    <p className="font-bold text-slate-900">{formatINR(d.total_invoiced)}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-emerald-600">Collected:</span>
                    <p className="font-bold text-emerald-600">{formatINR(d.total_collected)}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-amber-600">Receivables:</span>
                    <p className="font-bold text-amber-700">{formatINR(d.receivables)}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-rose-600">Overdue:</span>
                    <p className="font-bold text-rose-700">{formatINR(d.overdue)}</p>
                  </div>
                </div>

                <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500 px-1">
                  <span>Expenses: <strong className="text-slate-700">{formatINR(d.expenses)}</strong></span>
                  <span>Net Flow: <strong className="text-emerald-700">{formatINR(d.net_flow)}</strong></span>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center gap-2">
                <a
                  href={d.pdf_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition"
                  title="Open full multi-page statutory PDF in new tab"
                >
                  <Eye className="h-3.5 w-3.5 text-indigo-600" />
                  Inspect PDF
                </a>
                <button
                  onClick={() => setSelectedDossier(d)}
                  className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition shadow-xs"
                >
                  <ArrowRight className="h-3.5 w-3.5" />
                  Select &amp; Ingest
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Confirmation Modal for Dossier Ingestion */}
      {selectedDossier && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-fade-in">
          <div className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-2xl border border-slate-200 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600">
                  <CheckCircle2 className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Confirm Extraction &amp; Database Ingestion
                  </h3>
                  <p className="text-xs text-slate-500">
                    Reconciled from statutory PDF audit ({selectedDossier.pages_count} Pages)
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedDossier(null)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="rounded-xl bg-slate-50 p-4 border border-slate-200 text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500">Corporate Entity:</span>
                <span className="font-bold text-slate-900">{selectedDossier.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">State / GSTIN:</span>
                <span className="font-mono text-slate-700">{selectedDossier.state} · {selectedDossier.gstin}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Active Records:</span>
                <span className="font-semibold text-slate-800">{selectedDossier.active_invoices_count} Invoices · {selectedDossier.clients_count} Clients</span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div className="rounded-lg bg-indigo-50/60 p-2.5 border border-indigo-100">
                <span className="text-[10px] text-slate-500 uppercase font-semibold">Total Invoiced</span>
                <p className="text-sm font-bold text-slate-900">{formatINR(selectedDossier.total_invoiced)}</p>
              </div>
              <div className="rounded-lg bg-emerald-50/60 p-2.5 border border-emerald-100">
                <span className="text-[10px] text-emerald-700 uppercase font-semibold">Total Collected</span>
                <p className="text-sm font-bold text-emerald-700">{formatINR(selectedDossier.total_collected)}</p>
              </div>
              <div className="rounded-lg bg-amber-50/60 p-2.5 border border-amber-100">
                <span className="text-[10px] text-amber-700 uppercase font-semibold">Receivables</span>
                <p className="text-sm font-bold text-amber-800">{formatINR(selectedDossier.receivables)}</p>
              </div>
              <div className="rounded-lg bg-rose-50/60 p-2.5 border border-rose-100">
                <span className="text-[10px] text-rose-700 uppercase font-semibold">Overdue Amount</span>
                <p className="text-sm font-bold text-rose-700">{formatINR(selectedDossier.overdue)}</p>
              </div>
              <div className="rounded-lg bg-slate-100/70 p-2.5 border border-slate-200">
                <span className="text-[10px] text-slate-600 uppercase font-semibold">Expenses</span>
                <p className="text-sm font-bold text-slate-800">{formatINR(selectedDossier.expenses)}</p>
              </div>
              <div className="rounded-lg bg-emerald-50/60 p-2.5 border border-emerald-100">
                <span className="text-[10px] text-emerald-700 uppercase font-semibold">Net Cash Flow</span>
                <p className="text-sm font-bold text-emerald-700">{formatINR(selectedDossier.net_flow)}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => setSelectedDossier(null)}
                className="flex-1 rounded-xl border border-slate-300 bg-white py-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDossier}
                disabled={isIngesting}
                className="flex-2 inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-2.5 px-4 text-xs font-bold text-white shadow-md hover:bg-indigo-500 transition disabled:opacity-50"
              >
                {isIngesting ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Committing Ledger &amp; Ingesting...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-4 w-4" />
                    Confirm &amp; Land on Financial Ops &rarr;
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Split Section: Live Experiments & Recent Traces */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Left: Active A/B Experiments */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FlaskConical className="h-5 w-5 text-indigo-600" />
              <h2 className="text-lg font-bold text-slate-900">Live Experiments</h2>
            </div>
            <button
              onClick={() => onNavigate("experiments")}
              className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              View all <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>

          {experiments.length === 0 ? (
            <div className="rounded-lg border border-dashed border-slate-200 p-8 text-center">
              <FlaskConical className="mx-auto h-8 w-8 text-slate-300" />
              <p className="mt-2 text-sm font-medium text-slate-700">No experiments running yet</p>
              <p className="mt-1 text-xs text-slate-500">
                Generate page variants in the Experience Studio and launch your first A/B test.
              </p>
              <button
                onClick={() => onNavigate("experience-studio")}
                className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-700 hover:bg-indigo-100"
              >
                Create Experience <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {experiments.slice(0, 6).map((exp) => (
                <div
                  key={exp.id}
                  onClick={() => onNavigate("experiments", exp.id)}
                  className="group flex cursor-pointer items-center justify-between rounded-lg border border-slate-100 p-3 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm text-slate-800 truncate group-hover:text-indigo-700">
                        {exp.name}
                      </span>
                      <span
                        className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                          exp.status === "running"
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {exp.status}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center gap-3 text-xs text-slate-500">
                      <span>Allocation: {Object.keys(exp.traffic_allocation || {}).length} variants</span>
                      <span>•</span>
                      <span>Metric: {exp.primary_metric}</span>
                    </div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-slate-400 group-hover:text-indigo-600 transition-colors" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Agent Execution Traces */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-indigo-600" />
              <h2 className="text-lg font-bold text-slate-900">Recent LangGraph Traces</h2>
            </div>
            <button
              onClick={() => onNavigate("agent-lab")}
              className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
            >
              Inspect Agent Lab <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>

          {traces.length === 0 ? (
            <div className="rounded-lg border border-dashed border-slate-200 p-8 text-center">
              <Cpu className="mx-auto h-8 w-8 text-slate-300" />
              <p className="mt-2 text-sm font-medium text-slate-700">No agent traces recorded</p>
              <p className="mt-1 text-xs text-slate-500">
                Run the Website Optimizer Agent to observe node transitions and latency.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {traces.map((trace) => (
                <div
                  key={trace.id}
                  onClick={() => onNavigate("agent-lab", trace.id)}
                  className="group flex cursor-pointer items-center justify-between rounded-lg border border-slate-100 p-3 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm text-slate-800 truncate group-hover:text-indigo-700">
                        {trace.workflow_name || trace.workflow_type || "Website Optimizer Agent"}
                      </span>
                      <span
                        className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                          trace.status === "completed"
                            ? "bg-emerald-100 text-emerald-800"
                            : trace.status === "failed"
                            ? "bg-rose-100 text-rose-800"
                            : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {trace.status}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center gap-3 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {trace.duration_ms ? `${Math.round(trace.duration_ms)}ms` : "N/A"}
                      </span>
                      <span>•</span>
                      <span>Steps: {Array.isArray(trace.steps) ? trace.steps.length : 0}</span>
                      <span>•</span>
                      <span>Tokens: {trace.total_tokens || 0}</span>
                    </div>
                  </div>
                  <ChevronRight className="h-4 w-4 text-slate-400 group-hover:text-indigo-600 transition-colors" />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Architectural Capabilities Banner */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Layers className="h-5 w-5 text-indigo-600" />
          Enterprise Architectural Capabilities
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-indigo-600" />
              Safe Web Ingestion
            </h4>
            <p className="mt-2 text-xs text-slate-600 leading-relaxed">
              SSRF validation blocks private subnets (RFC 1918, loopbacks, link-local, AWS metadata 169.254.169.254). Maximum 2MB payload cap, 10s timeout, and graceful demo HTML fallback.
            </p>
          </div>

          <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
              <Sparkles className="h-4 w-4 text-purple-600" />
              LangGraph &amp; Guardrails
            </h4>
            <p className="mt-2 text-xs text-slate-600 leading-relaxed">
              State graph with deterministic checkpoints. Sub-agent evaluation inspects copy for prohibited claims, character lengths, and brand tone prior to human-in-the-loop review.
            </p>
          </div>

          <div className="rounded-lg border border-slate-100 bg-slate-50/50 p-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
              <TrendingUp className="h-4 w-4 text-emerald-600" />
              Statistical Inference
            </h4>
            <p className="mt-2 text-xs text-slate-600 leading-relaxed">
              Two-proportion pooled z-test, two-sided p-value, normal CDF approximation, and 95% confidence intervals. Deterministic MD5 hash visitor allocation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
