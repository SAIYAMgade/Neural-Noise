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
  Search,
  Cpu,
  ShieldCheck,
  BrainCircuit,
  Binary
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

const LANGGRAPH_NODES: NodeSpec[] = [
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

const RAG_STEPS: NodeSpec[] = [
  {
    id: "pdf_ingestion",
    name: "Statutory PDF Dossier Ingestion",
    pythonHandler: "dossier_rag_service.DossierRAGService.get_or_build_index",
    agent: "pypdf Ingestion Service",
    inputs: ["Apex_Global (24p)", "Kavach_Security (25p)", "Zenith_Digital (22p)"],
    outputs: ["raw_page_streams"],
    description: "Loads verified statutory balance sheets, CARO 2020 matrices, and 12-month GSTR accounting logs from disk with zero network latency.",
    type: "database"
  },
  {
    id: "chunker",
    name: "Hierarchical Chunk & Metadata Parser",
    pythonHandler: "dossier_rag_service._extract_page_chunks",
    agent: "DossierChunker",
    inputs: ["raw_page_streams"],
    outputs: ["chunks (page_idx, section_title, text)"],
    description: "Splits 20+ page dossiers into structured page-level chunks with header detection, preserving accounting table alignments and note schedules.",
    type: "agent"
  },
  {
    id: "vectorizer",
    name: "TF-IDF Vectorizer (n-gram 1-3, sublinear_tf)",
    pythonHandler: "sklearn.feature_extraction.text.TfidfVectorizer",
    agent: "In-Memory Vector Matrix",
    inputs: ["chunks text"],
    outputs: ["sparse_tfidf_matrix", "vectorizer_vocabulary"],
    description: "Builds a high-dimensional vocabulary index using sublinear term frequencies and bi/tri-grams, eliminating cold-start embedding latency.",
    type: "agent"
  },
  {
    id: "ranker",
    name: "Cosine Similarity Vector Ranker",
    pythonHandler: "dossier_rag_service.search_chunks",
    agent: "Vector Search Engine",
    inputs: ["user_natural_query", "tfidf_matrix"],
    outputs: ["top_k_grounded_chunks (score >= threshold)"],
    description: "Computes cosine distance between query tokens and indexed dossier schedules to extract the 3 most relevant accounting notes.",
    type: "agent"
  },
  {
    id: "gemini_synthesis",
    name: "Google Gemini Synthesis (Primary)",
    pythonHandler: "dossier_rag_service._get_gemini_model",
    agent: "Gemini 2.0 / 1.5 Flash",
    inputs: ["top_k_chunks", "system_financial_prompt", "query"],
    outputs: ["grounded_natural_response"],
    description: "Synthesizes concise, auditable answers strictly bounded by retrieved dossier facts, formatting monetary amounts in INR (₹).",
    type: "router"
  },
  {
    id: "smart_fallback",
    name: "Deterministic Fallback Engine (Offline)",
    pythonHandler: "dossier_rag_service._generate_smart_fallback",
    agent: "SQL Ledger & SAC Tax Calculator",
    inputs: ["SQL database state", "top_k_chunks", "query"],
    outputs: ["zero_hallucination_response"],
    description: "Dual-mode guarantee: if Gemini API is unreachable or unconfigured, queries are answered deterministically from live SQL double-entry ledgers.",
    type: "terminal"
  }
];

const LANGGRAPH_MERMAID = `flowchart TD
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

const RAG_MERMAID = `flowchart LR
    PDF[20+ Page Statutory PDF] --> Parser[pypdf Page & Section Parser]
    Parser --> Chunks[Hierarchical Chunks + Metadata]
    Chunks --> TFIDF[TfidfVectorizer: n-gram 1-3, sublinear_tf]
    
    UserQuery[User Natural Query] --> Matcher[Cosine Similarity Vector Ranker]
    TFIDF --> Matcher
    Matcher --> TopK[Top-K Grounded Contexts]
    
    TopK --> LLM[Google Gemini: Flash 2.0 / 1.5]
    SQL[Live SQL Database State] --> Fallback[Zero-Hallucination Fallback Engine]
    LLM -.->|If API key active| Response[Grounded Natural Response]
    Fallback -.->|If offline / fallback| Response`;

export function FlowchartTab() {
  const [selectedSubsystem, setSelectedSubsystem] = useState<"langgraph" | "rag">("langgraph");
  const [activeView, setActiveView] = useState<"diagram" | "nodes" | "code">("diagram");
  const [selectedNode, setSelectedNode] = useState<NodeSpec>(LANGGRAPH_NODES[0]);
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [copied, setCopied] = useState<boolean>(false);
  const [fullscreenModal, setFullscreenModal] = useState<boolean>(false);

  const isLangGraph = selectedSubsystem === "langgraph";
  const currentNodes = isLangGraph ? LANGGRAPH_NODES : RAG_STEPS;
  const currentMermaid = isLangGraph ? LANGGRAPH_MERMAID : RAG_MERMAID;
  const currentImage = isLangGraph
    ? "/images/langgraph-cfo-flowchart.png"
    : "/images/rag-architecture-flowchart.png";

  const handleSwitchSubsystem = (sub: "langgraph" | "rag") => {
    setSelectedSubsystem(sub);
    setSelectedNode(sub === "langgraph" ? LANGGRAPH_NODES[0] : RAG_STEPS[0]);
    setZoomLevel(1);
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(currentMermaid);
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
              <span className="inline-flex items-center gap-1.5 rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-400 border border-cyan-500/20">
                <BrainCircuit className="h-3.5 w-3.5" />
                Dossier RAG Vector Pipeline
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Zero-Hallucination Fallback
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              System Architecture Flowcharts
            </h1>
            <p className="text-sm text-zinc-400 max-w-3xl leading-relaxed">
              Explore the two core AI engines powering Neural-Noise: the compiled{" "}
              <strong className="text-rose-400">LangGraph Multi-Agent CFO State Machine</strong> and the{" "}
              <strong className="text-cyan-400">Statutory Dossier RAG Pipeline</strong> with deterministic zero-hallucination guarantees.
            </p>
          </div>

          {/* Subsystem Switcher Pills */}
          <div className="flex flex-col sm:flex-row items-center gap-2">
            <div className="flex items-center bg-zinc-900 border border-zinc-800 rounded-xl p-1 gap-1">
              <button
                onClick={() => handleSwitchSubsystem("langgraph")}
                className={`inline-flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-lg transition-all ${
                  isLangGraph
                    ? "bg-rose-500 text-white shadow-md shadow-rose-950/50"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                <GitFork className="h-3.5 w-3.5" />
                1. LangGraph CFO Graph
              </button>
              <button
                onClick={() => handleSwitchSubsystem("rag")}
                className={`inline-flex items-center gap-2 px-3.5 py-2 text-xs font-bold rounded-lg transition-all ${
                  !isLangGraph
                    ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/50"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                <Search className="h-3.5 w-3.5" />
                2. RAG Retrieval Pipeline
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* View Mode Switcher Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5">
        <div className="flex items-center gap-2 text-xs text-zinc-400">
          <span className="font-semibold text-zinc-200">
            {isLangGraph ? "LangGraph CFO Workflow:" : "RAG Vector Architecture:"}
          </span>
          <span>{currentNodes.length} Architectural Components</span>
          <span className="text-zinc-700">•</span>
          <span className={isLangGraph ? "text-rose-400 font-medium" : "text-cyan-400 font-medium"}>
            {isLangGraph ? "Cyclical Self-Healing Loop" : "Dual-Engine Synthesis"}
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* View Toggles */}
          <div className="flex items-center bg-zinc-900 border border-zinc-800 rounded-lg p-0.5 gap-1">
            <button
              onClick={() => setActiveView("diagram")}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                activeView === "diagram"
                  ? "bg-zinc-800 text-white"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Diagram View
            </button>
            <button
              onClick={() => setActiveView("nodes")}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                activeView === "nodes"
                  ? "bg-zinc-800 text-white"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Component Inspector
            </button>
            <button
              onClick={() => setActiveView("code")}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                activeView === "code"
                  ? "bg-zinc-800 text-white"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Mermaid Code
            </button>
          </div>

          {/* Zoom Controls for Diagram View */}
          {activeView === "diagram" && (
            <div className="flex items-center gap-1.5 pl-2 border-l border-zinc-800">
              <button
                onClick={() => setZoomLevel((z) => Math.max(0.7, z - 0.15))}
                className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors"
                title="Zoom Out"
              >
                <ZoomOut className="h-3.5 w-3.5" />
              </button>
              <span className="text-xs font-mono text-zinc-400 min-w-[42px] text-center">
                {Math.round(zoomLevel * 100)}%
              </span>
              <button
                onClick={() => setZoomLevel((z) => Math.min(1.8, z + 0.15))}
                className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors"
                title="Zoom In"
              >
                <ZoomIn className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setZoomLevel(1)}
                className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors"
                title="Reset Zoom"
              >
                <RotateCcw className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setFullscreenModal(true)}
                className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-colors"
                title="Fullscreen"
              >
                <Maximize2 className="h-3.5 w-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      {activeView === "diagram" && (
        <div className="space-y-4">
          {/* Diagram Canvas */}
          <div className="relative rounded-2xl border border-zinc-800 bg-[#0d0e12] p-6 flex flex-col items-center justify-center overflow-auto min-h-[560px] shadow-2xl">
            {/* Background Dot Grid */}
            <div
              className="absolute inset-0 opacity-[0.08] pointer-events-none"
              style={{
                backgroundImage: "radial-gradient(#ffffff 1px, transparent 1px)",
                backgroundSize: "24px 24px"
              }}
            />

            <div
              className="transition-transform duration-200 ease-out origin-top flex items-center justify-center w-full"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={currentImage}
                alt={isLangGraph ? "LangGraph Architecture Flowchart" : "RAG Pipeline Flowchart"}
                className={`w-full h-auto rounded-xl shadow-2xl border border-zinc-800/80 bg-zinc-950/90 ${
                  isLangGraph ? "max-w-[850px]" : "max-w-[1100px]"
                }`}
              />
            </div>
          </div>

          {/* Subsystem Descriptive Cards */}
          {isLangGraph ? (
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
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              <div className="rounded-xl border border-cyan-900/40 bg-cyan-950/20 p-4 space-y-2">
                <div className="flex items-center gap-2 text-cyan-400 font-semibold text-sm">
                  <FileText className="h-4 w-4" />
                  1. Statutory PDF Chunking & Vectorization
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Extracts page streams from 20+ page audit dossiers using <code className="text-cyan-300">pypdf</code>. Chunks preserve accounting schedule tables and section headers, building a high-speed in-memory <code className="text-cyan-300">TfidfVectorizer</code> matrix.
                </p>
              </div>

              <div className="rounded-xl border border-indigo-900/40 bg-indigo-950/20 p-4 space-y-2">
                <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
                  <Binary className="h-4 w-4" />
                  2. Cosine Similarity Vector Retrieval
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  User natural questions are vectorized across n-grams (1 to 3) with sublinear term-frequency weights, matching the Top-K most relevant statutory accounting schedules with sub-10ms query latency.
                </p>
              </div>

              <div className="rounded-xl border border-emerald-900/40 bg-emerald-950/20 p-4 space-y-2">
                <div className="flex items-center gap-2 text-emerald-400 font-semibold text-sm">
                  <ShieldCheck className="h-4 w-4" />
                  3. Dual-Engine Zero-Hallucination Delivery
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Grounded answers are generated via Google Gemini 2.0/1.5 Flash. If the LLM is offline or rate-limited, the <strong className="text-emerald-300">Deterministic Fallback Engine</strong> extracts exact figures directly from live SQL double-entry ledgers.
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Component / Node Inspector View */}
      {activeView === "nodes" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Component List */}
          <div className="lg:col-span-5 space-y-2.5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 px-1">
              {isLangGraph ? "LangGraph Nodes" : "RAG Pipeline Steps"} ({currentNodes.length})
            </h3>
            <div className="space-y-1.5 max-h-[640px] overflow-y-auto pr-1">
              {currentNodes.map((node) => {
                const isSelected = selectedNode.id === node.id;
                return (
                  <button
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    className={`w-full text-left p-3 rounded-xl border transition-all flex items-start justify-between gap-3 ${
                      isSelected
                        ? isLangGraph
                          ? "bg-zinc-900 border-rose-500/80 shadow-md shadow-rose-950/30"
                          : "bg-zinc-900 border-cyan-500/80 shadow-md shadow-cyan-950/30"
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
                          <span className="rounded bg-emerald-950/90 text-emerald-300 text-[10px] px-1.5 py-0.5 border border-emerald-800">
                            Deterministic
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-zinc-400 font-mono truncate max-w-[280px]">
                        {node.agent}
                      </div>
                    </div>
                    <ArrowRight
                      className={`h-4 w-4 shrink-0 transition-transform ${
                        isSelected
                          ? isLangGraph
                            ? "text-rose-400 translate-x-0.5"
                            : "text-cyan-400 translate-x-0.5"
                          : "text-zinc-600"
                      }`}
                    />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Component Detail */}
          <div className="lg:col-span-7">
            <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-6 space-y-6 shadow-xl sticky top-6">
              <div className="flex items-center justify-between border-b border-zinc-800/80 pb-4">
                <div>
                  <span
                    className={`text-xs font-mono uppercase tracking-wider font-semibold ${
                      isLangGraph ? "text-rose-400" : "text-cyan-400"
                    }`}
                  >
                    ID: {selectedNode.id}
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

              {/* Implementation */}
              <div className="space-y-1.5">
                <h4 className="text-xs font-semibold uppercase text-zinc-400 tracking-wider">
                  Codebase Handler & Engine
                </h4>
                <div className="p-3 rounded-xl bg-black/60 border border-zinc-800 font-mono text-xs text-emerald-400 space-y-1">
                  <div><span className="text-zinc-500">Handler:</span> {selectedNode.pythonHandler}</div>
                  <div><span className="text-zinc-500">Agent/Module:</span> <span className="text-cyan-400">{selectedNode.agent}</span></div>
                </div>
              </div>

              {/* Inputs & Outputs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold uppercase text-zinc-400 tracking-wider">
                    Input Parameters / State
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
                    Output Mutations / Payloads
                  </h4>
                  <div className="space-y-1">
                    {selectedNode.outputs.map((out) => (
                      <div
                        key={out}
                        className={`text-xs font-mono rounded-md px-2.5 py-1 ${
                          isLangGraph
                            ? "bg-rose-950/20 border border-rose-900/40 text-rose-300"
                            : "bg-cyan-950/20 border border-cyan-900/40 text-cyan-300"
                        }`}
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
              <span className="font-semibold text-zinc-200">
                {isLangGraph ? "LangGraph State Machine Mermaid" : "RAG Pipeline Mermaid"}
              </span>
              <span>— Portable GitHub-flavored markdown</span>
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
            <pre>{currentMermaid}</pre>
          </div>
        </div>
      )}

      {/* Fullscreen Modal */}
      {fullscreenModal && (
        <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex flex-col p-4 md:p-8">
          <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
            <div className="flex items-center gap-2">
              <Workflow className="h-5 w-5 text-rose-500" />
              <h2 className="text-lg font-bold text-white">
                {isLangGraph
                  ? "LangGraph Multi-Agent CFO State Machine"
                  : "Statutory Dossier RAG Pipeline"}
              </h2>
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
              src={currentImage}
              alt={isLangGraph ? "LangGraph Flowchart" : "RAG Pipeline Flowchart"}
              className="max-h-[85vh] max-w-full w-auto object-contain rounded-xl border border-zinc-800 shadow-2xl"
            />
          </div>
        </div>
      )}
    </div>
  );
}
