"use client";

import React, { useState, useEffect } from "react";
import {
  FlaskConical,
  TrendingUp,
  Activity,
  Play,
  RotateCw,
  CheckCircle2,
  AlertTriangle,
  Users,
  Zap,
  BarChart2,
  Sliders,
  Sparkles,
  Info
} from "lucide-react";
import {
  getExperiments,
  getExperimentMetrics,
  simulateTraffic,
  ExperimentData,
  ExperimentMetricsData
} from "@/lib/api";

interface ExperimentsTabProps {
  initialExperimentId?: string;
}

export function ExperimentsTab({ initialExperimentId }: ExperimentsTabProps) {
  const [experiments, setExperiments] = useState<ExperimentData[]>([]);
  const [selectedExpId, setSelectedExpId] = useState<string>(initialExperimentId || "");
  const [metrics, setMetrics] = useState<ExperimentMetricsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [simulating, setSimulating] = useState(false);

  // Simulation parameters
  const [simVisitors, setSimVisitors] = useState<number>(500);
  const [simControlCr, setSimControlCr] = useState<number>(0.07);
  const [simVariantCr, setSimVariantCr] = useState<number>(0.11);
  const [notification, setNotification] = useState<string | null>(null);

  const loadExperiments = async () => {
    try {
      const data = await getExperiments();
      setExperiments(data);
      if (data.length > 0) {
        if (!selectedExpId || !data.some((e) => e.id === selectedExpId)) {
          setSelectedExpId(data[0].id);
        }
      }
    } catch (err) {
      console.error("Failed to load experiments", err);
    }
  };

  useEffect(() => {
    loadExperiments();
  }, []);

  useEffect(() => {
    if (initialExperimentId) {
      setSelectedExpId(initialExperimentId);
    }
  }, [initialExperimentId]);

  const loadMetrics = async (expId: string) => {
    if (!expId) return;
    setLoading(true);
    try {
      const m = await getExperimentMetrics(expId);
      setMetrics(m);
    } catch (err) {
      console.error("Failed to fetch experiment metrics", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedExpId) {
      loadMetrics(selectedExpId);
    }
  }, [selectedExpId]);

  const handleSimulate = async () => {
    if (!selectedExpId) return;
    setSimulating(true);
    try {
      const res = await simulateTraffic(selectedExpId, {
        total_visitors: simVisitors,
        control_cr: simControlCr,
        variant_cr: simVariantCr
      });
      setNotification(`Simulated ${res.total_visitors} visitors (${res.total_conversions} conversions)! Metrics updated.`);
      await loadMetrics(selectedExpId);
      setTimeout(() => setNotification(null), 4000);
    } catch (err: any) {
      console.error("Simulation error", err);
    } finally {
      setSimulating(false);
    }
  };

  const activeExp = experiments.find((e) => e.id === selectedExpId);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-indigo-600" />
            A/B Experimentation & Statistical Engine
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time inference using two-proportion pooled z-tests, normal CDF p-values, 95% confidence intervals, and deterministic visitor allocation.
          </p>
        </div>

        {experiments.length > 0 && (
          <div className="flex items-center gap-3">
            <label className="text-xs font-semibold text-slate-600">Select Experiment:</label>
            <select
              value={selectedExpId}
              onChange={(e) => setSelectedExpId(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-800 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {experiments.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name} ({e.status})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {notification && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-50 border border-emerald-200 p-4 text-sm font-medium text-emerald-800 shadow-sm">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 flex-shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {experiments.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-200 bg-white p-12 text-center shadow-sm">
          <FlaskConical className="mx-auto h-12 w-12 text-slate-300" />
          <h3 className="mt-4 text-base font-bold text-slate-900">No active experiments yet</h3>
          <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto">
            Head to the Experience Studio, generate page variants with the LangGraph agent, approve them, and launch your first A/B test.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Top High-level Overview Cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Total Exposures
              </span>
              <div className="mt-2 text-2xl font-bold text-slate-900">
                {metrics?.total_visitors || 0}
              </div>
              <p className="mt-1 text-xs text-slate-500">Unique visitors allocated</p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Total Conversions
              </span>
              <div className="mt-2 text-2xl font-bold text-slate-900">
                {metrics?.total_conversions || 0}
              </div>
              <p className="mt-1 text-xs text-slate-500">Goal: {activeExp?.primary_metric || "cta_click"}</p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Pooled CR
              </span>
              <div className="mt-2 text-2xl font-bold text-indigo-600">
                {metrics?.total_visitors && metrics.total_visitors > 0
                  ? `${((metrics.total_conversions / metrics.total_visitors) * 100).toFixed(2)}%`
                  : "0.00%"}
              </div>
              <p className="mt-1 text-xs text-slate-500">Baseline across all variants</p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Status & Allocation
              </span>
              <div className="mt-2 flex items-center gap-2">
                <span className="inline-flex rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-bold text-emerald-800">
                  {activeExp?.status || "running"}
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-500">Deterministic MD5 partitioning</p>
            </div>
          </div>

          {/* Statistical Breakdown: Control vs Variants */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <BarChart2 className="h-5 w-5 text-indigo-600" />
                <h3 className="text-base font-bold text-slate-900">Statistical Significance & Lift Breakdown</h3>
              </div>
              <button
                onClick={() => selectedExpId && loadMetrics(selectedExpId)}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
              >
                <RotateCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
                Refresh
              </button>
            </div>

            {/* Variants Comparison Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-slate-600 border-b border-slate-200">
                  <tr>
                    <th className="py-3 px-4">Variant</th>
                    <th className="py-3 px-4">Visitors</th>
                    <th className="py-3 px-4">Conversions</th>
                    <th className="py-3 px-4">Conv. Rate (CR)</th>
                    <th className="py-3 px-4">Relative Lift</th>
                    <th className="py-3 px-4">Z-Score</th>
                    <th className="py-3 px-4">P-Value</th>
                    <th className="py-3 px-4">Significance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {(() => {
                    const variantsList: any[] = Array.isArray(metrics?.variants)
                      ? metrics.variants
                      : metrics?.variants
                      ? Object.values(metrics.variants)
                      : [];
                    const controlItem = variantsList.find((v: any) => v.is_control) || metrics?.control;
                    const testedVariants = variantsList.filter((v: any) => !v.is_control);

                    return (
                      <>
                        {/* Control Row */}
                        {controlItem && (
                          <tr className="bg-slate-50/40 font-medium">
                            <td className="py-3.5 px-4 font-bold text-slate-800 flex items-center gap-2">
                              <span className="h-2 w-2 rounded-full bg-slate-400" />
                              {controlItem.variant_name || "Control (Baseline)"}
                            </td>
                            <td className="py-3.5 px-4 font-mono">{controlItem.exposures ?? controlItem.visitors ?? 0}</td>
                            <td className="py-3.5 px-4 font-mono">{controlItem.conversions ?? 0}</td>
                            <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                              {typeof controlItem.conversion_rate === "number"
                                ? controlItem.conversion_rate.toFixed(2)
                                : "0.00"}%
                            </td>
                            <td className="py-3.5 px-4 text-slate-400 font-mono">-</td>
                            <td className="py-3.5 px-4 text-slate-400 font-mono">-</td>
                            <td className="py-3.5 px-4 text-slate-400 font-mono">-</td>
                            <td className="py-3.5 px-4">
                              <span className="text-[11px] text-slate-500">Baseline Reference</span>
                            </td>
                          </tr>
                        )}

                        {/* Tested Variants Rows */}
                        {testedVariants.map((vData: any, idx: number) => {
                          const isSignificant = vData.is_significant || vData.significant;
                          const hasWarning = vData.sample_size_warning;
                          const relLift = vData.relative_lift_pct ?? vData.relative_lift ?? 0;
                          const liftPositive = relLift >= 0;

                          return (
                            <tr key={vData.variant_id || idx} className="hover:bg-slate-50/80 transition-colors">
                              <td className="py-3.5 px-4 font-bold text-indigo-950 flex items-center gap-2">
                                <span className="h-2 w-2 rounded-full bg-indigo-600" />
                                {vData.variant_name || vData.name || `Variant ${String.fromCharCode(65 + idx)}`}
                              </td>
                              <td className="py-3.5 px-4 font-mono">{vData.exposures ?? vData.visitors ?? 0}</td>
                              <td className="py-3.5 px-4 font-mono">{vData.conversions ?? 0}</td>
                              <td className="py-3.5 px-4 font-mono font-bold text-indigo-700">
                                {typeof vData.conversion_rate === "number"
                                  ? vData.conversion_rate.toFixed(2)
                                  : "0.00"}%
                              </td>
                              <td className={`py-3.5 px-4 font-mono font-bold ${liftPositive ? "text-emerald-600" : "text-rose-600"}`}>
                                {liftPositive ? "+" : ""}
                                {Number(relLift).toFixed(1)}%
                              </td>
                              <td className="py-3.5 px-4 font-mono text-slate-700">
                                {vData.z_score !== null && vData.z_score !== undefined
                                  ? Number(vData.z_score).toFixed(3)
                                  : "N/A"}
                              </td>
                              <td className="py-3.5 px-4 font-mono text-slate-700">
                                {vData.p_value !== null && vData.p_value !== undefined
                                  ? Number(vData.p_value).toFixed(4)
                                  : "N/A"}
                              </td>
                              <td className="py-3.5 px-4">
                                {hasWarning ? (
                                  <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full">
                                    <AlertTriangle className="h-3 w-3" />
                                    Low Sample ({vData.exposures ?? vData.visitors ?? 0})
                                  </span>
                                ) : isSignificant ? (
                                  <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                                    <CheckCircle2 className="h-3 w-3" />
                                    Significant (p &lt; 0.05)
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full">
                                    Inconclusive
                                  </span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </>
                    );
                  })()}
                </tbody>
              </table>
            </div>

            {/* Confidence Interval Explainer */}
            {metrics?.variants && Object.values(metrics.variants).some((v) => v.confidence_interval_95) && (
              <div className="mt-4 rounded-lg bg-indigo-50/50 border border-indigo-100 p-3 text-xs text-indigo-900">
                <span className="font-bold flex items-center gap-1.5 mb-1">
                  <Info className="h-4 w-4 text-indigo-600" />
                  Statistical Rigor Note:
                </span>
                Confidence intervals are computed using the standard error of difference between two independent proportions. If 0 is not in the 95% CI and p &lt; 0.05, the observed lift is statistically defensible against the null hypothesis.
              </div>
            )}
          </div>

          {/* 1-Click Synthetic Traffic Simulator */}
          <div className="rounded-xl border border-indigo-200 bg-gradient-to-br from-indigo-50/30 via-white to-purple-50/30 p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Zap className="h-5 w-5 text-indigo-600" />
              <h3 className="text-base font-bold text-slate-900">
                1-Click Synthetic Traffic Simulator
              </h3>
            </div>
            <p className="text-xs text-slate-600 mb-5 max-w-2xl leading-relaxed">
              Generate realistic synthetic visitor streams using binomial random sampling. Evaluates how the statistical inference engine detects conversion anomalies and lifts in real time.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Visitor Volume
                </label>
                <input
                  type="number"
                  min="50"
                  max="5000"
                  step="50"
                  value={simVisitors}
                  onChange={(e) => setSimVisitors(parseInt(e.target.value) || 200)}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-mono text-slate-800"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Expected Baseline CR (Control)
                </label>
                <input
                  type="number"
                  min="0.01"
                  max="0.50"
                  step="0.01"
                  value={simControlCr}
                  onChange={(e) => setSimControlCr(parseFloat(e.target.value) || 0.05)}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-mono text-slate-800"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Expected Variant CR (Hypothesis)
                </label>
                <input
                  type="number"
                  min="0.01"
                  max="0.50"
                  step="0.01"
                  value={simVariantCr}
                  onChange={(e) => setSimVariantCr(parseFloat(e.target.value) || 0.1)}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-mono text-slate-800"
                />
              </div>
            </div>

            <button
              onClick={handleSimulate}
              disabled={simulating || !selectedExpId}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 transition-colors"
            >
              {simulating ? (
                <>
                  <RotateCw className="h-4 w-4 animate-spin" />
                  Simulating Traffic Stream & Calculating Z-Scores...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Simulate {simVisitors} Visitors
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
