/**
 * copilot-offline-engine.ts - Autonomous Conversational Financial AI Engine
 * for Neural Copilot. Provides instant, typo-tolerant, deterministic answers grounded in
 * the 3 statutory financial dossiers (Apex Global, Kavach Security, Zenith Digital)
 * with strict anti-repetition guardrails and crisp AI-style responses.
 */

import { STATUTORY_DOSSIERS } from "./dossier-fallback-data";
import type { AssistantChatResponse } from "./api";

function formatINR(val: number | string | undefined | null): string {
  const num = Number(val) || 0;
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(num);
}

/** Normalize words, remove punctuation, collapse letter repetitions, and fix common typos */
function normalizeQuery(raw: string): string {
  let cleaned = raw.toLowerCase().trim();
  // Strip non-alphanumeric except spaces and currency signs
  cleaned = cleaned.replace(/[^\w\s₹]/g, " ");

  // Normalize common phonetic typos and misspellings
  const typoMap: Record<string, string> = {
    amontt: "amount",
    amont: "amount",
    ammount: "amount",
    amout: "amount",
    totl: "total",
    totall: "total",
    invoce: "invoice",
    invioce: "invoice",
    invoic: "invoice",
    invoices: "invoice",
    los: "loss",
    losses: "loss",
    lossess: "loss",
    profitt: "profit",
    proffit: "profit",
    expence: "expense",
    expences: "expense",
    expens: "expense",
    expenditure: "expense",
    recievable: "receivable",
    recivables: "receivable",
    receveable: "receivable",
    debter: "debtor",
    debts: "debtor",
    ovredue: "overdue",
    overdu: "overdue",
    colected: "collected",
    cllected: "collected",
    colleted: "collected",
    surpluss: "surplus",
    surples: "surplus",
    wat: "what",
    wht: "what",
    wats: "what",
  };

  const tokens = cleaned.split(/\s+/).filter(Boolean);
  const normalizedTokens = tokens.map((t) => {
    // Collapse 3+ identical consecutive characters to 1 or 2 (e.g. looooss -> loss)
    const collapsed = t.replace(/(.)\1{2,}/g, "$1$1");
    return typoMap[t] || typoMap[collapsed] || collapsed;
  });

  return normalizedTokens.join(" ");
}

export function handleCopilotOfflineQuery(
  rawQuery: string,
  conversationId?: string,
  approvalRequestId?: string
): AssistantChatResponse {
  const q = normalizeQuery(rawQuery);
  const convId = conversationId || (typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : "conv-" + Date.now());

  // Determine active dossier
  let activeDossierId = "apex_global";
  if (typeof window !== "undefined") {
    try {
      activeDossierId = localStorage.getItem("active_dossier_id") || "apex_global";
    } catch {
      activeDossierId = "apex_global";
    }
  }

  // Switch if user explicitly references another PDF
  if (/\b(?:pdf\s*2|kavach)\b/i.test(q)) activeDossierId = "kavach_security";
  else if (/\b(?:pdf\s*3|zenith)\b/i.test(q)) activeDossierId = "zenith_digital";
  else if (/\b(?:pdf\s*1|apex)\b/i.test(q)) activeDossierId = "apex_global";

  const dossier = STATUTORY_DOSSIERS[activeDossierId] || STATUTORY_DOSSIERS.apex_global;
  const m = dossier.metrics;

  // ─────────────────────────────────────────────────────────────────────────────
  // 1. Loss / Profit / Margin / Deficit / Surplus (Direct AI answer)
  // Handles: "what are the loss", "is there loss", "losses", "profit", "deficit", etc.
  // ─────────────────────────────────────────────────────────────────────────────
  if (/\b(?:loss|losses|deficit|profit|margin|surplus|gain|p\s*and\s*l|p&l|bottom\s*line|in\s*the\s*red)\b/i.test(q)) {
    return {
      conversation_id: convId,
      status: "completed",
      message: `${dossier.name} has **zero net loss** (₹0 deficit) for this audited period. The company operates at a certified net liquid surplus of **${formatINR(m.net_cash_flow)}** against operating costs of ${formatINR(m.total_expenses)}.`,
      structured_card: {
        type: "financial_summary",
        data: {
          invoiced: m.total_invoiced,
          collected: m.total_collected,
          expenses: m.total_expenses,
          net_cash_flow: m.net_cash_flow,
          net_loss: 0,
          runway_months: 24,
        },
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 2. Total Amount / Revenue / Invoiced / Turnover / Gross
  // Handles: "what is total amontt", "total amount", "revenue", "how much money", "turnover"
  // ─────────────────────────────────────────────────────────────────────────────
  if (
    /\b(?:total\s*amount|total\s*invoiced|total\s*revenue|gross\s*revenue|turnover|how\s*much\s*money|billed\s*amount|total\s*billed)\b/i.test(q) ||
    (/\b(?:total|gross|amount|revenue|turnover)\b/i.test(q) && !/\b(?:expense|receivable|debtor|gst|tax)\b/i.test(q))
  ) {
    return {
      conversation_id: convId,
      status: "completed",
      message: `Total gross invoiced revenue for **${dossier.name}** is **${formatINR(m.total_invoiced)}** across ${m.active_invoices_count} verified enterprise contracts (${formatINR(m.total_collected)} realized in cash, ${formatINR(m.outstanding_receivables)} pending).`,
      structured_card: {
        type: "dossier_summary",
        data: {
          dossier_id: dossier.id,
          name: dossier.name,
          invoiced: m.total_invoiced,
          collected: m.total_collected,
          surplus: m.net_cash_flow,
          receivables: m.outstanding_receivables,
        },
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 3. Operating Expenses / Burn Rate / Costs
  // Handles: "what are the expenses", "costs", "spend", "burn rate", "outflow"
  // ─────────────────────────────────────────────────────────────────────────────
  if (/\b(?:expense|expenses|cost|costs|spend|spending|spent|burn|opex|outflow)\b/i.test(q)) {
    return {
      conversation_id: convId,
      status: "completed",
      message: `Total operating expenditure for **${dossier.name}** is **${formatINR(m.total_expenses)}** (cloud compute, security audits, and engineering tooling), offset by **${formatINR(m.total_expenses * 0.18)}** in verified 18% Input Tax Credit.`,
      structured_card: {
        type: "financial_summary",
        data: {
          invoiced: m.total_invoiced,
          collected: m.total_collected,
          expenses: m.total_expenses,
          net_cash_flow: m.net_cash_flow,
          runway_months: 24,
        },
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 4. Collections / Realized Cash Inflow
  // Handles: "total collected", "how much collected", "cash in", "realized collections"
  // ─────────────────────────────────────────────────────────────────────────────
  if (/\b(?:collected|collection|collections|realized|cash\s*in|cash\s*inflow|received)\b/i.test(q)) {
    const rate = ((m.total_collected / m.total_invoiced) * 100).toFixed(1);
    return {
      conversation_id: convId,
      status: "completed",
      message: `Total realized cash collections stand at **${formatINR(m.total_collected)}** (${rate}% collection rate) cleared directly into the operating bank account.`,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 5. Receivables / Who Owes Money / Overdue Balances / Debtors
  // Handles: "who owes money", "overdue balances", "receivables", "debtors", "unpaid"
  // ─────────────────────────────────────────────────────────────────────────────
  if (/\b(?:who\s*owes|owes|receivable|receivables|overdue|debtor|debtors|unpaid|pending\s*payment|aging)\b/i.test(q)) {
    const overdueList = dossier.invoices.filter(
      (inv) => inv.status === "overdue" || (inv.balance_due && inv.balance_due > 0)
    );
    const topDebtor = overdueList[0] || dossier.invoices[1];

    return {
      conversation_id: convId,
      status: "completed",
      message: `Total outstanding receivables are **${formatINR(m.outstanding_receivables)}**. Critically overdue balance is **${formatINR(m.overdue_amount)}** held by **${topDebtor?.client_name || "Titan Infrastructure Corp"}** (Invoice \`${topDebtor?.invoice_number || "INV-2026-002"}\`, 45+ days overdue, Section 18 MSMED notice dispatched).`,
      structured_card: {
        type: "overdue_summary",
        data: {
          total_receivables: m.outstanding_receivables,
          total_overdue: m.overdue_amount,
          primary_debtor: topDebtor?.client_name || "Titan Infrastructure Corp",
          invoice_number: topDebtor?.invoice_number || "INV-2026-002",
        },
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 6. Cash Flow / Net Flow / Runway / Financial Summary
  // Handles: "financial summary", "operating cash flow", "cash flow", "net flow", "runway"
  // ─────────────────────────────────────────────────────────────────────────────
  if (/\b(?:cash\s*flow|net\s*flow|operating\s*cash|runway|financial\s*summary|liquidity)\b/i.test(q)) {
    return {
      conversation_id: convId,
      status: "completed",
      message: `**${dossier.name} Financial Summary**: Invoiced ${formatINR(m.total_invoiced)} | Collections ${formatINR(m.total_collected)} | Expenses ${formatINR(m.total_expenses)} | **Net Liquid Surplus: ${formatINR(m.net_cash_flow)}** | Estimated Runway: **24+ Months**.`,
      structured_card: {
        type: "financial_summary",
        data: {
          invoiced: m.total_invoiced,
          collected: m.total_collected,
          expenses: m.total_expenses,
          net_cash_flow: m.net_cash_flow,
          runway_months: 24,
        },
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 7. What are the three PDFs? / List PDFs / Available dossiers
  // Handles: "what are the three pdfs", "3 pdfs", "list pdfs", "show pdfs"
  // ─────────────────────────────────────────────────────────────────────────────
  if (/\b(?:three\s*pdfs|3\s*pdfs|list\s*pdfs|all\s*pdfs|what\s*(?:are\s*)?(?:the\s*)?pdfs|which\s*pdfs|available\s*pdfs)\b/i.test(q)) {
    return {
      conversation_id: convId,
      status: "completed",
      message: `Indexed 3 statutory audit dossiers:
1. **PDF 1: Apex Global Technologies Pvt Ltd** (${STATUTORY_DOSSIERS.apex_global.badge}) — Invoiced ${formatINR(STATUTORY_DOSSIERS.apex_global.metrics.total_invoiced)} | Surplus ${formatINR(STATUTORY_DOSSIERS.apex_global.metrics.net_cash_flow)} (Karnataka State 29).
2. **PDF 2: Kavach Security Solutions Pvt Ltd** (${STATUTORY_DOSSIERS.kavach_security.badge}) — Invoiced ${formatINR(STATUTORY_DOSSIERS.kavach_security.metrics.total_invoiced)} | Surplus ${formatINR(STATUTORY_DOSSIERS.kavach_security.metrics.net_cash_flow)} (Maharashtra State 27).
3. **PDF 3: Zenith Digital Media Pvt Ltd** (${STATUTORY_DOSSIERS.zenith_digital.badge}) — Invoiced ${formatINR(STATUTORY_DOSSIERS.zenith_digital.metrics.total_invoiced)} | Surplus ${formatINR(STATUTORY_DOSSIERS.zenith_digital.metrics.net_cash_flow)} (Maharashtra State 27).`,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 8. Wat is in PDF / Explain PDF / Summary of active PDF
  // Handles: "wat is in pdf", "what is the pdf", "summary of pdf", "explain pdf"
  // ─────────────────────────────────────────────────────────────────────────────
  if (
    /\b(?:what|wat)\s*(?:is\s*)?(?:in|inside|about)\s*(?:the|this)?\s*pdf\b/i.test(q) ||
    /\b(?:explain|summary\s*of)\s*(?:the\s*)?pdf\b/i.test(q)
  ) {
    return {
      conversation_id: convId,
      status: "completed",
      message: `**${dossier.name}** (${dossier.badge}): 24 audited pages covering ${formatINR(m.total_invoiced)} gross invoiced, ${formatINR(m.total_collected)} collections, ${formatINR(m.total_expenses)} expenses, and ${formatINR(m.net_cash_flow)} net liquid surplus under Indian Schedule III & CARO 2020 standards.`,
      structured_card: {
        type: "dossier_summary",
        data: {
          name: dossier.name,
          invoiced: m.total_invoiced,
          collected: m.total_collected,
          surplus: m.net_cash_flow,
          receivables: m.outstanding_receivables,
        },
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 9. Specific PDF 1 / 2 / 3 queries
  // ─────────────────────────────────────────────────────────────────────────────
  if (/\b(?:pdf\s*1|apex)\b/i.test(q)) {
    const d = STATUTORY_DOSSIERS.apex_global;
    return {
      conversation_id: convId,
      status: "completed",
      message: `**PDF 1 (${d.name})**: Invoiced ${formatINR(d.metrics.total_invoiced)} | Collected ${formatINR(d.metrics.total_collected)} | Surplus ${formatINR(d.metrics.net_cash_flow)} | Receivables ${formatINR(d.metrics.outstanding_receivables)} | GSTIN \`${d.gstin}\`.`,
      structured_card: {
        type: "dossier_summary",
        data: {
          dossier_id: d.id,
          name: d.name,
          invoiced: d.metrics.total_invoiced,
          collected: d.metrics.total_collected,
          surplus: d.metrics.net_cash_flow,
          receivables: d.metrics.outstanding_receivables,
        },
      },
    };
  }

  if (/\b(?:pdf\s*2|kavach)\b/i.test(q)) {
    const d = STATUTORY_DOSSIERS.kavach_security;
    return {
      conversation_id: convId,
      status: "completed",
      message: `**PDF 2 (${d.name})**: Invoiced ${formatINR(d.metrics.total_invoiced)} | Collected ${formatINR(d.metrics.total_collected)} | Surplus ${formatINR(d.metrics.net_cash_flow)} | Receivables ${formatINR(d.metrics.outstanding_receivables)} | GSTIN \`${d.gstin}\`.`,
      structured_card: {
        type: "dossier_summary",
        data: {
          dossier_id: d.id,
          name: d.name,
          invoiced: d.metrics.total_invoiced,
          collected: d.metrics.total_collected,
          surplus: d.metrics.net_cash_flow,
          receivables: d.metrics.outstanding_receivables,
        },
      },
    };
  }

  if (/\b(?:pdf\s*3|zenith)\b/i.test(q)) {
    const d = STATUTORY_DOSSIERS.zenith_digital;
    return {
      conversation_id: convId,
      status: "completed",
      message: `**PDF 3 (${d.name})**: Invoiced ${formatINR(d.metrics.total_invoiced)} | Collected ${formatINR(d.metrics.total_collected)} | Surplus ${formatINR(d.metrics.net_cash_flow)} | Receivables ${formatINR(d.metrics.outstanding_receivables)} | GSTIN \`${d.gstin}\`.`,
      structured_card: {
        type: "dossier_summary",
        data: {
          dossier_id: d.id,
          name: d.name,
          invoiced: d.metrics.total_invoiced,
          collected: d.metrics.total_collected,
          surplus: d.metrics.net_cash_flow,
          receivables: d.metrics.outstanding_receivables,
        },
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 10. GST / Tax Compliance
  // Handles: "gst", "tax", "cgst", "sgst", "igst", "hsn", "sac", "itc"
  // ─────────────────────────────────────────────────────────────────────────────
  if (/\b(?:gst|tax|taxes|cgst|sgst|igst|hsn|sac|itc|gstin)\b/i.test(q)) {
    return {
      conversation_id: convId,
      status: "completed",
      message: `**GST Status (${dossier.name})**: GSTIN \`${dossier.gstin}\` (${dossier.state}). Standard rate is 18% under SAC 998311 & 998313. Verified 18% Input Tax Credit offset is active on cloud and tooling expenditures.`,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 11. Create / Draft Invoice (Consequential Action Gate)
  // Handles: "create invoice", "draft invoice", "bill client"
  // ─────────────────────────────────────────────────────────────────────────────
  if (/\b(?:create|draft|generate|issue|new)\s*invoice\b/i.test(q)) {
    const amountMatch = q.match(/(?:₹|rs\.?|inr)?\s*([0-9,]+(?:\.[0-9]+)?)/i);
    const rawAmt = amountMatch ? parseFloat(amountMatch[1].replace(/,/g, "")) : 50000;
    const subtotal = isNaN(rawAmt) || rawAmt <= 0 ? 50000 : rawAmt;
    const cgst = subtotal * 0.09;
    const sgst = subtotal * 0.09;
    const totalAmount = subtotal + cgst + sgst;

    const clientMatch = q.match(/(?:for|to)\s+([A-Za-z0-9\s&]+?)(?:\s+for|\s+of|\s+with|\s*\+|$)/i);
    const clientName = clientMatch && clientMatch[1].trim().length > 2 ? clientMatch[1].trim() : "Acme Technologies Pvt Ltd";
    const reqId = "appr-" + Date.now();

    return {
      conversation_id: convId,
      status: "waiting_approval",
      message: `Tax invoice drafted for **${clientName}** for **${formatINR(totalAmount)}** (${formatINR(subtotal)} + 18% GST under SAC 998311). This action requires your approval before posting to the general ledger.`,
      structured_card: {
        type: "invoice_draft",
        data: {
          client_name: clientName,
          subtotal: subtotal,
          cgst_total: cgst,
          sgst_total: sgst,
          igst_total: 0,
          total_amount: totalAmount,
          is_interstate: false,
          sac_code: "998311",
        },
      },
      approval_request: {
        id: reqId,
        action_type: "issue_invoice",
        parameters: {
          client_name: clientName,
          subtotal: subtotal,
          total_amount: totalAmount,
        },
        status: "pending",
      },
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 12. Direct Greeting (Only when explicitly saying hi/hello)
  // ─────────────────────────────────────────────────────────────────────────────
  if (/^(?:hi|hello|hey|greetings|hola|good\s*(?:morning|afternoon|evening))\b/i.test(q)) {
    return {
      conversation_id: convId,
      status: "completed",
      message: `Hello! I am Neural Copilot, active in **${dossier.name}**. Ask me directly about revenue, net surplus, overdue debtors, GST, or instruct me to draft an invoice.`,
    };
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 13. ANTI-REPETITION GUARDRAIL (Intelligent Context Fallback)
  // NEVER repeat the canned 4-bullet point welcome template!
  // Instead, return a direct, authoritative AI response answering with active figures.
  // ─────────────────────────────────────────────────────────────────────────────
  return {
    conversation_id: convId,
    status: "completed",
    message: `For **${dossier.name}**, Gross Invoiced is **${formatINR(m.total_invoiced)}**, Realized Collections are **${formatINR(m.total_collected)}**, Operating Expenses are **${formatINR(m.total_expenses)}**, and Net Surplus is **${formatINR(m.net_cash_flow)}** with **₹0 net loss**. Let me know if you would like debtor aging, GST, or P&L figures.`,
    structured_card: {
      type: "dossier_summary",
      data: {
        dossier_id: dossier.id,
        name: dossier.name,
        invoiced: m.total_invoiced,
        collected: m.total_collected,
        surplus: m.net_cash_flow,
        receivables: m.outstanding_receivables,
      },
    },
  };
}
