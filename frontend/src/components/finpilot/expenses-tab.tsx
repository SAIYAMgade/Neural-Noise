"use client";

import React, { useState, useEffect } from "react";
import {
  CreditCard,
  Plus,
  RefreshCw,
  X,
  CheckCircle2,
  AlertCircle,
  Tag,
  Receipt,
  ArrowUpRight,
} from "lucide-react";
import {
  getExpenses,
  createExpense,
  type ExpenseData,
} from "@/lib/api";
import { formatINR, formatDate } from "./utils";

const EXPENSE_CATEGORIES = [
  "software_expense",
  "contractor_expense",
  "office_rent",
  "marketing_expense",
  "salary_expense",
  "professional_services",
  "travel_expense",
  "hardware_equipment",
  "utilities",
  "other",
];

const PAYMENT_METHODS = ["UPI", "Credit Card", "Net Banking", "Debit Card", "Cash", "Cheque"];

export function ExpensesTab() {
  const [expenses, setExpenses] = useState<ExpenseData[]>([]);
  const [loading, setLoading] = useState(true);

  // Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newExpense, setNewExpense] = useState({
    category: "software_expense",
    vendor: "",
    amount: 1500,
    payment_method: "Credit Card",
    tax_amount: 0,
    gstin: "",
    is_tax_deductible: true,
    notes: "",
  });
  const [creating, setCreating] = useState(false);

  const loadExpenses = async () => {
    try {
      const data = await getExpenses();
      setExpenses(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load expenses:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExpenses();
  }, []);

  const handleCreateExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newExpense.amount || Number(newExpense.amount) <= 0) {
      alert("Please enter a valid expense amount.");
      return;
    }

    setCreating(true);
    try {
      await createExpense({
        ...newExpense,
        amount: Number(newExpense.amount),
        tax_amount: Number(newExpense.tax_amount) || 0,
        expense_date: new Date().toISOString().split("T")[0],
      });
      setIsModalOpen(false);
      setNewExpense({
        category: "software_expense",
        vendor: "",
        amount: 1500,
        payment_method: "Credit Card",
        tax_amount: 0,
        gstin: "",
        is_tax_deductible: true,
        notes: "",
      });
      await loadExpenses();
    } catch (err: any) {
      alert(`Failed to record expense: ${err.message || "Error"}`);
    } finally {
      setCreating(false);
    }
  };

  const totalExpenseAmount = expenses.reduce((sum, e) => sum + (Number(e.amount) || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Operating Expenses &amp; Outflows</h2>
          <p className="text-xs text-zinc-400">
            Track business deductions, SaaS subscriptions, contractor fees, and vendor GST input credits.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition"
        >
          <Plus className="h-4 w-4" />
          Record Expense
        </button>
      </div>

      {/* Summary Banner */}
      <div className="flex items-center justify-between rounded-xl border border-zinc-800 bg-zinc-900 p-4 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-rose-50 p-2.5 text-rose-600">
            <ArrowUpRight className="h-5 w-5" />
          </div>
          <div>
            <span className="text-xs font-medium text-zinc-400">Total Recorded Outflows</span>
            <p className="text-lg font-bold text-white">{formatINR(totalExpenseAmount)}</p>
          </div>
        </div>
        <span className="rounded-full bg-zinc-800 px-3 py-1 text-xs font-semibold text-zinc-400">
          {expenses.length} Expense Item(s)
        </span>
      </div>

      {/* Expenses Table */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 shadow-sm overflow-hidden">
        {loading ? (
          <div className="py-12 text-center text-xs text-zinc-500">
            <RefreshCw className="h-5 w-5 animate-spin mx-auto mb-2 text-indigo-600" />
            Loading expenses...
          </div>
        ) : expenses.length === 0 ? (
          <div className="py-12 text-center text-xs text-zinc-500">
            No expenses recorded yet. Click &ldquo;Record Expense&rdquo; to add your operational costs.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-950/70 text-zinc-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Vendor</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Method</th>
                  <th className="py-3 px-4">Deductible</th>
                  <th className="py-3 px-4">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {expenses.map((e) => (
                  <tr key={e.id} className="hover:bg-zinc-950/50 transition">
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center rounded-md bg-zinc-800 px-2 py-0.5 text-[11px] font-medium text-zinc-200 capitalize">
                        {(e.category || "Expense").replace("_", " ")}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-zinc-200">
                      {e.vendor || (e as any).merchant || "-"}
                    </td>
                    <td className="py-3 px-4 font-bold text-white">
                      {formatINR(e.amount)}
                    </td>
                    <td className="py-3 px-4 text-zinc-400">
                      {formatDate(e.expense_date || (e as any).date)}
                    </td>
                    <td className="py-3 px-4 text-zinc-400">
                      {e.payment_method || "-"}
                    </td>
                    <td className="py-3 px-4">
                      {e.is_tax_deductible ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                          <CheckCircle2 className="h-3 w-3" /> Yes (ITR)
                        </span>
                      ) : (
                        <span className="text-[10px] text-zinc-500">No</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-zinc-400 italic max-w-xs truncate">
                      {e.notes || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Record Expense Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-lg rounded-2xl bg-zinc-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">Record Operating Expense</h3>
                <p className="text-xs text-zinc-400">
                  Track vendor payments, tax deductions, and input credits.
                </p>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="rounded-lg p-1 text-zinc-500 hover:text-zinc-400"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateExpense} className="mt-4 space-y-3.5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Expense Category *
                  </label>
                  <select
                    value={newExpense.category}
                    onChange={(e) => setNewExpense({ ...newExpense, category: e.target.value })}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 capitalize focus:border-indigo-500 focus:outline-none"
                  >
                    {EXPENSE_CATEGORIES.map((c) => (
                      <option key={c} value={c}>
                        {c.replace("_", " ")}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Vendor / Merchant Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. AWS, GitHub, Figma, Co-working"
                    value={newExpense.vendor}
                    onChange={(e) => setNewExpense({ ...newExpense, vendor: e.target.value })}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Amount (₹) *
                  </label>
                  <input
                    type="number"
                    min="1"
                    step="0.01"
                    value={newExpense.amount}
                    onChange={(e) => setNewExpense({ ...newExpense, amount: Number(e.target.value) })}
                    required
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Payment Method
                  </label>
                  <select
                    value={newExpense.payment_method}
                    onChange={(e) => setNewExpense({ ...newExpense, payment_method: e.target.value })}
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

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    GST Amount Included (₹)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={newExpense.tax_amount}
                    onChange={(e) => setNewExpense({ ...newExpense, tax_amount: Number(e.target.value) })}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-300 mb-1">
                    Vendor GSTIN (Optional)
                  </label>
                  <input
                    type="text"
                    maxLength={15}
                    placeholder="27AABCU9603R1ZM"
                    value={newExpense.gstin}
                    onChange={(e) => setNewExpense({ ...newExpense, gstin: e.target.value.toUpperCase() })}
                    className="w-full rounded-xl border border-zinc-800 p-2 text-xs font-mono uppercase text-zinc-200 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="deductible"
                  checked={newExpense.is_tax_deductible}
                  onChange={(e) => setNewExpense({ ...newExpense, is_tax_deductible: e.target.checked })}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="deductible" className="text-xs text-zinc-300 cursor-pointer">
                  Eligible for Business Expense Deduction under Indian Income Tax Act
                </label>
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">
                  Description / Purpose
                </label>
                <input
                  type="text"
                  placeholder="e.g. Monthly cloud server infrastructure subscription"
                  value={newExpense.notes}
                  onChange={(e) => setNewExpense({ ...newExpense, notes: e.target.value })}
                  className="w-full rounded-xl border border-zinc-800 p-2 text-xs text-zinc-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

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
                  {creating ? "Saving..." : "Record Expense"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
