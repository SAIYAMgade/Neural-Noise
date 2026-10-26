"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  Sparkles,
  FileText,
  Users,
  CreditCard,
  Receipt,
  TrendingUp,
  LayoutDashboard,
  Layers
} from "lucide-react";
import { OverviewTab as FinOverviewTab } from "@/components/finpilot/overview-tab";
import { AssistantTab } from "@/components/finpilot/assistant-tab";
import { InvoicesTab } from "@/components/finpilot/invoices-tab";
import { ClientsTab } from "@/components/finpilot/clients-tab";
import { PaymentsTab } from "@/components/finpilot/payments-tab";
import { ExpensesTab } from "@/components/finpilot/expenses-tab";
import { AnalyticsTab } from "@/components/finpilot/analytics-tab";

type FinanceSubTab =
  | "overview"
  | "assistant"
  | "invoices"
  | "clients"
  | "payments"
  | "expenses"
  | "analytics";

export function FinanceTab() {
  const [subTab, setSubTab] = useState<FinanceSubTab>("overview");

  const subNav = [
    { id: "overview", label: "Financial Overview", icon: LayoutDashboard },
    { id: "assistant", label: "CFO Assistant", icon: Sparkles, badge: "AI" },
    { id: "invoices", label: "Invoices (GST)", icon: FileText },
    { id: "clients", label: "Clients", icon: Users },
    { id: "payments", label: "Payments", icon: CreditCard },
    { id: "expenses", label: "Expenses", icon: Receipt },
    { id: "analytics", label: "Runway & Analytics", icon: TrendingUp },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Banner explaining the shared platform integration */}
      <div className="rounded-xl border border-amber-200 bg-amber-50/40 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-amber-900 shadow-sm">
        <div className="flex items-center gap-2.5">
          <div className="rounded-lg bg-amber-100 p-2 text-amber-700">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold">
              AI Finance Operations Studio (Secondary Demonstrator)
            </h4>
            <p className="text-xs text-amber-800/80">
              Shares the core IntentFlow platform: LangGraph agent workflows, human-in-the-loop draft confirmations, deterministic Indian GST rules (CGST/SGST/IGST), and immutable ledger auditing.
            </p>
          </div>
        </div>
      </div>

      {/* Sub Navigation Bar */}
      <div className="border-b border-slate-200 bg-white rounded-t-xl px-4 pt-2 shadow-sm">
        <div className="flex flex-wrap gap-2">
          {subNav.map((item) => {
            const Icon = item.icon;
            const isActive = subTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setSubTab(item.id as FinanceSubTab)}
                className={`inline-flex items-center gap-2 border-b-2 py-3 px-3 text-xs font-semibold transition-all ${
                  isActive
                    ? "border-indigo-600 text-indigo-600 bg-indigo-50/30 rounded-t-lg"
                    : "border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300"
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
                <span>{item.label}</span>
                {item.badge && (
                  <span className="rounded-full bg-indigo-100 px-1.5 py-0.2 text-[9px] font-bold text-indigo-700">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Sub Tab Content */}
      <div className="pt-2">
        {subTab === "overview" && (
          <FinOverviewTab onNavigateTab={(tab) => setSubTab(tab as FinanceSubTab)} />
        )}
        {subTab === "assistant" && <AssistantTab />}
        {subTab === "invoices" && <InvoicesTab />}
        {subTab === "clients" && <ClientsTab />}
        {subTab === "payments" && <PaymentsTab />}
        {subTab === "expenses" && <ExpensesTab />}
        {subTab === "analytics" && <AnalyticsTab />}
      </div>
    </div>
  );
}
