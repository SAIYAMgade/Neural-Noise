"use client";

import React, { useState, useEffect } from "react";
import {
  Users,
  Plus,
  Search,
  RefreshCw,
  X,
  FileText,
  CreditCard,
  AlertCircle,
  ExternalLink,
  CheckCircle2,
  Building,
} from "lucide-react";
import {
  getClients,
  getClientLedger,
  createClient,
  type ClientData,
  type ClientLedgerData,
} from "@/lib/api";
import { formatINR, formatDate, STATUS_STYLES } from "./utils";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const GST_STATE_NAMES: Record<string, string> = {
  "01": "Jammu & Kashmir",
  "02": "Himachal Pradesh",
  "03": "Punjab",
  "06": "Haryana",
  "07": "Delhi",
  "08": "Rajasthan",
  "09": "Uttar Pradesh",
  "19": "West Bengal",
  "24": "Gujarat",
  "27": "Maharashtra",
  "29": "Karnataka",
  "32": "Kerala",
  "33": "Tamil Nadu",
  "36": "Telangana",
  "37": "Andhra Pradesh",
};

export function ClientsTab() {
  const [clients, setClients] = useState<ClientData[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  // Add Client Modal
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newClient, setNewClient] = useState({
    name: "",
    legal_name: "",
    gstin: "",
    state_code: "27",
    email: "",
    phone: "",
    address: "",
    payment_terms_days: 15,
  });
  const [creating, setCreating] = useState(false);

  // Ledger Drawer/Modal
  const [activeLedger, setActiveLedger] = useState<ClientLedgerData | null>(null);
  const [loadingLedger, setLoadingLedger] = useState(false);

  const loadClients = async () => {
    try {
      const data = await getClients(searchQuery);
      setClients(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load clients:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadClients();
  }, [searchQuery]);

  const handleGstinChange = (gstinVal: string) => {
    const cleaned = gstinVal.toUpperCase().trim();
    let stateCode = newClient.state_code;
    if (cleaned.length >= 2 && /^\d{2}/.test(cleaned)) {
      stateCode = cleaned.slice(0, 2);
    }
    setNewClient((prev) => ({
      ...prev,
      gstin: cleaned,
      state_code: stateCode,
    }));
  };

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newClient.name.trim()) {
      alert("Client name is required.");
      return;
    }

    if (newClient.gstin && newClient.gstin.length !== 15) {
      alert("Indian GSTIN must be exactly 15 characters (e.g. 27AABCU9603R1ZM).");
      return;
    }

    setCreating(true);
    try {
      await createClient({
        ...newClient,
        payment_terms_days: Number(newClient.payment_terms_days) || 15,
      });
      setIsAddModalOpen(false);
      setNewClient({
        name: "",
        legal_name: "",
        gstin: "",
        state_code: "27",
        email: "",
        phone: "",
        address: "",
        payment_terms_days: 15,
      });
      await loadClients();
    } catch (err: any) {
      alert(`Failed to add client: ${err.message || "Error"}`);
    } finally {
      setCreating(false);
    }
  };

  const handleOpenLedger = async (client: ClientData) => {
    setLoadingLedger(true);
    try {
      const ledger = await getClientLedger(client.id);
      setActiveLedger(ledger);
    } catch (err: any) {
      alert(`Could not fetch ledger: ${err.message || "Error"}`);
    } finally {
      setLoadingLedger(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Client Directory &amp; Ledgers</h2>
          <p className="text-xs text-zinc-400">
            Indian customer accounts, GSTIN verification, place of supply detection, and lifetime receivables.
          </p>
        </div>

        <button
          onClick={() => setIsAddModalOpen(true)}
          className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition"
        >
          <Plus className="h-4 w-4" />
          Add Client
        </button>
      </div>

      {/* Search Input */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-3 shadow-xs">
        <div className="flex items-center gap-2">
          <Search className="h-4 w-4 text-zinc-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search clients by trade name, legal entity, or GSTIN..."
            className="w-full text-xs text-zinc-200 placeholder-slate-400 focus:outline-none"
          />
        </div>
      </div>

      {/* Clients Table */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 shadow-sm overflow-hidden">
        {loading ? (
          <div className="py-12 text-center text-xs text-zinc-500">
            <RefreshCw className="h-5 w-5 animate-spin mx-auto mb-2 text-indigo-600" />
            Loading clients...
          </div>
        ) : clients.length === 0 ? (
          <div className="py-12 text-center text-xs text-zinc-500">
            No clients registered yet. Click &ldquo;Add Client&rdquo; to create your first client account.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-950/70 text-zinc-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Client Name</th>
                  <th className="py-3 px-4">GSTIN &amp; State</th>
                  <th className="py-3 px-4">Contact</th>
                  <th className="py-3 px-4">Payment Terms</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {clients.map((c) => {
                  const stateName = GST_STATE_NAMES[c.state_code || ""] || `State ${c.state_code || "-"}`;
                  return (
                    <tr key={c.id} className="hover:bg-zinc-950/50 transition">
                      <td className="py-3 px-4">
                        <div className="font-bold text-white">{c.name}</div>
                        {c.legal_name && (
                          <div className="text-[11px] text-zinc-500">{c.legal_name}</div>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        {c.gstin ? (
                          <div>
                            <span className="font-mono font-semibold text-zinc-200">{c.gstin}</span>
                            <div className="text-[10px] text-indigo-600 font-medium">
                              Code {c.state_code} &middot; {stateName}
                            </div>
                          </div>
                        ) : (
                          <span className="text-zinc-500 italic">Unregistered / Consumer</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-[11px] text-zinc-400">
                        <div>{c.email || "-"}</div>
                        <div className="text-zinc-500">{c.phone || ""}</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center rounded-md bg-zinc-800 px-2 py-0.5 text-[10px] font-semibold text-zinc-300">
                          Net {c.payment_terms_days} Days
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleOpenLedger(c)}
                          className="inline-flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs font-semibold text-zinc-300 hover:bg-zinc-950 transition shadow-xs"
                        >
                          <FileText className="h-3.5 w-3.5 text-indigo-600" />
                          View Ledger
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Client Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-lg rounded-2xl bg-zinc-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">Add New Client</h3>
                <p className="text-xs text-zinc-400">
                  Register a customer with Indian GSTIN verification and place of supply.
                </p>
              </div>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="rounded-lg p-1 text-zinc-500 hover:text-zinc-400"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateClient} className="mt-4 space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">
                  Business / Trade Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g. Acme Technologies"
                  value={newClient.name}
                  onChange={(e) => setNewClient({ ...newClient, name: e.target.value })}
                  required
                  className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">
                  Legal Entity Name (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Acme Technologies Private Limited"
                  value={newClient.legal_name}
                  onChange={(e) => setNewClient({ ...newClient, legal_name: e.target.value })}
                  className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    GSTIN (15 Chars)
                  </label>
                  <input
                    type="text"
                    maxLength={15}
                    placeholder="27AABCU9603R1ZM"
                    value={newClient.gstin}
                    onChange={(e) => handleGstinChange(e.target.value)}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs font-mono uppercase text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    State Code (2 Digits)
                  </label>
                  <input
                    type="text"
                    maxLength={2}
                    placeholder="27"
                    value={newClient.state_code}
                    onChange={(e) => setNewClient({ ...newClient, state_code: e.target.value })}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs font-mono text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Billing Email
                  </label>
                  <input
                    type="email"
                    placeholder="billing@acme.in"
                    value={newClient.email}
                    onChange={(e) => setNewClient({ ...newClient, email: e.target.value })}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Payment Terms (Days)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="180"
                    value={newClient.payment_terms_days}
                    onChange={(e) => setNewClient({ ...newClient, payment_terms_days: Number(e.target.value) })}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">
                  Billing Address
                </label>
                <input
                  type="text"
                  placeholder="e.g. 402 Business Park, Bandra Kurla Complex, Mumbai, MH"
                  value={newClient.address}
                  onChange={(e) => setNewClient({ ...newClient, address: e.target.value })}
                  className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 border-t border-zinc-800 pt-3">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="rounded-xl border border-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-400 hover:bg-zinc-950 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition disabled:opacity-50"
                >
                  {creating ? "Adding..." : "Add Client"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Client Ledger Modal */}
      {activeLedger && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-2xl rounded-2xl bg-zinc-900 p-6 shadow-2xl max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">
                  {activeLedger.client_name} &middot; Financial Ledger
                </h3>
                <p className="text-xs text-zinc-400">
                  Historical invoicing, settlements, and outstanding balance summary.
                </p>
              </div>
              <button
                onClick={() => setActiveLedger(null)}
                className="rounded-lg p-1 text-zinc-500 hover:text-zinc-400"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Ledger KPI Cards */}
            <div className="grid grid-cols-3 gap-3 my-4">
              <div className="rounded-xl bg-zinc-950 p-3 border border-zinc-800">
                <span className="text-[11px] text-zinc-400">Total Invoiced</span>
                <p className="text-base font-bold text-white">{formatINR(activeLedger.total_invoiced)}</p>
                <p className="text-[10px] text-zinc-500">{activeLedger.invoices_count} invoice(s)</p>
              </div>
              <div className="rounded-xl bg-emerald-50 p-3 border border-emerald-100">
                <span className="text-[11px] text-emerald-700">Total Paid</span>
                <p className="text-base font-bold text-emerald-700">{formatINR(activeLedger.total_paid)}</p>
                <p className="text-[10px] text-emerald-600">Settled receipts</p>
              </div>
              <div className="rounded-xl bg-amber-50 p-3 border border-amber-100">
                <span className="text-[11px] text-amber-700">Total Outstanding</span>
                <p className="text-base font-bold text-amber-700">{formatINR(activeLedger.total_due)}</p>
                <p className="text-[10px] text-rose-600 font-semibold">{activeLedger.overdue_count} overdue</p>
              </div>
            </div>

            {/* Invoices List for Client */}
            <h4 className="text-xs font-bold text-zinc-200 uppercase tracking-wider mb-2">
              Invoices History
            </h4>

            {activeLedger.invoices.length === 0 ? (
              <p className="py-6 text-center text-xs text-zinc-500">
                No invoices found for this client.
              </p>
            ) : (
              <div className="divide-y divide-zinc-800 border border-zinc-800 rounded-xl overflow-hidden">
                {activeLedger.invoices.map((inv) => {
                  const style = STATUS_STYLES[inv.status] || STATUS_STYLES.draft;
                  return (
                    <div
                      key={inv.id}
                      className="flex items-center justify-between p-3 hover:bg-zinc-950/50 text-xs transition"
                    >
                      <div>
                        <span className="font-mono font-bold text-white">{inv.invoice_number}</span>
                        <div className="text-[11px] text-zinc-500">
                          Due: {formatDate(inv.due_date)}
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="font-bold text-white">{formatINR(inv.total_amount)}</div>
                        <div className="text-[11px] text-indigo-600">Balance: {formatINR(inv.balance_due)}</div>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className={`rounded-full border px-2 py-0.5 text-[10px] font-bold capitalize ${style.bg} ${style.text} ${style.border}`}>
                          {inv.status}
                        </span>
                        <a
                          href={`${API_BASE}/api/v1/invoices/${inv.id}/pdf`}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-lg border border-zinc-800 p-1 text-zinc-400 hover:bg-zinc-800 transition"
                          title="Download PDF"
                        >
                          <FileText className="h-3.5 w-3.5" />
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
