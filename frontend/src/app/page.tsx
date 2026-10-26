"use client";

import React, { useState, useEffect } from "react";
import {
  Sparkles,
  ShieldCheck,
  CreditCard,
  LayoutDashboard,
  CheckCircle2,
  AlertCircle,
  Menu,
  X,
  ChevronRight,
  FileText,
  Users,
  Receipt,
  Cpu,
  Award,
  ArrowLeft,
  Home,
  GitFork,
  Workflow
} from "lucide-react";
import { checkHealth } from "@/lib/api";
import { LandingPage } from "@/components/neural-noise/landing-page";
import { OverviewTab } from "@/components/finpilot/overview-tab";
import { AssistantTab } from "@/components/finpilot/assistant-tab";
import { InvoicesTab } from "@/components/finpilot/invoices-tab";
import { ClientsTab } from "@/components/finpilot/clients-tab";
import { PaymentsTab } from "@/components/finpilot/payments-tab";
import { ExpensesTab } from "@/components/finpilot/expenses-tab";
import { TaxComplianceTab } from "@/components/finpilot/tax-compliance-tab";
import { AgentLabTab } from "@/components/intentflow/agent-lab-tab";
import { EvaluationsTab } from "@/components/intentflow/evaluations-tab";
import { FlowchartTab } from "@/components/finpilot/flowchart-tab";

type MainTabId =
  | "overview"
  | "assistant"
  | "invoices"
  | "tax-compliance"
  | "clients"
  | "payments"
  | "expenses"
  | "flowchart"
  | "agent-lab"
  | "evaluations";

export default function HomePage() {
  const [viewMode, setViewMode] = useState<"landing" | "platform">("landing");
  const [activeTab, setActiveTab] = useState<MainTabId>("overview");
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    checkHealth()
      .then((ok) => setApiOnline(ok))
      .catch(() => setApiOnline(false));
  }, []);

  const navSections = [
    {
      title: "OPERATIONS & LEDGER",
      items: [
        { id: "overview", label: "Financial Overview", icon: LayoutDashboard },
        { id: "assistant", label: "AI CFO Assistant", icon: Sparkles, badge: "LangGraph", badgeColor: "bg-rose-950 text-rose-300 border border-rose-800" },
        { id: "invoices", label: "Invoices & GST", icon: FileText },
        { id: "tax-compliance", label: "Tax & GST Compliance", icon: ShieldCheck, badge: "New", badgeColor: "bg-emerald-950 text-emerald-300 border border-emerald-800" },
        { id: "clients", label: "Clients & Counterparties", icon: Users },
      ],
    },
    {
      title: "AI AGENTS & OBSERVABILITY",
      items: [
        { id: "flowchart", label: "Architecture Flowcharts", icon: GitFork, badge: "LangGraph + RAG", badgeColor: "bg-blue-950 text-blue-300 border border-blue-800" },
        { id: "agent-lab", label: "Agent Lab & Traces", icon: Cpu, badge: "LangGraph", badgeColor: "bg-purple-950 text-purple-300 border border-purple-800" },
        { id: "evaluations", label: "AI Evals & Guardrails", icon: Award, badge: "Safety", badgeColor: "bg-teal-950 text-teal-300 border border-teal-800" },
      ],
    },
  ];

  const currentTabLabel =
    navSections.flatMap((s) => s.items).find((i) => i.id === activeTab)?.label || "Overview";

  // If in Landing Page mode, render the Neural Noise landing page
  if (viewMode === "landing") {
    return <LandingPage onEnterPlatform={() => setViewMode("platform")} />;
  }

  return (
    <div className="min-h-screen bg-[#09090d] text-zinc-100 flex font-sans w-full max-w-full overflow-x-hidden">
      {/* Mobile Drawer Backdrop */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-xs md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Expanded Roomy Left Sidebar (w-72 md, w-80 lg) themed in Dark + Neural Rose */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 lg:w-80 bg-zinc-950 border-r border-zinc-800 flex flex-col transition-transform duration-200 ease-in-out md:static md:translate-x-0 ${
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Sidebar Brand Header */}
        <div className="flex items-center justify-between p-5 border-b border-zinc-800/80 bg-zinc-950">
          <div className="flex items-center gap-3.5">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-tr from-rose-600 via-rose-700 to-pink-600 text-white shadow-lg shadow-rose-900/40 border border-rose-500/30">
              <Sparkles className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-black tracking-tight text-white">
                  Neural <span className="text-rose-500">Noise</span>
                </span>
                <span className="rounded-full bg-rose-950 border border-rose-500/30 px-2 py-0.5 text-[10px] font-bold text-rose-400">
                  v2.0
                </span>
              </div>
              <p className="text-xs text-zinc-400 font-medium">
                Financial Operations &amp; Intelligence
              </p>
            </div>
          </div>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="md:hidden text-zinc-400 hover:text-zinc-200 p-1.5 rounded-lg"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Back to Landing Page Button */}
        <div className="px-4 pt-4 pb-1">
          <button
            onClick={() => setViewMode("landing")}
            className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 px-3.5 py-2.5 text-xs font-semibold text-zinc-300 hover:text-white transition-all shadow-xs"
          >
            <ArrowLeft className="h-3.5 w-3.5 text-rose-400" />
            <span>Return to Landing Page</span>
          </button>
        </div>

        {/* Navigation Sections */}
        <div className="flex-1 px-4 py-4 space-y-6 overflow-y-auto">
          {navSections.map((section, sIdx) => (
            <div key={sIdx} className="space-y-1.5">
              <div className="px-3 pb-1 text-[11px] font-extrabold uppercase tracking-wider text-zinc-500">
                {section.title}
              </div>
              {section.items.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id as MainTabId);
                      setMobileMenuOpen(false);
                    }}
                    className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-xs font-semibold transition-all ${
                      isActive
                        ? "bg-rose-500/15 text-rose-300 font-bold border border-rose-500/30 shadow-xs"
                        : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon
                        className={`h-4.5 w-4.5 ${
                          isActive ? "text-rose-400" : "text-zinc-500"
                        }`}
                      />
                      <span className="text-[13px]">{tab.label}</span>
                    </div>
                    {tab.badge && (
                      <span
                        className={`rounded-full px-2 py-0.5 text-[9px] font-bold ${tab.badgeColor}`}
                      >
                        {tab.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        {/* Sidebar Footer Info & Live Status */}
        <div className="p-4 border-t border-zinc-800/80 space-y-3 bg-zinc-950">
          <div className="flex items-center justify-between rounded-xl bg-zinc-900/70 border border-zinc-800 px-3.5 py-2.5 text-xs">
            <span className="text-zinc-400 font-medium">Compliance Target:</span>
            <span className="font-bold text-rose-400">Indian GST &amp; Audits</span>
          </div>

          <div className="flex items-center justify-between rounded-xl bg-zinc-900/70 border border-zinc-800 px-3.5 py-2.5 text-xs">
            <span className="text-zinc-400 font-medium">Backend Health:</span>
            <div className="flex items-center gap-1.5">
              {apiOnline === null ? (
                <>
                  <span className="h-2 w-2 rounded-full bg-zinc-500 animate-pulse" />
                  <span className="text-zinc-400 font-medium">Checking</span>
                </>
              ) : apiOnline ? (
                <>
                  <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-emerald-400 font-bold">FastAPI Connected</span>
                </>
              ) : (
                <>
                  <span className="h-2 w-2 rounded-full bg-rose-500" />
                  <span className="text-rose-400 font-bold">Offline</span>
                </>
              )}
            </div>
          </div>
        </div>
      </aside>

      {/* Main Workspace Body */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen bg-[#07070a]">
        {/* Mobile Header Bar */}
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-zinc-800 bg-zinc-950/95 px-4 py-3 backdrop-blur-md md:hidden">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-900"
            >
              <Menu className="h-5 w-5" />
            </button>
            <span className="text-sm font-bold text-white">
              Neural <span className="text-rose-500">Noise</span>
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode("landing")}
              className="rounded-lg bg-zinc-900 px-2.5 py-1 text-[11px] font-semibold text-rose-400 border border-zinc-800"
            >
              Landing Page
            </button>
          </div>
        </header>

        {/* Top Breadcrumb & Status Header */}
        <div className="hidden md:flex items-center justify-between border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md px-8 py-4 shadow-xs">
          <div className="flex items-center gap-3 text-xs">
            <button
              onClick={() => setViewMode("landing")}
              className="inline-flex items-center gap-1.5 font-semibold text-zinc-400 hover:text-rose-400 transition-colors"
            >
              <Home className="h-3.5 w-3.5 text-rose-500" />
              <span>Neural Noise</span>
            </button>
            <ChevronRight className="h-3.5 w-3.5 text-zinc-600" />
            <span className="font-bold text-white text-sm">{currentTabLabel}</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setViewMode("landing")}
              className="inline-flex items-center gap-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 px-3.5 py-1.5 text-xs font-semibold text-zinc-300 hover:text-white transition-all shadow-xs"
            >
              <ArrowLeft className="h-3.5 w-3.5 text-rose-400" />
              <span>Landing Page</span>
            </button>

            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-950/80 border border-emerald-800/80 px-3 py-1 text-xs font-semibold text-emerald-400">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              FastAPI Connected (Port 8000)
            </span>
          </div>
        </div>

        {/* Active Tab Workspace Container */}
        <main className="flex-1 w-full px-4 py-6 sm:px-6 lg:px-8 max-w-7xl mx-auto text-zinc-200">
          {activeTab === "overview" && (
            <OverviewTab
              onNavigateTab={(tab: string) => {
                if (tab === "assistant") setActiveTab("assistant");
                else if (tab === "invoices") setActiveTab("invoices");
                else if (tab === "clients") setActiveTab("clients");
                else if (tab === "payments") setActiveTab("payments");
                else if (tab === "expenses") setActiveTab("expenses");
                else if (tab === "tax-compliance") setActiveTab("tax-compliance");
                else if (tab === "agent-lab") setActiveTab("agent-lab");
                else if (tab === "flowchart") setActiveTab("flowchart");
              }}
            />
          )}
          {activeTab === "assistant" && <AssistantTab />}
          {activeTab === "invoices" && <InvoicesTab />}
          {activeTab === "tax-compliance" && <TaxComplianceTab />}
          {activeTab === "clients" && <ClientsTab />}
          {activeTab === "payments" && <PaymentsTab />}
          {activeTab === "expenses" && <ExpensesTab />}
          {activeTab === "flowchart" && <FlowchartTab />}
          {activeTab === "agent-lab" && <AgentLabTab />}
          {activeTab === "evaluations" && <EvaluationsTab />}
        </main>
      </div>
    </div>
  );
}
