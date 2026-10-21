export function formatINR(val: number | string | undefined | null): string {
  if (val === undefined || val === null || isNaN(Number(val))) return "₹0.00";
  const num = Number(val);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }).format(num);
}

export function formatDate(dateStr: string | undefined | null): string {
  if (!dateStr) return "-";
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export const STATUS_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  draft: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200" },
  issued: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200" },
  partially_paid: { bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-200" },
  paid: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200" },
  overdue: { bg: "bg-rose-50", text: "text-rose-700", border: "border-rose-200" },
  cancelled: { bg: "bg-gray-100", text: "text-gray-600", border: "border-gray-200" },
};
