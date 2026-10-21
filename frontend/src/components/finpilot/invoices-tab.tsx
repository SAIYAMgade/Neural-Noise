"use client";

import React, { useState, useEffect } from "react";
import {
  FileText,
  Plus,
  Download,
  CheckCircle2,
  AlertCircle,
  Clock,
  Filter,
  Search,
  RefreshCw,
  X,
  Trash2,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";
import {
  getInvoices,
  getClients,
  createInvoiceDraft,
  previewInvoice,
  issueInvoice,
  cancelInvoice,
  type InvoiceData,
  type ClientData,
  type InvoiceLineItemData,
} from "@/lib/api";
import { formatINR, formatDate, STATUS_STYLES } from "./utils";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const GST_RATES = [0, 5, 12, 18, 28];

export function InvoicesTab() {
  const [invoices, setInvoices] = useState<InvoiceData[]>([]);
  const [clients, setClients] = useState<ClientData[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedClientId, setSelectedClientId] = useState("");
  const [dueDateDays, setDueDateDays] = useState(15);
  const [notes, setNotes] = useState("");
  const [lineItems, setLineItems] = useState<InvoiceLineItemData[]>([
    {
      description: "Consulting & Engineering Services",
      hsn_sac: "998313",
      quantity: 1,
      unit_price: 50000,
      discount_rate: 0,
      gst_rate: 18,
    },
  ]);
  const [previewData, setPreviewData] = useState<any>(null);
  const [creating, setCreating] = useState(false);
  const [issuingId, setIssuingId] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [invList, clientList] = await Promise.all([
        getInvoices(),
        getClients(),
      ]);
      setInvoices(Array.isArray(invList) ? invList : []);
      setClients(Array.isArray(clientList) ? clientList : []);
      if (Array.isArray(clientList) && clientList.length > 0 && !selectedClientId) {
        setSelectedClientId(clientList[0].id);
      }
    } catch (err) {
      console.error("Failed to load invoices data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Update preview when line items or client changes
  useEffect(() => {
    if (!selectedClientId || lineItems.length === 0) return;
    const fetchPreview = async () => {
      try {
        const prev = await previewInvoice({
          client_id: selectedClientId,
          line_items: lineItems.map((item) => ({
            ...item,
            quantity: Number(item.quantity) || 1,
            unit_price: Number(item.unit_price) || 0,
            gst_rate: Number(item.gst_rate) || 18,
          })),
        });
        setPreviewData(prev);
      } catch (err) {
        // quiet error on preview
      }
    };
    fetchPreview();
  }, [selectedClientId, lineItems]);

  const handleAddLineItem = () => {
    setLineItems((prev) => [
      ...prev,
      {
        description: "Additional Deliverable",
        hsn_sac: "998313",
        quantity: 1,
        unit_price: 10000,
        discount_rate: 0,
        gst_rate: 18,
      },
    ]);
  };

  const handleRemoveLineItem = (index: number) => {
    if (lineItems.length <= 1) return;
    setLineItems((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpdateLineItem = (index: number, field: keyof InvoiceLineItemData, value: any) => {
    setLineItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, [field]: value } : item))
    );
  };

  const handleCreateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClientId) {
      alert("Please select a client.");
      return;
    }
    setCreating(true);
    try {
      const dueDate = new Date();
      dueDate.setDate(dueDate.getDate() + Number(dueDateDays));

      await createInvoiceDraft({
        client_id: selectedClientId,
        due_date: dueDate.toISOString().split("T")[0],
        notes,
        line_items: lineItems.map((item) => ({
          description: item.description,
          hsn_sac: item.hsn_sac,
          quantity: Number(item.quantity),
          unit_price: Number(item.unit_price),
          discount_rate: Number(item.discount_rate || 0),
          gst_rate: Number(item.gst_rate),
        })),
      });

      setIsModalOpen(false);
      await loadData();
    } catch (err: any) {
      alert(`Error creating draft invoice: ${err.message || "Failed"}`);
    } finally {
      setCreating(false);
    }
  };

  const handleIssueInvoice = async (invoiceId: string) => {
    if (!confirm("Are you sure you want to issue this invoice? A permanent sequential invoice number (INV-YYYY-NNNN) will be assigned.")) {
      return;
    }
    setIssuingId(invoiceId);
    try {
      await issueInvoice(invoiceId, crypto.randomUUID());
      await loadData();
    } catch (err: any) {
      alert(`Failed to issue invoice: ${err.message || "Error"}`);
    } finally {
      setIssuingId(null);
    }
  };

  const handleCancelInvoice = async (invoiceId: string) => {
    const reason = prompt("Enter cancellation reason:", "Client requested cancellation");
    if (reason === null) return;
    try {
      await cancelInvoice(invoiceId, reason);
      await loadData();
    } catch (err: any) {
      alert(`Failed to cancel invoice: ${err.message || "Error"}`);
    }
  };

  const filteredInvoices = (Array.isArray(invoices) ? invoices : []).filter((inv) => {
    if (!inv) return false;
    const invNum = inv.invoice_number || "";
    const clientName = inv.client_name || "";
    const invStatus = inv.status || "draft";
    const matchesStatus = filterStatus === "all" || invStatus === filterStatus;
    const matchesSearch =
      invNum.toLowerCase().includes(searchQuery.toLowerCase()) ||
      clientName.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Invoices &amp; Tax Documents</h2>
          <p className="text-xs text-zinc-400">
            Indian GST-compliant invoices with deterministic intra/inter-state tax splitting and sequential numbering.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition"
          >
            <Plus className="h-4 w-4" />
            Create Invoice Draft
          </button>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 rounded-xl border border-zinc-800 bg-zinc-900 p-3 shadow-xs">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Search className="h-4 w-4 text-zinc-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by invoice # or client..."
            className="text-xs text-zinc-200 placeholder-slate-400 focus:outline-none w-full sm:w-64"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar w-full sm:w-auto">
          {["all", "draft", "issued", "partially_paid", "paid", "overdue"].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`rounded-lg px-2.5 py-1 text-xs font-medium capitalize transition ${
                filterStatus === st
                  ? "bg-slate-900 text-white"
                  : "bg-zinc-800 text-zinc-400 hover:bg-slate-200"
              }`}
            >
              {st.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {/* Invoices Table */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 shadow-sm overflow-hidden">
        {loading ? (
          <div className="py-12 text-center text-xs text-zinc-500">
            <RefreshCw className="h-5 w-5 animate-spin mx-auto mb-2 text-indigo-600" />
            Loading invoices ledger...
          </div>
        ) : filteredInvoices.length === 0 ? (
          <div className="py-12 text-center text-xs text-zinc-500">
            No invoices found matching your criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-950/70 text-zinc-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Invoice #</th>
                  <th className="py-3 px-4">Client</th>
                  <th className="py-3 px-4">Dates</th>
                  <th className="py-3 px-4">Tax Type</th>
                  <th className="py-3 px-4">Subtotal</th>
                  <th className="py-3 px-4">GST Tax</th>
                  <th className="py-3 px-4">Total</th>
                  <th className="py-3 px-4">Balance</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {filteredInvoices.map((inv) => {
                  const status = inv.status || "draft";
                  const style = STATUS_STYLES[status] || STATUS_STYLES.draft || { bg: "bg-zinc-800", text: "text-zinc-300", border: "border-zinc-800" };
                  const isInter = inv.is_interstate ?? (inv.tax_type === "inter_state");
                  const totalTax = Number(inv.total_tax) || (Number(inv.cgst_amount || inv.cgst_total || 0) + Number(inv.sgst_amount || inv.sgst_total || 0) + Number(inv.igst_amount || inv.igst_total || 0));
                  const subtotal = Number(inv.subtotal) || 0;
                  const totalAmount = Number(inv.grand_total || inv.total_amount) || 0;
                  const balanceDue = Number(inv.amount_due || inv.balance_due) || 0;
                  const issueDate = inv.invoice_date || inv.issue_date;
                  const dueDate = inv.due_date;

                  return (
                    <tr key={inv.id} className="hover:bg-zinc-950/50 transition">
                      <td className="py-3 px-4 font-mono font-bold text-white">
                        {inv.invoice_number}
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-semibold text-zinc-200">{inv.client_name || "Client"}</span>
                      </td>
                      <td className="py-3 px-4 text-[11px] text-zinc-400">
                        <div>Issue: {formatDate(issueDate)}</div>
                        <div>Due: {formatDate(dueDate)}</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-[10px] font-semibold ${
                          isInter ? "bg-amber-50 text-amber-700 border border-amber-200" : "bg-blue-50 text-blue-700 border border-blue-200"
                        }`}>
                          {isInter ? "IGST (Inter)" : "CGST+SGST (Intra)"}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-zinc-400">
                        {formatINR(subtotal)}
                      </td>
                      <td className="py-3 px-4 text-zinc-400 font-medium">
                        {formatINR(totalTax)}
                      </td>
                      <td className="py-3 px-4 font-bold text-white">
                        {formatINR(totalAmount)}
                      </td>
                      <td className="py-3 px-4 font-bold text-indigo-600">
                        {formatINR(balanceDue)}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold capitalize ${style.bg} ${style.text} ${style.border}`}>
                          {status.replace("_", " ")}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* PDF Download Button */}
                          <a
                            href={`${API_BASE}/api/v1/invoices/${inv.id}/pdf`}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 rounded-lg border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-[11px] font-medium text-zinc-300 hover:bg-zinc-950 transition shadow-xs"
                            title="Download Indian GST Tax PDF"
                          >
                            <Download className="h-3 w-3" />
                            PDF
                          </a>

                          {/* Issue Button (if draft) */}
                          {inv.status === "draft" && (
                            <button
                              onClick={() => handleIssueInvoice(inv.id)}
                              disabled={issuingId === inv.id}
                              className="inline-flex items-center gap-1 rounded-lg bg-emerald-600 px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-emerald-500 transition shadow-xs disabled:opacity-50"
                              title="Officially issue invoice"
                            >
                              <CheckCircle2 className="h-3 w-3" />
                              Issue
                            </button>
                          )}

                          {/* Cancel Button */}
                          {inv.status !== "cancelled" && inv.status !== "paid" && (
                            <button
                              onClick={() => handleCancelInvoice(inv.id)}
                              className="rounded-lg p-1 text-zinc-500 hover:text-rose-600 transition"
                              title="Cancel invoice"
                            >
                              <X className="h-3.5 w-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Invoice Draft Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-2xl rounded-2xl bg-zinc-900 p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">Create Invoice Draft</h3>
                <p className="text-xs text-zinc-400">
                  Calculates deterministic GST line items and previews tax split before saving.
                </p>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="rounded-lg p-1 text-zinc-500 hover:text-zinc-400"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateDraft} className="mt-4 space-y-4">
              {/* Client Selection */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Select Client *
                  </label>
                  <select
                    value={selectedClientId}
                    onChange={(e) => setSelectedClientId(e.target.value)}
                    required
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  >
                    {clients.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name} {c.gstin ? `(${c.gstin})` : ""}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Payment Terms (Due in Days)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="180"
                    value={dueDateDays}
                    onChange={(e) => setDueDateDays(Number(e.target.value))}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Line Items */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-bold text-zinc-200 uppercase tracking-wider">
                    Itemized Deliverables &amp; Services
                  </label>
                  <button
                    type="button"
                    onClick={handleAddLineItem}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    Add Item
                  </button>
                </div>

                <div className="space-y-2">
                  {lineItems.map((item, idx) => (
                    <div
                      key={idx}
                      className="grid grid-cols-12 gap-2 rounded-xl border border-zinc-800 bg-zinc-950/50 p-2.5 items-center"
                    >
                      <div className="col-span-5">
                        <input
                          type="text"
                          placeholder="Description"
                          value={item.description}
                          onChange={(e) => handleUpdateLineItem(idx, "description", e.target.value)}
                          required
                          className="w-full rounded-lg border border-zinc-800 bg-zinc-900 p-1.5 text-xs text-zinc-200"
                        />
                      </div>
                      <div className="col-span-2">
                        <input
                          type="text"
                          placeholder="HSN/SAC"
                          value={item.hsn_sac}
                          onChange={(e) => handleUpdateLineItem(idx, "hsn_sac", e.target.value)}
                          className="w-full rounded-lg border border-zinc-800 bg-zinc-900 p-1.5 text-xs text-zinc-200"
                        />
                      </div>
                      <div className="col-span-1">
                        <input
                          type="number"
                          min="1"
                          placeholder="Qty"
                          value={item.quantity}
                          onChange={(e) => handleUpdateLineItem(idx, "quantity", e.target.value)}
                          className="w-full rounded-lg border border-zinc-800 bg-zinc-900 p-1.5 text-xs text-zinc-200"
                        />
                      </div>
                      <div className="col-span-2">
                        <input
                          type="number"
                          placeholder="Price (₹)"
                          value={item.unit_price}
                          onChange={(e) => handleUpdateLineItem(idx, "unit_price", e.target.value)}
                          className="w-full rounded-lg border border-zinc-800 bg-zinc-900 p-1.5 text-xs text-zinc-200"
                        />
                      </div>
                      <div className="col-span-1">
                        <select
                          value={item.gst_rate}
                          onChange={(e) => handleUpdateLineItem(idx, "gst_rate", Number(e.target.value))}
                          className="w-full rounded-lg border border-zinc-800 bg-zinc-900 p-1.5 text-xs text-zinc-200"
                        >
                          {GST_RATES.map((r) => (
                            <option key={r} value={r}>
                              {r}%
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="col-span-1 text-right">
                        <button
                          type="button"
                          onClick={() => handleRemoveLineItem(idx)}
                          disabled={lineItems.length <= 1}
                          className="rounded-md p-1 text-zinc-500 hover:text-rose-600 disabled:opacity-30"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">
                  Payment Instructions / Notes
                </label>
                <input
                  type="text"
                  placeholder="e.g. Bank transfer to HDFC A/c 502000... or UPI saiyam@upi"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              {/* Live Preview Calculation */}
              {previewData && (
                <div className="rounded-xl border border-indigo-100 bg-indigo-50/40 p-4 space-y-1.5 text-xs">
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Tax Jurisdiction:</span>
                    <span className="font-semibold text-zinc-200">
                      {previewData.is_interstate ? "Inter-State (IGST 18%)" : "Intra-State (CGST 9% + SGST 9%)"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-zinc-400">
                    <span>Subtotal:</span>
                    <span>{formatINR(previewData.subtotal)}</span>
                  </div>
                  {!previewData.is_interstate ? (
                    <>
                      <div className="flex items-center justify-between text-zinc-400">
                        <span>CGST (Central GST):</span>
                        <span>{formatINR(previewData.cgst_total)}</span>
                      </div>
                      <div className="flex items-center justify-between text-zinc-400">
                        <span>SGST (State GST):</span>
                        <span>{formatINR(previewData.sgst_total)}</span>
                      </div>
                    </>
                  ) : (
                    <div className="flex items-center justify-between text-zinc-400">
                      <span>IGST (Integrated GST):</span>
                      <span>{formatINR(previewData.igst_total)}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between border-t border-indigo-200/60 pt-2 font-bold text-sm text-white">
                    <span>Total Amount:</span>
                    <span className="text-indigo-600">{formatINR(previewData.total_amount)}</span>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-2 border-t border-zinc-800 pt-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-950 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition disabled:opacity-50"
                >
                  {creating ? (
                    <>
                      <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                      Saving Draft...
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      Save as Draft
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
