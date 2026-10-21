"use client";

import React, { useState } from "react";
import {
  GitFork,
  Workflow,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  ArrowRight,
  ArrowDown,
  Layers,
  Code2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2,
  FileText,
  Database,
  LineChart,
  TrendingUp,
  HelpCircle,
  Copy,
  Check,
  ExternalLink
} from "lucide-react";

interface NodeSpec {
  id: string;
  name: string;
  pythonHandler: string;
  agent: string;
  inputs: string[];
  outputs: string[];
  description: string;
  type: "router" | "agent" | "loop" | "database" | "terminal";
}

const GRAPH_NODES: NodeSpec[] = [
  {
    id: "router",
    name: "Router Node",
    pythonHandler: "CFOGraphRunner._router_node",
    agent: "CFOGraphRouter",
    inputs: ["task", "run_id"],
    outputs: ["task", "run_id", "messages", "correction_attempts"],
    description: "Evaluates task payload ('analyze', 'report', 'board_prep') and conditionally routes execution to the target starting agent. Publishes pipeline_started WebSocket event.",
    type: "router"
  },
  {
    id: "ingestion",
    name: "Ingestion Agent",
    pythonHandler: "CFOGraphRunner._ingestion_node",
    agent: "IngestionAgent",
    inputs: ["file_name", "file_bytes", "company_name", "sector"],
    outputs: ["raw_rows", "validated_rows", "validation_errors", "needs_correction"],
    description: "Parses CSV/Excel bank feeds and statutory ledgers. Computes SHA256 checksums, validates columns against strict financial schemas, and triggers self-healing if parse errors occur.",
    type: "agent"
  },
  {
    id: "correction",
    name: "Self-Healing Correction Loop",
    pythonHandler: "CFOGraphRunner._correction_node",
    agent: "IngestionAgent (LLM Reflection)",
    inputs: ["validation_errors", "raw_rows", "correction_attempts"],
    outputs: ["corrected_rows", "correction_attempts"],
    description: "Cyclic LangGraph reflection loop: automatically analyzes schema discrepancies, misaligned date formats, and corrupted ledger amounts using structured LLM repair without data loss.",
    type: "loop"
  },
  {
    id: "persist_raw",
    name: "Persist Raw SQL Node",
    pythonHandler: "CFOGraphRunner._persist_raw_node",
    agent: "DatabaseManager",
    inputs: ["validated_rows", "run_id"],
    outputs: ["persisted_count"],
    description: "Executes atomic double-entry database writes to PostgreSQL/SQLite, recording sanitized ledger transactions with foreign key verification.",
    type: "database"
  },
  {
    id: "analysis",
    name: "Analysis Agent: Runway & Monte Carlo",
    pythonHandler: "CFOGraphRunner._analysis_node",
    agent: "AnalysisAgent",
    inputs: ["validated_rows", "persisted_count"],
    outputs: ["kpis", "anomalies", "survival_analysis", "scenario_analysis"],
    description: "Deterministic financial computation: calculates net burn rate, runway months, cash velocity, Monte Carlo fan simulations (1,000 runs), and statistical Z-score fraud/anomaly detection.",
    type: "agent"
  },
  {
    id: "market_analyze",
    name: "Market Intelligence & Benchmarks",
    pythonHandler: "CFOGraphRunner._market_analyze_node",
    agent: "MarketAgent",
    inputs: ["kpis", "sector"],
    outputs: ["market_signals"],
    description: "Enriches internal runway metrics with live macroeconomic indicators, sector peer multiples (SaaS, FinTech, Media), and benchmark valuation comparisons.",
    type: "agent"
  },
  {
    id: "market",
    name: "Market Agent (Report Flow)",
    pythonHandler: "CFOGraphRunner._market_node",
    agent: "MarketAgent",
    inputs: ["company_name", "sector"],
    outputs: ["market_signals"],
    description: "Gathers competitor landscape data, funding activity, and sector headwind analyses for executive reporting without running full ledger ingestion.",
    type: "agent"
  },
  {
    id: "insight",
    name: "Insight Writer: Memos & VC Decks",
    pythonHandler: "CFOGraphRunner._insight_node",
    agent: "InsightWriterAgent",
    inputs: ["market_signals", "company_name", "sector"],
    outputs: ["executive_summary", "full_report_markdown"],
    description: "Generates institutional-grade executive memos, board memos, and risk pre-mortems grounded in verified ledger data and external sector telemetry.",
    type: "agent"
  },
  {
    id: "board_prep",
    name: "Board Prep Agent",
    pythonHandler: "CFOGraphRunner._board_prep_node",
    agent: "BoardPrepAgent",
    inputs: ["company_name", "sector"],
    outputs: ["board_questions"],
    description: "Simulates adversarial VC partner and audit board committee interrogation, producing targeted counter-arguments and sensitivity stress tests.",
    type: "agent"
  },
  {
    id: "failure",
    name: "Failure Node",
    pythonHandler: "CFOGraphRunner._failure_node",
    agent: "CFOGraphRunner",
    inputs: ["validation_errors", "error"],
    outputs: ["status", "error"],
    description: "Graceful terminal recovery node capturing fatal validation exceptions, uncorrectable corrupt data, and broadcasting diagnostic alert payloads.",
    type: "terminal"
  }
];

const MERMAID_CODE = `flowchart TD
    START([START]) --> router[Router Node]
    
    router -->|task == analyze| ingestion[Ingestion Agent]
    router -->|task == report| market[Market Agent]
    router -->|task == board_prep| board_prep[Board Prep Agent]
    
    ingestion -->|schema errors| correction[Self-Healing Correction Loop]
    correction -->|retry fixed data| ingestion
    ingestion -->|fatal errors| failure[Failure Node]
    ingestion -->|clean data| persist_raw[Persist Raw SQL Node]
    
    persist_raw --> analysis[Analysis Agent: Runway & Monte Carlo]
    analysis --> market_analyze[Market Intelligence & Benchmarks]
    market_analyze --> END([END])
    
    market --> insight[Insight Writer: Memos & VC Decks]
    insight --> END
    board_prep --> END
    failure --> END`;

export function FlowchartTab() {
  const [activeView, setActiveView] = useState<"diagram" | "nodes" | "code">("diagram");
  const [selectedNode, setSelectedNode] = useState<NodeSpec>(GRAPH_NODES[0]);
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [copied, setCopied] = useState<boolean>(false);
  const [fullscreenModal, setFullscreenModal] = useState<boolean>(false);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(MERMAID_CODE);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-zinc-950 via-zinc-900 to-zinc-950 border border-zinc-800 p-6 shadow-xl">
        <div className="absolute top-0 right-0 h-48 w-48 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-500/10 px-3 py-1 text-xs font-semibold text-rose-400 border border-rose-500/20">
                <Workflow className="h-3.5 w-3.5" />
                LangGraph State Machine
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-400 border border-blue-500/20">
                <GitFork className="h-3.5 w-3.5" />
                Multi-Agent Architecture
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Bounded Memory Saver (200 Cap)
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              LangGraph Multi-Agent Flowchart
            </h1>
            <p className="text-sm text-zinc-400 max-w-3xl leading-relaxed">
              Visual topology of the Autonomous CFO execution graph (<code className="text-rose-400 bg-zinc-900 px-1 py-0.5 rounded text-xs">graph/cfo_graph.py</code>).
              Coordinates ingestion, cyclic self-healing reflection, double-entry SQL persistence, deterministic Monte Carlo runway simulations, and board governance.
            </p>
          </div>

          {/* View Mode Switcher */}
          <div className="flex items-center bg-zinc-900 border border-zinc-800 rounded-xl p-1 gap-1 self-start md:self-auto shrink-0">
            <button
              onClick={() => setActiveView("diagram")}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeView === "diagram"
                  ? "bg-rose-500 text-white shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Diagram View
            </button>
            <button
              onClick={() => setActiveView("nodes")}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeView === "nodes"
                  ? "bg-rose-500 text-white shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Node Inspector
            </button>
            <button
              onClick={() => setActiveView("code")}
              className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeView === "code"
                  ? "bg-rose-500 text-white shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Mermaid Code
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {activeView === "diagram" && (
        <div className="space-y-4">
          {/* Controls Bar */}
          <div className="flex items-center justify-between bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5">
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <span className="font-semibold text-zinc-300">Topology:</span>
              <span>10 Nodes</span>
              <span className="text-zinc-700">•</span>
              <span>3 Conditional Branches</span>
              <span className="text-zinc-700">•</span>
              <span className="text-amber-400 font-medium">1 Cyclical Self-Healing Edge</span>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setZoomLevel((z) => Math.max(0.7, z - 0.15))}
                className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors"
                title="Zoom Out"
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              <span className="text-xs font-mono text-zinc-400 min-w-[48px] text-center">
                {Math.round(zoomLevel * 100)}%
              </span>
              <button
                onClick={() => setZoomLevel((z) => Math.min(1.8, z + 0.15))}
                className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors"
                title="Zoom In"
              >
                <ZoomIn className="h-4 w-4" />
              </button>
              <button
                onClick={() => setZoomLevel(1)}
                className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors"
                title="Reset Zoom"
              >
                <RotateCcw className="h-4 w-4" />
              </button>
              <div className="h-4 w-px bg-zinc-800 mx-1" />
              <button
                onClick={() => setFullscreenModal(true)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs font-semibold text-zinc-200 hover:text-white hover:bg-zinc-800 transition-colors"
              >
                <Maximize2 className="h-3.5 w-3.5" />
                Fullscreen
              </button>
            </div>
          </div>

          {/* Diagram Canvas */}
          <div className="relative rounded-2xl border border-zinc-800 bg-[#0d0e12] p-6 flex flex-col items-center justify-center overflow-auto min-h-[580px] shadow-2xl">
            {/* Background Dot Grid */}
            <div
              className="absolute inset-0 opacity-[0.08] pointer-events-none"
              style={{
                backgroundImage: "radial-gradient(#ffffff 1px, transparent 1px)",
                backgroundSize: "24px 24px"
              }}
            />

            <div
              className="transition-transform duration-200 ease-out origin-top flex items-center justify-center"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              {/* Render the LangGraph Flowchart Diagram */}
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/images/langgraph-cfo-flowchart.png"
                alt="LangGraph Multi-Agent Architecture Flowchart"
                className="max-w-[850px] w-full h-auto rounded-xl shadow-2xl border border-zinc-800/80 bg-zinc-950/90"
              />
            </div>
          </div>

          {/* Explanatory Branch Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <div className="rounded-xl border border-blue-900/40 bg-blue-950/20 p-4 space-y-2">
              <div className="flex items-center gap-2 text-blue-400 font-semibold text-sm">
                <Database className="h-4 w-4" />
                Branch 1: Financial Analysis (analyze)
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Ingests CSV/Excel ledgers. When format errors are detected, loops into the <span className="text-amber-400 font-medium">Self-Healing Correction Loop</span> for LLM schema repair. Persists clean records to SQL, runs Monte Carlo burn simulations, and enriches with market intelligence.
              </p>
            </div>

            <div className="rounded-xl border border-purple-900/40 bg-purple-950/20 p-4 space-y-2">
              <div className="flex items-center gap-2 text-purple-400 font-semibold text-sm">
                <FileText className="h-4 w-4" />
                Branch 2: Executive Reporting (report)
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Bypasses heavy ledger parsing. The Market Agent collects sector multiples and macroeconomic indicators, passing structured telemetry directly into the Insight Writer for institutional VC memo and board deck generation.
              </p>
            </div>

            <div className="rounded-xl border border-teal-900/40 bg-teal-950/20 p-4 space-y-2">
              <div className="flex items-center gap-2 text-teal-400 font-semibold text-sm">
                <HelpCircle className="h-4 w-4" />
                Branch 3: Board Interrogation (board_prep)
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Adversarial simulation engine that crafts high-stakes audit and investor committee inquiries, preparing founders and CFOs with empirical counterarguments and sensitivity projections.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Node Inspector View */}
      {activeView === "nodes" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Node List Sidebar */}
          <div className="lg:col-span-5 space-y-2.5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 px-1">
              State Machine Nodes ({GRAPH_NODES.length})
            </h3>
            <div className="space-y-1.5 max-h-[640px] overflow-y-auto pr-1">
              {GRAPH_NODES.map((node) => {
                const isSelected = selectedNode.id === node.id;
                return (
                  <button
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    className={`w-full text-left p-3 rounded-xl border transition-all flex items-start justify-between gap-3 ${
                      isSelected
                        ? "bg-zinc-900 border-rose-500/80 shadow-md shadow-rose-950/30"
                        : "bg-zinc-950/70 border-zinc-800 hover:bg-zinc-900 hover:border-zinc-700"
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-zinc-100">{node.name}</span>
                        {node.type === "loop" && (
                          <span className="rounded bg-amber-950/90 text-amber-300 text-[10px] px-1.5 py-0.5 border border-amber-800">
                            Cyclic Loop
                          </span>
                        )}
                        {node.type === "terminal" && (
                          <span className="rounded bg-red-950/90 text-red-300 text-[10px] px-1.5 py-0.5 border border-red-800">
                            Failure
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-zinc-400 font-mono truncate max-w-[280px]">
                        {node.agent}
                      </div>
                    </div>
                    <ArrowRight
                      className={`h-4 w-4 shrink-0 transition-transform ${
                        isSelected ? "text-rose-400 translate-x-0.5" : "text-zinc-600"
                      }`}
                    />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Node Detail Card */}
          <div className="lg:col-span-7">
            <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-6 space-y-6 shadow-xl sticky top-6">
              <div className="flex items-center justify-between border-b border-zinc-800/80 pb-4">
                <div>
                  <span className="text-xs font-mono uppercase text-rose-400 tracking-wider font-semibold">
                    Node ID: {selectedNode.id}
                  </span>
                  <h2 className="text-xl font-bold text-white mt-0.5">{selectedNode.name}</h2>
                </div>
                <span className="rounded-full bg-zinc-900 px-3 py-1 text-xs font-medium text-zinc-300 border border-zinc-800">
                  {selectedNode.type.toUpperCase()}
                </span>
              </div>

              {/* Description */}
              <div className="space-y-1.5">
                <h4 className="text-xs font-semibold uppercase text-zinc-400 tracking-wider">
                  Functional Purpose
                </h4>
                <p className="text-sm text-zinc-300 leading-relaxed bg-zinc-900/60 p-3.5 rounded-xl border border-zinc-800/60">
                  {selectedNode.description}
                </p>
              </div>

              {/* Python Implementation */}
              <div className="space-y-1.5">
                <h4 className="text-xs font-semibold uppercase text-zinc-400 tracking-wider">
                  Python Method & Agent
                </h4>
                <div className="p-3 rounded-xl bg-black/60 border border-zinc-800 font-mono text-xs text-emerald-400 space-y-1">
                  <div><span className="text-zinc-500">Handler:</span> {selectedNode.pythonHandler}</div>
                  <div><span className="text-zinc-500">Agent:</span> <span className="text-cyan-400">{selectedNode.agent}</span></div>
                </div>
              </div>

              {/* State Transitions */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold uppercase text-zinc-400 tracking-wider">
                    Input State Requirements
                  </h4>
                  <div className="space-y-1">
                    {selectedNode.inputs.map((inp) => (
                      <div
                        key={inp}
                        className="text-xs font-mono bg-zinc-900 border border-zinc-800/80 rounded-md px-2.5 py-1 text-zinc-300"
                      >
                        {inp}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="text-xs font-semibold uppercase text-zinc-400 tracking-wider">
                    Output State Mutations
                  </h4>
                  <div className="space-y-1">
                    {selectedNode.outputs.map((out) => (
                      <div
                        key={out}
                        className="text-xs font-mono bg-rose-950/20 border border-rose-900/40 rounded-md px-2.5 py-1 text-rose-300"
                      >
                        +{out}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mermaid Code View */}
      {activeView === "code" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5">
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <Code2 className="h-4 w-4 text-rose-400" />
              <span className="font-semibold text-zinc-200">Mermaid Definition</span>
              <span>— Portable GFM diagram format</span>
            </div>

            <button
              onClick={handleCopyCode}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs font-semibold text-zinc-200 hover:text-white hover:bg-zinc-800 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  <span>Copy Mermaid</span>
                </>
              )}
            </button>
          </div>

          <div className="rounded-2xl border border-zinc-800 bg-black/80 p-5 font-mono text-xs text-zinc-300 overflow-x-auto shadow-xl leading-relaxed">
            <pre>{MERMAID_CODE}</pre>
          </div>
        </div>
      )}

      {/* Fullscreen Modal */}
      {fullscreenModal && (
        <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex flex-col p-4 md:p-8">
          <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
            <div className="flex items-center gap-2">
              <Workflow className="h-5 w-5 text-rose-500" />
              <h2 className="text-lg font-bold text-white">LangGraph Multi-Agent Architecture</h2>
            </div>
            <button
              onClick={() => setFullscreenModal(false)}
              className="px-3.5 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-xs font-semibold text-zinc-200"
            >
              Close
            </button>
          </div>
          <div className="flex-1 flex items-center justify-center p-4 overflow-auto">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/images/langgraph-cfo-flowchart.png"
              alt="LangGraph Multi-Agent Architecture Flowchart (Fullscreen)"
              className="max-h-[85vh] max-w-full w-auto object-contain rounded-xl border border-zinc-800 shadow-2xl"
            />
          </div>
        </div>
      )}
    </div>
  );
}
