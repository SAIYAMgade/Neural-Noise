import { getBaseUrl } from "@/lib/api";
"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  TrendingUp,
  Shield,
  BarChart3,
  Brain,
  Sparkles,
  ArrowRight,
  Upload,
  RefreshCw,
  FileSpreadsheet,
  CheckCircle2,
  Lock,
} from "lucide-react";
import { startDemo, startAnalysis } from "@/lib/api";

// getBaseUrl imported from @/lib/api

const FEATURES = [
  {
    icon: BarChart3,
    title: "Monte Carlo Survival Simulation",
    desc: "1,000+ stochastic iterations predicting cash runway, ruin probability, and survival horizon.",
  },
  {
    icon: Shield,
    title: "IsolationForest ML Anomaly AI",
    desc: "Unsupervised machine learning identifying irregular transaction spikes, churn anomalies, and leaks.",
  },
  {
    icon: TrendingUp,
    title: "Scenario & Sensitivity Engine",
    desc: "Stress-tests business resilience across Bear, Base, and Bull operational scenarios.",
  },
  {
    icon: Brain,
    title: "Autonomous Board & CFO Reporting",
    desc: "Automated executive summary generation, VC memos, and board deck question answering.",
  },
];

export function AnalyticsTab() {
  const router = useRouter();
  const [runningDemo, setRunningDemo] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [companyName, setCompanyName] = useState("FinPilot Independent Studio");

  const handleLaunchDemo = async () => {
    setRunningDemo(true);
    try {
      const runId = crypto.randomUUID();
      sessionStorage.setItem(
        `run_${runId}`,
        JSON.stringify({ run_id: runId, company_name: companyName, sector: "saas_productivity" })
      );

      const params = new URLSearchParams({
        run_id: runId,
        company_name: companyName,
        sector: "saas_productivity",
      });
      await fetch(`${getBaseUrl()}/demo/async?${params}`, { method: "POST" });
      router.push(`/run/${runId}`);
    } catch (err: any) {
      alert(`Demo pipeline trigger failed: ${err.message || "Error"}`);
      setRunningDemo(false);
    }
  };

  const handleUploadAndAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    try {
      const runId = crypto.randomUUID();
      sessionStorage.setItem(
        `run_${runId}`,
        JSON.stringify({ run_id: runId, company_name: companyName, sector: "saas_productivity" })
      );

      const form = new FormData();
      form.append("file", file);
      form.append("run_id", runId);
      form.append("company_name", companyName);
      form.append("sector", "saas_productivity");

      await fetch(`${getBaseUrl()}/analyze/async`, { method: "POST", body: form });
      router.push(`/run/${runId}`);
    } catch (err: any) {
      alert(`Analysis failed: ${err.message || "Error"}`);
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">Deep Financial Analytics &amp; Runway AI</h2>
        <p className="text-xs text-slate-500">
          Stochastic simulations, machine learning anomaly detection, and executive reporting for your venture.
        </p>
      </div>

      {/* Hero Action Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-950 via-slate-900 to-indigo-900 p-8 text-white shadow-xl">
        <div className="absolute right-0 top-0 -mt-8 -mr-8 h-80 w-80 rounded-full bg-indigo-500/20 blur-3xl" />
        <div className="relative z-10 max-w-2xl">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-500/20 px-3 py-1 text-xs font-semibold text-indigo-300 border border-indigo-500/30">
            <Sparkles className="h-3.5 w-3.5" /> Multi-Agent Intelligence Pipeline
          </span>
          <h3 className="mt-3 text-2xl font-bold text-white">
            Run Full Multi-Agent Intelligence Engine
          </h3>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            Execute the complete financial analysis pipeline with Monte Carlo simulations, Polars data processing, IsolationForest anomaly detection, and real-time WebSocket progress streaming.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              onClick={handleLaunchDemo}
              disabled={runningDemo}
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-semibold text-white shadow-md hover:bg-indigo-500 transition disabled:opacity-50"
            >
              {runningDemo ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Spinning Pipeline Agents...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Launch Interactive Demo Pipeline
                  <ArrowRight className="h-4 w-4 ml-1" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Feature Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {FEATURES.map((feat, idx) => (
          <div
            key={idx}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs hover:border-indigo-300 hover:shadow-md transition"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
              <feat.icon className="h-5 w-5" />
            </div>
            <h4 className="mt-3 text-sm font-bold text-slate-900">{feat.title}</h4>
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">{feat.desc}</p>
          </div>
        ))}
      </div>

      {/* Custom CSV Upload Section */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-3 mb-4">
          <FileSpreadsheet className="h-5 w-5 text-indigo-600" />
          <div>
            <h3 className="text-sm font-bold text-slate-900">Analyze Custom Transactions CSV</h3>
            <p className="text-xs text-slate-500">
              Upload a 4-column CSV (<code className="font-mono">date, category, amount, customer_id</code>) for automated multi-agent analysis.
            </p>
          </div>
        </div>

        <form onSubmit={handleUploadAndAnalyze} className="space-y-4 max-w-xl">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Venture / Business Name
            </label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="w-full rounded-xl border border-slate-200 p-2 text-xs text-slate-800 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Select CSV File
            </label>
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full rounded-xl border border-slate-200 p-2 text-xs text-slate-800 focus:border-indigo-500 focus:outline-none file:mr-3 file:py-1 file:px-2.5 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
            />
          </div>

          <button
            type="submit"
            disabled={!file || uploading}
            className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-xs font-semibold text-white shadow hover:bg-slate-800 transition disabled:opacity-40"
          >
            {uploading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                Ingesting and Processing...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Analyze Uploaded Transactions
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
