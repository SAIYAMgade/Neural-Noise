"use client";

import React, { useState, useEffect } from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RotateCw,
  Play,
  ShieldCheck,
  Award,
  Layers,
  Clock,
  Sparkles,
  Info
} from "lucide-react";
import { getEvaluations, runEvaluationSuite, EvaluationRunData } from "@/lib/api";

export function EvaluationsTab() {
  const [evaluations, setEvaluations] = useState<EvaluationRunData[]>([]);
  const [running, setRunning] = useState(false);
  const [selectedRun, setSelectedRun] = useState<EvaluationRunData | null>(null);
  const [notification, setNotification] = useState<string | null>(null);

  const loadEvaluations = async () => {
    try {
      const data = await getEvaluations(10);
      setEvaluations(data);
      if (data.length > 0 && !selectedRun) {
        setSelectedRun(data[0]);
      }
    } catch (err) {
      console.error("Failed to load evaluations", err);
    }
  };

  useEffect(() => {
    loadEvaluations();
  }, []);

  const handleRunSuite = async () => {
    setRunning(true);
    try {
      const run = await runEvaluationSuite();
      setNotification(`Evaluation completed! ${run.tests_passed ?? run.passed_cases ?? 0}/${run.total_tests ?? run.total_cases ?? 0} tests passed (${Math.round((run.pass_rate ?? 1) * 100)}%).`);
      await loadEvaluations();
      setSelectedRun(run);
      setTimeout(() => setNotification(null), 4000);
    } catch (err: any) {
      console.error("Failed to run evaluation suite", err);
    } finally {
      setRunning(false);
    }
  };

  const activeRun = selectedRun || evaluations[0];
  const passRate = activeRun ? Math.round((activeRun.pass_rate ?? 1) * 100) : 100;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-indigo-600" />
            AI Evaluations & Regression Guardrails
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Automated test battery verifying brand guardrails, character constraints, JSON schema validity, and financial precision.
          </p>
        </div>

        <button
          onClick={handleRunSuite}
          disabled={running}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-bold text-white shadow hover:bg-indigo-500 disabled:opacity-50 transition-colors"
        >
          {running ? (
            <>
              <RotateCw className="h-4 w-4 animate-spin" />
              Running Test Battery...
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              Run Evaluation Suite
            </>
          )}
        </button>
      </div>

      {notification && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-50 border border-emerald-200 p-4 text-sm font-medium text-emerald-800 shadow-sm">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 flex-shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Total Test Cases
          </span>
          <div className="mt-2 text-2xl font-bold text-slate-900">
            {activeRun?.total_tests || 0}
          </div>
          <p className="mt-1 text-xs text-slate-500">Across 4 quality dimensions</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Tests Passed
          </span>
          <div className="mt-2 text-2xl font-bold text-emerald-600">
            {activeRun?.tests_passed || 0}
          </div>
          <p className="mt-1 text-xs text-slate-500">Zero regressions tolerated</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Pass Rate
          </span>
          <div className="mt-2 text-2xl font-bold text-indigo-600">
            {passRate}%
          </div>
          <p className="mt-1 text-xs text-slate-500">Target: 100% compliance</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Suite Duration
          </span>
          <div className="mt-2 text-2xl font-bold text-slate-800">
            {activeRun?.duration_ms ? `${Math.round(activeRun.duration_ms)}ms` : "Fast"}
          </div>
          <p className="mt-1 text-xs text-slate-500">Deterministic regression checks</p>
        </div>
      </div>

      {/* Main Breakdown: Test Cases Grid */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Award className="h-5 w-5 text-indigo-600" />
          Test Results Breakdown: {activeRun?.suite_name || "IntentFlow Core Regression Suite"}
        </h3>

        {activeRun?.results && Array.isArray(activeRun.results) ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {activeRun.results.map((tc: any, idx: number) => {
              const isPass = tc.status === "passed" || tc.passed === true;

              return (
                <div
                  key={idx}
                  className={`rounded-lg border p-4 transition-all ${
                    isPass
                      ? "border-emerald-200 bg-emerald-50/20"
                      : "border-rose-200 bg-rose-50/20"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      {isPass ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0" />
                      ) : (
                        <XCircle className="h-4 w-4 text-rose-600 flex-shrink-0" />
                      )}
                      {tc.test_name || `Test Case ${idx + 1}`}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        isPass ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
                      }`}
                    >
                      {isPass ? "PASSED" : "FAILED"}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed">
                    {tc.description || "Validates deterministic behavior and outputs."}
                  </p>

                  {tc.details && (
                    <div className="mt-2 rounded bg-slate-50 p-2 font-mono text-[10px] text-slate-700">
                      {typeof tc.details === "string"
                        ? tc.details
                        : JSON.stringify(tc.details, null, 2)}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-slate-500">
            Click &quot;Run Evaluation Suite&quot; above to execute automated tests against your agent models and guardrails.
          </div>
        )}
      </div>

      {/* History List */}
      {evaluations.length > 1 && (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3">
            Evaluation Run History
          </h4>
          <div className="divide-y divide-slate-100">
            {evaluations.map((ev) => (
              <div
                key={ev.id}
                onClick={() => setSelectedRun(ev)}
                className={`flex cursor-pointer items-center justify-between py-2.5 px-3 rounded hover:bg-slate-50 transition-colors ${
                  selectedRun?.id === ev.id ? "bg-indigo-50/50 font-semibold" : ""
                }`}
              >
                <div className="flex items-center gap-2 text-xs text-slate-800">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                  <span>{ev.suite_name}</span>
                  <span className="text-slate-400 font-normal">
                    ({new Date(ev.created_at).toLocaleString()})
                  </span>
                </div>
                <div className="text-xs font-mono font-bold text-indigo-700">
                  {Math.round((ev.pass_rate ?? 1) * 100)}% ({ev.tests_passed ?? ev.passed_cases ?? 0}/{ev.total_tests ?? ev.total_cases ?? 0})
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
