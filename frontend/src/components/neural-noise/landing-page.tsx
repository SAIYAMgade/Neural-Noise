"use client";

import React, { useState } from "react";
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  FileText,
  CreditCard,
  Cpu,
  Layers,
  ChevronRight,
  Receipt,
  Users,
  CheckCircle2,
  ExternalLink,
  BookOpen,
  Eye
} from "lucide-react";
import { NeuralNoise } from "@/components/ui/neural-noise";
import { activateDossier } from "@/lib/api";

interface LandingPageProps {
  onEnterPlatform: () => void;
}

const DOSSIERS = [
  {
    id: "apex_global",
    name: "Apex Global Technologies Pvt Ltd",
    badge: "PDF 1 · 24 Pages Verified",
    industry: "Enterprise Cloud & AI Systems",
    state: "Karnataka (State Code 29 · Bengaluru)",
    gstin: "29AAACA1234A1Z5",
    invoiced: "₹29,26,400",
    collected: "₹21,83,000",
    surplus: "₹10,10,000",
    pdfUrl: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf",
  },
  {
    id: "kavach_security",
    name: "Kavach Security Solutions Pvt Ltd",
    badge: "PDF 2 · 25 Pages Verified",
    industry: "Enterprise Cybersecurity & SOC 2",
    state: "Maharashtra (State Code 27 · Mumbai)",
    gstin: "27AABCK5678B1Z2",
    invoiced: "₹38,50,000",
    collected: "₹29,00,000",
    surplus: "₹14,80,000",
    pdfUrl: "/dossiers/Kavach_Security_Solutions_Annual_Audit_2026.pdf",
  },
  {
    id: "zenith_digital",
    name: "Zenith Digital Media & Design LLP",
    badge: "PDF 3 · 22 Pages Verified",
    industry: "Performance Marketing & Growth",
    state: "New Delhi (State Code 07)",
    gstin: "07AAGFZ9012C1Z8",
    invoiced: "₹19,11,600",
    collected: "₹15,10,400",
    surplus: "₹6,70,000",
    pdfUrl: "/dossiers/Zenith_Digital_Media_Q3_Financial_Review.pdf",
  },
];

export function LandingPage({ onEnterPlatform }: LandingPageProps) {
  const [activatingId, setActivatingId] = useState<string | null>(null);

  const handleSelectDossier = async (dossierId: string) => {
    setActivatingId(dossierId);
    try {
      await activateDossier(dossierId);
    } catch (err) {
      console.warn("Dossier switch note:", err);
    } finally {
      setActivatingId(null);
      onEnterPlatform();
    }
  };

  const features = [
    {
      icon: Sparkles,
      title: "LangGraph Autonomous CFO Agent",
      description:
        "Multi-step conversational intelligence with stateful checkpoints, typed tool-calling, automated draft creation, and human-in-the-loop approval gates.",
      tag: "Agentic AI",
    },
    {
      icon: FileText,
      title: "Deterministic GST & Invoicing Engine",
      description:
        "Automatic intra-state (CGST 9% + SGST 9%) vs inter-state (IGST 18%) tax splitting with sequential numbering and on-the-fly PDF generation.",
      tag: "Indian FinTech",
    },
    {
      icon: BookOpen,
      title: "20–25+ Page Statutory Audit Vector RAG",
      description:
        "TF-IDF vector indexing across verified balance sheets, P&L statements, and receivables schedules with zero-hallucination citations.",
      tag: "Document Intelligence",
    },
    {
      icon: ShieldCheck,
      title: "GSTR-1 & 3B Tax Compliance Hub",
      description:
        "Automated outward supplies ledger, SAC 998311/998313 service classification, and 1-click JSON schema export for official GST portal filing.",
      tag: "Statutory Filing",
    },
    {
      icon: CreditCard,
      title: "Receivables Aging & Liquidity Tracking",
      description:
        "Real-time 0–30 day current and 31–60 day overdue debtor tracking, cash burn projections, and automated collection reminders.",
      tag: "Cash Flow",
    },
    {
      icon: Cpu,
      title: "Cryptographic Audit & Traces",
      description:
        "Immutable double-entry transaction ledgers with actor signatures (user:web vs agent:copilot_approved) and sub-second trace latency.",
      tag: "Observability",
    },
  ];

  return (
    <div className="relative min-h-screen bg-[#07070a] text-slate-100 overflow-x-hidden font-sans selection:bg-rose-500 selection:text-white">
      {/* Interactive WebGL Neural Noise Shader Background */}
      <NeuralNoise
        color={[0.96, 0.18, 0.42]}
        opacity={0.88}
        speed={0.0012}
        className="fixed inset-0 pointer-events-none z-0"
      />

      {/* Subtle radial vignette overlay for contrast */}
      <div className="fixed inset-0 bg-radial from-transparent via-[#07070a]/60 to-[#07070a]/95 pointer-events-none z-0" />

      {/* Relative Content Container */}
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Navigation Bar */}
        <header className="border-b border-rose-500/15 bg-[#07070a]/75 backdrop-blur-xl sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            {/* Brand Logo */}
            <div className="flex items-center gap-3">
              <div className="h-11 w-11 rounded-2xl bg-gradient-to-tr from-rose-600 to-pink-500 flex items-center justify-center text-white shadow-lg shadow-rose-600/30 border border-rose-400/30">
                <Sparkles className="h-6 w-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xl font-black tracking-tight text-white drop-shadow-[0_0_12px_rgba(244,63,94,0.4)]">
                    Neural <span className="text-rose-500">Noise</span>
                  </span>
                  <span className="rounded-full bg-rose-950/80 border border-rose-500/30 px-2 py-0.5 text-[10px] font-bold text-rose-400">
                    AI Platform v2.0
                  </span>
                </div>
                <p className="text-[11px] text-zinc-400 font-medium hidden sm:block">
                  Autonomous Financial Operations &amp; Intelligence
                </p>
              </div>
            </div>

            {/* Nav Links */}
            <nav className="hidden md:flex items-center gap-8 text-xs font-semibold text-zinc-300">
              <a href="#dossiers" className="hover:text-rose-400 transition-colors">
                Statutory Dossiers
              </a>
              <a href="#features" className="hover:text-rose-400 transition-colors">
                Platform Architecture
              </a>
            </nav>

            {/* Launch App Button */}
            <div className="flex items-center gap-3">
              <button
                onClick={onEnterPlatform}
                className="group relative inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-rose-600 to-pink-600 px-5 py-2.5 text-xs font-bold text-white shadow-lg shadow-rose-600/30 hover:from-rose-500 hover:to-pink-500 transition-all border border-rose-400/40"
              >
                <span>Launch Platform</span>
                <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
              </button>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="flex-1 flex flex-col items-center justify-center text-center px-4 pt-16 pb-20 max-w-5xl mx-auto">
          {/* Top Pill */}
          <div className="inline-flex items-center gap-2 rounded-full bg-rose-950/70 border border-rose-500/30 px-4 py-1.5 text-xs font-semibold text-rose-300 shadow-lg shadow-rose-950/50 mb-8 backdrop-blur-md">
            <span className="flex h-2 w-2 rounded-full bg-rose-500 animate-pulse" />
            <span>Autonomous Financial Operations for Indian Independents &amp; Enterprises</span>
          </div>

          {/* Central Glowing Title */}
          <h1 className="text-7xl sm:text-8xl md:text-9xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white via-rose-100 to-rose-500 drop-shadow-[0_0_50px_rgba(244,63,94,0.45)] leading-none mb-8 select-none">
            Neural Noise
          </h1>

          {/* Subtitle */}
          <p className="max-w-2xl text-base sm:text-lg text-zinc-300 font-normal leading-relaxed mb-10">
            A production-grade AI financial operations platform. Deterministic Indian GST invoicing,
            human-in-the-loop LangGraph agents, multi-page statutory audit vector intelligence, and
            one-click GSTR-1 tax compliance.
          </p>

          {/* Call to Actions */}
          <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
            <button
              onClick={onEnterPlatform}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-rose-600 via-rose-500 to-pink-600 px-8 py-4 text-sm font-bold text-white shadow-xl shadow-rose-600/35 hover:shadow-rose-600/50 hover:brightness-110 transition-all border border-rose-300/40"
            >
              <Sparkles className="h-4 w-4" />
              <span>Enter Financial Workspace</span>
              <ArrowRight className="h-4 w-4" />
            </button>

            <a
              href="#dossiers"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-zinc-900/80 hover:bg-zinc-800/80 border border-zinc-700/80 px-6 py-4 text-sm font-semibold text-zinc-200 backdrop-blur-md transition-all shadow-md"
            >
              <BookOpen className="h-4 w-4 text-rose-400" />
              <span>Explore Statutory Dossiers</span>
            </a>
          </div>
        </section>

        {/* Multi-Page Statutory Dossier Selector Strip */}
        <section id="dossiers" className="border-y border-rose-500/20 bg-zinc-950/85 backdrop-blur-xl py-14">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
              <div>
                <div className="inline-flex items-center gap-2 rounded-full bg-rose-950/80 border border-rose-500/30 px-3 py-1 text-xs font-bold text-rose-300 mb-2">
                  <FileText className="h-3.5 w-3.5" />
                  <span>Verified Corporate Financial Dossiers</span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                  Select a Verified Statutory Audit Dossier
                </h2>
                <p className="mt-1 text-xs sm:text-sm text-zinc-400">
                  Select any of the 3 multi-page statutory audits (22–25 pages each with complete double-entry books and verified GST records).
                </p>
              </div>
            </div>

            {/* 3 Dossiers Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {DOSSIERS.map((d) => (
                <div
                  key={d.id}
                  className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6 flex flex-col justify-between hover:border-rose-500/50 hover:bg-zinc-900/90 transition-all shadow-xl shadow-black/40 group relative overflow-hidden"
                >
                  <div className="absolute top-0 right-0 w-28 h-28 bg-rose-600/5 rounded-full blur-2xl group-hover:bg-rose-600/15 pointer-events-none" />

                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="rounded-full bg-rose-950/90 border border-rose-500/40 px-2.5 py-0.5 text-[11px] font-bold text-rose-300">
                        {d.badge}
                      </span>
                      <a
                        href={d.pdfUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-[11px] text-zinc-400 hover:text-rose-400 font-semibold transition"
                      >
                        <Eye className="h-3.5 w-3.5" />
                        <span>View PDF</span>
                      </a>
                    </div>

                    <h3 className="text-base font-bold text-white group-hover:text-rose-300 transition-colors">
                      {d.name}
                    </h3>
                    <p className="text-xs text-zinc-400 mt-1">
                      {d.industry}
                    </p>
                    <p className="text-[11px] text-zinc-500 font-mono mt-0.5">
                      {d.state} · {d.gstin}
                    </p>

                    <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-zinc-800/80 text-center">
                      <div className="rounded-lg bg-zinc-950/60 p-2 border border-zinc-800/60">
                        <span className="text-[10px] text-zinc-500 block uppercase font-bold">Invoiced</span>
                        <span className="text-xs font-bold text-white">{d.invoiced}</span>
                      </div>
                      <div className="rounded-lg bg-zinc-950/60 p-2 border border-zinc-800/60">
                        <span className="text-[10px] text-zinc-500 block uppercase font-bold">Collected</span>
                        <span className="text-xs font-bold text-emerald-400">{d.collected}</span>
                      </div>
                      <div className="rounded-lg bg-zinc-950/60 p-2 border border-zinc-800/60">
                        <span className="text-[10px] text-zinc-500 block uppercase font-bold">Surplus</span>
                        <span className="text-xs font-bold text-rose-300">{d.surplus}</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 pt-3">
                    <button
                      onClick={() => handleSelectDossier(d.id)}
                      disabled={activatingId === d.id}
                      className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-zinc-800 hover:bg-rose-600/90 border border-zinc-700/80 hover:border-rose-400/50 py-2.5 text-xs font-bold text-zinc-200 hover:text-white transition-all shadow-md group-hover:bg-rose-600"
                    >
                      <Sparkles className="h-3.5 w-3.5 text-rose-400 group-hover:text-white" />
                      <span>{activatingId === d.id ? "Loading Ledger..." : "Activate & Inspect Dossier"}</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Feature Grid */}
        <section id="features" className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-widest text-rose-400 mb-3">
              Full-Stack Platform Architecture
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Engineered for Audit-Grade Precision &amp; Autonomous Operation
            </h3>
            <p className="mt-4 text-sm text-zinc-400">
              Every workflow executes against verified PostgreSQL transactions, LangGraph state graphs, and deterministic tax rules.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => {
              const Icon = f.icon;
              return (
                <div
                  key={i}
                  className="rounded-2xl border border-zinc-800/90 bg-zinc-900/50 p-7 shadow-xl hover:border-rose-500/40 hover:bg-zinc-900/80 transition-all relative group flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-5">
                      <div className="h-12 w-12 rounded-xl bg-rose-950/80 border border-rose-500/30 flex items-center justify-center text-rose-400 shadow-md shadow-rose-950/40 group-hover:scale-105 transition-transform">
                        <Icon className="h-6 w-6" />
                      </div>
                      <span className="rounded-full bg-zinc-800 border border-zinc-700 px-2.5 py-0.5 text-[10px] font-bold text-zinc-300">
                        {f.tag}
                      </span>
                    </div>

                    <h4 className="text-base font-bold text-white mb-2 group-hover:text-rose-300 transition-colors">
                      {f.title}
                    </h4>
                    <p className="text-xs text-zinc-400 leading-relaxed">
                      {f.description}
                    </p>
                  </div>

                  <div className="mt-6 pt-4 border-t border-zinc-800/80 flex items-center gap-1.5 text-xs font-semibold text-rose-400 group-hover:text-rose-300">
                    <span>Inspect workflow</span>
                    <ChevronRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* CTA Footer Banner */}
        <section className="border-t border-rose-500/20 bg-gradient-to-b from-zinc-950 to-black py-20">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-rose-600 to-pink-500 text-white shadow-xl shadow-rose-600/40 mb-6">
              <Sparkles className="h-7 w-7" />
            </div>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
              Step Into the Neural Noise Platform
            </h3>
            <p className="text-sm text-zinc-400 max-w-xl mx-auto mb-8">
              Explore live Indian GST invoices, run conversational LangGraph RAG over statutory dossiers, and inspect cryptographic ledgers.
            </p>
            <button
              onClick={onEnterPlatform}
              className="inline-flex items-center gap-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-pink-600 px-8 py-4 text-sm font-bold text-white shadow-2xl shadow-rose-600/50 hover:brightness-110 transition-all border border-rose-400/40"
            >
              <span>Launch Live Workspace</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </section>

        {/* Minimal Footer */}
        <footer className="border-t border-zinc-900 py-6 text-center text-xs text-zinc-500 bg-black">
          <p>© 2026 Neural Noise AI Platform. Designed for Autonomous Financial Operations.</p>
        </footer>
      </div>
    </div>
  );
}
