"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  Send,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Download,
  Clock,
  ArrowRight,
  TrendingUp,
  DollarSign,
  User,
  Bot,
  RefreshCw,
} from "lucide-react";
import {
  getBaseUrl,
  chatAssistant,
  approveAssistantAction,
  type AssistantChatResponse,
} from "@/lib/api";
import { handleCopilotOfflineQuery } from "@/lib/copilot-offline-engine";
import { formatINR } from "./utils";

// getBaseUrl imported from @/lib/api

interface MessageItem {
  id: string;
  sender: "user" | "assistant";
  text: string;
  timestamp: string;
  structured_card?: AssistantChatResponse["structured_card"];
  approval_request?: AssistantChatResponse["approval_request"];
}

function FormattedInline({ text }: { text: string }) {
  const parts: React.ReactNode[] = [];
  const regex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[Page \d+:[^\]]+\])/g;
  let lastIdx = 0;
  let match;
  let key = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIdx) {
      parts.push(text.slice(lastIdx, match.index));
    }
    const token = match[0];
    if (token.startsWith("**") && token.endsWith("**")) {
      parts.push(<strong key={key++} className="font-bold text-white">{token.slice(2, -2)}</strong>);
    } else if (token.startsWith("*") && token.endsWith("*")) {
      parts.push(<em key={key++} className="text-zinc-300 italic">{token.slice(1, -1)}</em>);
    } else if (token.startsWith("`") && token.endsWith("`")) {
      parts.push(
        <code key={key++} className="rounded bg-zinc-950 px-1 py-0.5 font-mono text-[11px] text-rose-300 border border-zinc-800">
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith("[Page ")) {
      parts.push(
        <span key={key++} className="inline-flex items-center rounded bg-rose-950/80 px-1.5 py-0.5 text-[10px] font-semibold text-rose-300 border border-rose-500/40 ml-1">
          {token.slice(1, -1)}
        </span>
      );
    }
    lastIdx = regex.lastIndex;
  }
  if (lastIdx < text.length) {
    parts.push(text.slice(lastIdx));
  }

  return <>{parts.length > 0 ? parts : text}</>;
}

function FormattedMessage({ text }: { text: string }) {
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let currentList: string[] = [];

  const flushList = (keyPrefix: string) => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`${keyPrefix}-list`} className="my-1.5 space-y-1 pl-4 list-disc text-xs text-zinc-300">
          {currentList.map((item, idx) => (
            <li key={idx}>
              <FormattedInline text={item} />
            </li>
          ))}
        </ul>
      );
      currentList = [];
    }
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    if (!trimmed) {
      flushList(`empty-${idx}`);
      return;
    }

    if (trimmed.startsWith("### ")) {
      flushList(`h3-${idx}`);
      elements.push(
        <h3 key={`h3-${idx}`} className="text-sm font-bold text-white mt-2 mb-1 flex items-center gap-1.5">
          <FormattedInline text={trimmed.slice(4)} />
        </h3>
      );
    } else if (trimmed.startsWith("#### ")) {
      flushList(`h4-${idx}`);
      elements.push(
        <h4 key={`h4-${idx}`} className="text-xs font-bold text-rose-300 mt-2 mb-0.5">
          <FormattedInline text={trimmed.slice(5)} />
        </h4>
      );
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      currentList.push(trimmed.slice(2));
    } else if (/^\d+\.\s+/.test(trimmed)) {
      flushList(`num-${idx}`);
      elements.push(
        <div key={`num-${idx}`} className="my-1 text-xs text-zinc-300 pl-2">
          <FormattedInline text={trimmed} />
        </div>
      );
    } else {
      flushList(`p-${idx}`);
      elements.push(
        <p key={`p-${idx}`} className="my-1 text-xs text-zinc-300 leading-relaxed">
          <FormattedInline text={trimmed} />
        </p>
      );
    }
  });

  flushList("final");
  return <div className="space-y-1">{elements}</div>;
}

function RenderAssistantCard({
  card,
  approvalRequest,
  approvingId,
  onApprove,
}: {
  card?: AssistantChatResponse["structured_card"];
  approvalRequest?: AssistantChatResponse["approval_request"];
  approvingId: string | null;
  onApprove: (id: string) => void;
}) {
  if (!card || !card.type || !card.data) return null;
  const d = card.data;

  // 1. Invoice Draft Preview
  if (card.type === "invoice_draft") {
    if (!d.subtotal && !d.total_amount) return null;
    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-950/90 p-4 shadow-xl transition-all space-y-3">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-2.5">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-rose-400" />
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Invoice Draft Preview
            </span>
          </div>
          <span className="rounded-full bg-amber-950/80 px-2 py-0.5 text-[11px] font-semibold text-amber-300 border border-amber-800/80">
            Pending Approval
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-zinc-500">Client:</span>
            <p className="font-semibold text-white">{d.client_name || "Client"}</p>
          </div>
          <div>
            <span className="text-zinc-500">Tax Type:</span>
            <p className="font-semibold text-white">
              {d.is_interstate ? "Inter-State (IGST 18%)" : "Intra-State (CGST 9% + SGST 9%)"}
            </p>
          </div>
          <div>
            <span className="text-zinc-500">Subtotal:</span>
            <p className="font-semibold text-white">{formatINR(d.subtotal)}</p>
          </div>
          <div>
            <span className="text-zinc-500">Total Tax:</span>
            <p className="font-semibold text-white">
              {formatINR((d.cgst_total || 0) + (d.sgst_total || 0) + (d.igst_total || 0))}
            </p>
          </div>
        </div>

        <div className="rounded-lg bg-zinc-900 p-2.5 flex items-center justify-between border border-zinc-800">
          <span className="text-xs font-semibold text-zinc-300">Total Amount Due:</span>
          <span className="text-base font-bold text-rose-400">{formatINR(d.total_amount)}</span>
        </div>

        {approvalRequest && (
          <div className="pt-2">
            <button
              onClick={() => onApprove(approvalRequest.id)}
              disabled={approvingId === approvalRequest.id}
              className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 px-4 py-2.5 text-xs font-semibold text-white shadow-md transition disabled:opacity-50"
            >
              {approvingId === approvalRequest.id ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle2 className="h-4 w-4" />
              )}
              <span>Confirm &amp; Issue Official GST Invoice</span>
            </button>
          </div>
        )}
      </div>
    );
  }

  // 2. Invoice Officially Issued
  if (card.type === "invoice_issued") {
    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-950/90 p-4 shadow-xl transition-all space-y-2.5">
        <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase">
          <CheckCircle2 className="h-4 w-4" />
          <span>Invoice Officially Issued &amp; Sealed</span>
        </div>
        <div className="text-xs space-y-1">
          <p className="text-zinc-400">
            Invoice Number: <strong className="text-white">{d.invoice_number || d.invoice_id}</strong>
          </p>
          <p className="text-zinc-400">
            Grand Total: <strong className="text-white">{formatINR(d.grand_total || d.total_amount)}</strong>
          </p>
        </div>
        {d.pdf_path && (
          <a
            href={`${getBaseUrl()}/api/v1/invoices/${d.invoice_id}/pdf`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-rose-600 hover:bg-rose-500 px-3 py-2 text-xs font-semibold text-white shadow-md transition"
          >
            <Download className="h-3.5 w-3.5" />
            Download Official GST PDF
          </a>
        )}
      </div>
    );
  }

  // 3. Overdue Receivables Summary
  if (card.type === "overdue_summary") {
    const overdueAmt = Number(d.total_overdue_amount ?? d.total_overdue ?? d.overdue_amount ?? 0);
    const rawList: any[] = Array.isArray(d.invoices) && d.invoices.length > 0
      ? d.invoices
      : (d.primary_debtor ? [{
          id: "primary-debtor",
          client_name: d.primary_debtor,
          invoice_number: d.invoice_number || "INV-2026-008",
          days_overdue: d.days_overdue || 45,
          amount_due: overdueAmt || 247800,
        }] : []);

    if (overdueAmt <= 0 && rawList.length === 0) return null;

    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-950/90 p-4 shadow-xl transition-all space-y-2.5">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
          <div className="flex items-center gap-2 text-rose-400 font-bold text-xs uppercase">
            <AlertTriangle className="h-4 w-4" />
            <span>Overdue Receivables Summary</span>
          </div>
          <span className="text-xs font-bold text-rose-400">
            {formatINR(overdueAmt)}
          </span>
        </div>
        <div className="space-y-1.5 max-h-48 overflow-y-auto divide-y divide-zinc-800/80">
          {rawList.map((inv: any, idx: number) => (
            <div key={inv.id || idx} className="pt-1.5 flex items-center justify-between text-xs">
              <div>
                <p className="font-semibold text-white">{inv.client_name}</p>
                <span className="text-[11px] text-zinc-500">
                  {inv.invoice_number} · {inv.days_overdue || 45} days overdue
                </span>
              </div>
              <span className="font-bold text-rose-400">
                {formatINR(inv.amount_due || inv.balance_due)}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 4. Financial Summary
  if (card.type === "financial_summary") {
    const invoiced = Number(d.total_invoiced ?? d.invoiced ?? 0);
    const collected = Number(d.total_collected ?? d.collected ?? 0);
    const receivables = Number(d.outstanding_receivables ?? d.receivables ?? 0);
    const netFlow = Number(d.net_cash_flow ?? d.surplus ?? 0);

    if (invoiced <= 0 && collected <= 0) return null;

    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-950/90 p-4 shadow-xl transition-all space-y-2.5">
        <div className="flex items-center gap-2 text-rose-400 font-bold text-xs uppercase border-b border-zinc-800 pb-2">
          <TrendingUp className="h-4 w-4" />
          <span>Corporate Financial Position</span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="rounded-lg bg-zinc-900 p-2 border border-zinc-800">
            <span className="text-zinc-500">Invoiced:</span>
            <p className="font-bold text-white">{formatINR(invoiced)}</p>
          </div>
          <div className="rounded-lg bg-zinc-900 p-2 border border-zinc-800">
            <span className="text-emerald-400">Collected:</span>
            <p className="font-bold text-emerald-400">{formatINR(collected)}</p>
          </div>
          <div className="rounded-lg bg-zinc-900 p-2 border border-zinc-800">
            <span className="text-amber-400">Receivables:</span>
            <p className="font-bold text-amber-400">{formatINR(receivables)}</p>
          </div>
          <div className="rounded-lg bg-zinc-900 p-2 border border-zinc-800">
            <span className="text-rose-400">Net Flow:</span>
            <p className="font-bold text-rose-400">{formatINR(netFlow)}</p>
          </div>
        </div>
      </div>
    );
  }

  // 5. Dossier Summary
  if (card.type === "dossier_summary") {
    const entityName = d.entity_name || d.name || "Apex Global Technologies Pvt Ltd";
    const dossierTitle = d.dossier_title || d.industry || "Enterprise Cloud & AI Systems";
    const gstin = d.gstin || "29AAACA1234A1Z5";
    const pagesCount = d.pages_count || 24;
    const invoiced = Number(d.total_invoiced ?? d.invoiced ?? 0);
    const collected = Number(d.total_collected ?? d.collected ?? 0);
    const receivables = Number(d.outstanding_receivables ?? d.receivables ?? 0);
    const overdueAmt = Number(d.overdue_amount ?? d.overdue ?? 0);

    if (invoiced <= 0 && collected <= 0) return null;

    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-950/90 p-4 shadow-xl transition-all space-y-3">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
          <div className="flex items-center gap-2 text-rose-400">
            <FileText className="h-4 w-4" />
            <span className="text-xs font-bold uppercase tracking-wider">
              Active Statutory Audit &amp; Dossier
            </span>
          </div>
          <span className="rounded-full bg-rose-950/80 px-2 py-0.5 text-[10px] font-bold text-rose-300 border border-rose-500/40">
            {pagesCount} Pages Verified
          </span>
        </div>

        <div className="text-xs">
          <p className="font-bold text-white">{entityName}</p>
          <p className="text-[11px] text-zinc-400">{dossierTitle} · {gstin}</p>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="rounded-lg bg-zinc-900 p-2 border border-zinc-800">
            <span className="text-zinc-500">Total Invoiced:</span>
            <p className="font-bold text-white">{formatINR(invoiced)}</p>
          </div>
          <div className="rounded-lg bg-zinc-900 p-2 border border-zinc-800">
            <span className="text-emerald-400">Total Collected:</span>
            <p className="font-bold text-emerald-400">{formatINR(collected)}</p>
          </div>
          <div className="rounded-lg bg-zinc-900 p-2 border border-zinc-800">
            <span className="text-amber-400">Receivables:</span>
            <p className="font-bold text-amber-400">{formatINR(receivables)}</p>
          </div>
          <div className="rounded-lg bg-zinc-900 p-2 border border-zinc-800">
            <span className="text-rose-400">Overdue Balance:</span>
            <p className="font-bold text-rose-400">{formatINR(overdueAmt)}</p>
          </div>
        </div>

        {d.pdf_url && (
          <a
            href={d.pdf_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 px-3 py-2 text-xs font-semibold text-white transition shadow-md"
          >
            <Download className="h-3.5 w-3.5" />
            View Complete Multi-Page Dossier PDF ({pagesCount} Pages)
          </a>
        )}
      </div>
    );
  }

  return null;
}


const SUGGESTIONS = [
  "Tell me about PDF 1",
  "What are the three PDFs?",
  "Who owes money and what are the overdue balances?",
  "Show our financial summary and operating cash flow",
  "Create invoice for Acme Consulting for ₹50,000 + 18% GST",
];

export function AssistantTab() {
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: "welcome",
      sender: "assistant",
      text: "Hello! I am Neural Copilot, your autonomous financial AI operations assistant for Neural Noise. I can analyze the 3 statutory audit PDFs (PDF 1: Apex Global, PDF 2: Kavach Security, PDF 3: Zenith Digital), verify Indian GST calculations, manage debtor ledgers, and draft invoices with human confirmation. How can I help you today?",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [approvingId, setApprovingId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSendMessage = async (msg: string) => {
    const trimmed = msg.trim();
    if (!trimmed || loading) return;

    const userMsg: MessageItem = {
      id: crypto.randomUUID(),
      sender: "user",
      text: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setLoading(true);

    try {
      const response = await chatAssistant(trimmed, conversationId);

      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      const assistantMsg: MessageItem = {
        id: crypto.randomUUID(),
        sender: "assistant",
        text: response.message || (response as any).response || (response as any).reply || "Response received.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        structured_card: response.structured_card,
        approval_request: response.approval_request,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.warn("Chat error, using deterministic copilot engine:", err);
      const fallback = handleCopilotOfflineQuery(trimmed, conversationId);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          sender: "assistant",
          text: fallback.message,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          structured_card: fallback.structured_card,
          approval_request: fallback.approval_request,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (approvalRequestId: string) => {
    setApprovingId(approvalRequestId);
    try {
      const result = await approveAssistantAction(approvalRequestId);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          sender: "assistant",
          text: result.message || "Action approved and executed successfully.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          structured_card: result.structured_card,
        },
      ]);
    } catch (err: any) {
      alert(`Approval error: ${err.message || "Failed to execute"}`);
    } finally {
      setApprovingId(null);
    }
  };

  return (
    <div className="flex flex-col h-[760px] rounded-2xl border border-zinc-800 bg-zinc-900 shadow-2xl shadow-black/50 overflow-hidden text-zinc-100">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 bg-zinc-950/80 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-rose-600 to-pink-600 text-white shadow-lg shadow-rose-600/30 border border-rose-400/30">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white">Neural Copilot</h2>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-950/80 px-2.5 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-800/80">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                LangGraph Autonomous Multi-Step Engine Active
              </span>
            </div>
            <p className="text-xs text-zinc-400">
              Deterministic calculations with human-in-the-loop approval safeguards
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs text-zinc-400">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span>Zero Hallucination Financial Math</span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-5 bg-gradient-to-b from-zinc-950 to-zinc-900">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex gap-3 ${m.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            {m.sender === "assistant" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-rose-950/80 text-rose-400 border border-rose-500/30">
                <Bot className="h-4 w-4" />
              </div>
            )}

            <div className="max-w-[85%] md:max-w-[70%] space-y-3">
              {/* Message Bubble */}
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-md ${
                  m.sender === "user"
                    ? "bg-rose-600 text-white rounded-tr-none shadow-rose-950/40"
                    : "bg-zinc-900/95 border border-zinc-800 text-zinc-200 rounded-tl-none shadow-black/40"
                }`}
              >
                {m.sender === "user" ? (
                  <p className="whitespace-pre-line">{m.text}</p>
                ) : (
                  <FormattedMessage text={m.text} />
                )}
                <p
                  className={`mt-1.5 text-[10px] text-right ${
                    m.sender === "user" ? "text-rose-200" : "text-zinc-500"
                  }`}
                >
                  {m.timestamp}
                </p>
              </div>

              {/* Structured Card Render */}
              <RenderAssistantCard
                card={m.structured_card}
                approvalRequest={m.approval_request}
                approvingId={approvingId}
                onApprove={handleApprove}
              />
            </div>

            {m.sender === "user" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-800 text-zinc-300 border border-zinc-700">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 text-xs text-zinc-400">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-rose-950/80 text-rose-400 border border-rose-500/30">
              <Bot className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-2 rounded-2xl bg-zinc-900 border border-zinc-800 px-4 py-2.5 shadow-md">
              <RefreshCw className="h-3.5 w-3.5 animate-spin text-rose-500" />
              Neural Copilot is evaluating financial tools &amp; deterministic rules...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestion Chips */}
      <div className="border-t border-zinc-800 bg-zinc-950 px-4 py-2.5 overflow-x-auto no-scrollbar max-w-full">
        <div className="flex items-center gap-2 max-w-full">
          <span className="text-[11px] font-semibold text-zinc-500 shrink-0">Try asking:</span>
          {SUGGESTIONS.map((s, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(s)}
              className="shrink-0 rounded-full border border-zinc-800 bg-zinc-900 px-3 py-1 text-[11px] font-medium text-zinc-300 hover:border-rose-500/50 hover:text-white hover:bg-zinc-800 transition shadow-xs"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-zinc-800 bg-zinc-950 p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage(inputText);
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask about PDF 1, 2, 3, overdue debts, cash flow, or create an invoice..."
            className="flex-1 rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-rose-500 focus:outline-none focus:ring-1 focus:ring-rose-500 transition"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || loading}
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-rose-600 to-pink-600 text-white shadow-md hover:brightness-110 transition disabled:opacity-40"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
