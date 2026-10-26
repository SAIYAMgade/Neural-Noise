"use client";

import React, { useState, useEffect } from "react";
import {
  CreditCard,
  Plus,
  RefreshCw,
  X,
  CheckCircle2,
  AlertCircle,
  FileText,
  DollarSign,
  ArrowDownRight,
} from "lucide-react";
import {
  getPayments,
  getClients,
  getInvoices,
  recordPayment,
  allocatePayment,
  type PaymentData,
  type ClientData,
  type InvoiceData,
} from "@/lib/api";
import { formatINR, formatDate } from "./utils";

const PAYMENT_METHODS = ["UPI", "NEFT", "IMPS", "RTGS", "Bank Transfer", "Credit Card", "Cash"];

export function PaymentsTab() {
  const [payments, setPayments] = useState<PaymentData[]>([]);
  const [clients, setClients] = useState<ClientData[]>([]);
  const [loading, setLoading] = useState(true);

  // Record Payment Modal
  const [isRecordModalOpen, setIsRecordModalOpen] = useState(false);
  const [selectedClientId, setSelectedClientId] = useState("");
  const [amount, setAmount] = useState(50000);
  const [paymentMethod, setPaymentMethod] = useState("UPI");
  const [referenceNumber, setReferenceNumber] = useState("");
  const [notes, setNotes] = useState("");
  const [autoAllocateInvoiceId, setAutoAllocateInvoiceId] = useState<string>("");
  const [clientInvoices, setClientInvoices] = useState<InvoiceData[]>([]);
  const [submitting, setSubmitting] = useState(false);

  // Allocate Modal
  const [allocatingPayment, setAllocatingPayment] = useState<PaymentData | null>(null);
  const [pendingInvoices, setPendingInvoices] = useState<InvoiceData[]>([]);
  const [targetInvoiceId, setTargetInvoiceId] = useState("");
  const [allocAmount, setAllocAmount] = useState(0);

  const loadData = async () => {
    try {
      const [payList, clientList] = await Promise.all([
        getPayments(),
        getClients(),
      ]);
      setPayments(Array.isArray(payList) ? payList : []);
      setClients(Array.isArray(clientList) ? clientList : []);
      if (Array.isArray(clientList) && clientList.length > 0 && !selectedClientId) {
        setSelectedClientId(clientList[0].id);
      }
    } catch (err) {
      console.error("Failed to load payments:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // When client changes in modal, load their unpaid invoices
  useEffect(() => {
    if (!selectedClientId) return;
    const fetchInvoices = async () => {
      try {
        const invs = await getInvoices({ client_id: selectedClientId });
        const unpaid = (Array.isArray(invs) ? invs : []).filter(
          (i) => (Number(i.amount_due || i.balance_due) > 0) && i.status !== "cancelled" && i.status !== "draft"
        );
        setClientInvoices(unpaid);
        if (unpaid.length > 0) {
          setAutoAllocateInvoiceId(unpaid[0].id);
        } else {
          setAutoAllocateInvoiceId("");
        }
      } catch (err) {
        // ignore
      }
    };
    fetchInvoices();
  }, [selectedClientId]);

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClientId || amount <= 0) {
      alert("Please select a client and valid amount.");
      return;
    }

    setSubmitting(true);
    try {
      const payment = await recordPayment({
        client_id: selectedClientId,
        amount: Number(amount),
        payment_method: paymentMethod,
        reference_number: referenceNumber || undefined,
        notes: notes || undefined,
      });

      // If user selected an invoice to allocate to
      if (autoAllocateInvoiceId && payment.id) {
        try {
          await allocatePayment({
            payment_id: payment.id,
            invoice_id: autoAllocateInvoiceId,
            amount_to_allocate: Number(amount),
          });
        } catch (allocErr) {
          console.warn("Payment recorded, but allocation notice:", allocErr);
        }
      }

      setIsRecordModalOpen(false);
      setReferenceNumber("");
      setNotes("");
      await loadData();
    } catch (err: any) {
      alert(`Failed to record payment: ${err.message || "Error"}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenAllocate = async (pay: PaymentData) => {
    setAllocatingPayment(pay);
    try {
      const invs = await getInvoices({ client_id: pay.client_id });
      const unpaid = invs.filter((i) => i.balance_due > 0 && i.status !== "cancelled" && i.status !== "draft");
      setPendingInvoices(unpaid);
      if (unpaid.length > 0) {
        setTargetInvoiceId(unpaid[0].id);
        setAllocAmount(Math.min(pay.unallocated_amount, unpaid[0].balance_due));
      }
    } catch (err) {
      alert("Could not load pending invoices.");
    }
  };

  const handleExecuteAllocation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!allocatingPayment || !targetInvoiceId || allocAmount <= 0) return;

    try {
      await allocatePayment({
        payment_id: allocatingPayment.id,
        invoice_id: targetInvoiceId,
        amount_to_allocate: Number(allocAmount),
      });
      setAllocatingPayment(null);
      await loadData();
    } catch (err: any) {
      alert(`Allocation failed: ${err.message || "Error"}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Payments &amp; Reconciliation</h2>
          <p className="text-xs text-zinc-400">
            Track bank collections, UPI settlements, and allocate funds against pending invoices.
          </p>
        </div>

        <button
          onClick={() => setIsRecordModalOpen(true)}
          className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition"
        >
          <Plus className="h-4 w-4" />
          Record Payment
        </button>
      </div>

      {/* Payments Table */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 shadow-sm overflow-hidden">
        {loading ? (
          <div className="py-12 text-center text-xs text-zinc-500">
            <RefreshCw className="h-5 w-5 animate-spin mx-auto mb-2 text-indigo-600" />
            Loading payments...
          </div>
        ) : payments.length === 0 ? (
          <div className="py-12 text-center text-xs text-zinc-500">
            No payments recorded yet. Click &ldquo;Record Payment&rdquo; to record a client settlement.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-950/70 text-zinc-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Payment #</th>
                  <th className="py-3 px-4">Client</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Method &amp; Reference</th>
                  <th className="py-3 px-4">Unallocated</th>
                  <th className="py-3 px-4">Allocations</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {payments.map((p) => (
                  <tr key={p.id} className="hover:bg-zinc-950/50 transition">
                    <td className="py-3 px-4 font-mono font-bold text-white">
                      {p.payment_number}
                    </td>
                    <td className="py-3 px-4 font-semibold text-zinc-200">
                      {p.client_name || "Client"}
                    </td>
                    <td className="py-3 px-4 font-bold text-emerald-600">
                      {formatINR(p.amount)}
                    </td>
                    <td className="py-3 px-4 text-zinc-400">
                      {formatDate(p.payment_date)}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-medium text-zinc-200">{p.payment_method}</span>
                      {p.reference_number && (
                        <div className="text-[10px] text-zinc-500 font-mono">Ref: {p.reference_number}</div>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {p.unallocated_amount > 0 ? (
                        <span className="font-semibold text-amber-600">
                          {formatINR(p.unallocated_amount)}
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-600 font-medium">
                          <CheckCircle2 className="h-3 w-3" /> Fully Allocated
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {p.allocations && p.allocations.length > 0 ? (
                        <div className="space-y-0.5">
                          {p.allocations.map((a) => (
                            <div key={a.id} className="text-[11px] text-zinc-400">
                              <span className="font-mono text-indigo-600">{a.invoice_number}</span>: {formatINR(a.amount)}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <span className="text-zinc-500 italic">None</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {p.unallocated_amount > 0 && (
                        <button
                          onClick={() => handleOpenAllocate(p)}
                          className="inline-flex items-center gap-1 rounded-lg bg-indigo-50 border border-indigo-200 px-2.5 py-1 text-[11px] font-semibold text-indigo-700 hover:bg-indigo-100 transition shadow-xs"
                        >
                          Allocate
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Record Payment Modal */}
      {isRecordModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-lg rounded-2xl bg-zinc-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">Record Client Payment</h3>
                <p className="text-xs text-zinc-400">
                  Record inbound bank/UPI settlement and allocate against open invoices.
                </p>
              </div>
              <button
                onClick={() => setIsRecordModalOpen(false)}
                className="rounded-lg p-1 text-zinc-500 hover:text-zinc-400"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleRecordPayment} className="mt-4 space-y-3.5">
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
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Amount Received (₹) *
                  </label>
                  <input
                    type="number"
                    min="1"
                    step="0.01"
                    value={amount}
                    onChange={(e) => setAmount(Number(e.target.value))}
                    required
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Payment Method
                  </label>
                  <select
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  >
                    {PAYMENT_METHODS.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">
                  Reference # (UTR / UPI Transaction ID)
                </label>
                <input
                  type="text"
                  placeholder="e.g. UTR198273641 or UPI/40281928"
                  value={referenceNumber}
                  onChange={(e) => setReferenceNumber(e.target.value)}
                  className="w-full rounded-xl border border-zinc-800 p-2 text-xs font-mono text-zinc-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              {/* Allocate directly to an invoice */}
              {clientInvoices.length > 0 && (
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Directly Allocate to Invoice (Optional)
                  </label>
                  <select
                    value={autoAllocateInvoiceId}
                    onChange={(e) => setAutoAllocateInvoiceId(e.target.value)}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="">Leave Unallocated</option>
                    {clientInvoices.map((inv) => (
                      <option key={inv.id} value={inv.id}>
                        {inv.invoice_number} (Due: {formatINR(inv.balance_due)})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">
                  Notes
                </label>
                <input
                  type="text"
                  placeholder="e.g. Received via HDFC current account"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 border-t border-zinc-800 pt-3">
                <button
                  type="button"
                  onClick={() => setIsRecordModalOpen(false)}
                  className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-950 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition disabled:opacity-50"
                >
                  {submitting ? "Recording..." : "Record Payment"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Allocate Payment Modal */}
      {allocatingPayment && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-md rounded-2xl bg-zinc-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">Allocate Payment</h3>
                <p className="text-xs text-zinc-400">
                  {allocatingPayment.payment_number} &middot; Unallocated: {formatINR(allocatingPayment.unallocated_amount)}
                </p>
              </div>
              <button
                onClick={() => setAllocatingPayment(null)}
                className="rounded-lg p-1 text-zinc-500 hover:text-zinc-400"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {pendingInvoices.length === 0 ? (
              <div className="py-6 text-center text-xs text-zinc-500">
                This client has no open or overdue invoices to allocate to.
              </div>
            ) : (
              <form onSubmit={handleExecuteAllocation} className="mt-4 space-y-3.5">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Select Invoice *
                  </label>
                  <select
                    value={targetInvoiceId}
                    onChange={(e) => {
                      setTargetInvoiceId(e.target.value);
                      const inv = pendingInvoices.find((i) => i.id === e.target.value);
                      if (inv) {
                        setAllocAmount(Math.min(allocatingPayment.unallocated_amount, inv.balance_due));
                      }
                    }}
                    required
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  >
                    {pendingInvoices.map((inv) => (
                      <option key={inv.id} value={inv.id}>
                        {inv.invoice_number} (Outstanding: {formatINR(inv.balance_due)})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Amount to Allocate (₹) *
                  </label>
                  <input
                    type="number"
                    min="1"
                    max={allocatingPayment.unallocated_amount}
                    step="0.01"
                    value={allocAmount}
                    onChange={(e) => setAllocAmount(Number(e.target.value))}
                    required
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="flex items-center justify-end gap-2 border-t border-zinc-800 pt-3">
                  <button
                    type="button"
                    onClick={() => setAllocatingPayment(null)}
                    className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-950 transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition"
                  >
                    Confirm Allocation
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
