"""
financial_calculator.py - Deterministic Financial and GST Engine for FinPilot AI.

Guarantees:
1. Strict Decimal arithmetic with no floating-point inaccuracies.
2. Standard quantization to 2 decimal places (ROUND_HALF_UP).
3. Indian GST Tax Rules:
   - Intra-state (Seller State == Buyer State): CGST + SGST (50% / 50% split).
   - Inter-state (Seller State != Buyer State): IGST (100%).
   - Export / Zero-rated: 0% tax.
4. Line Item Invariants:
   - quantity >= 0, unit_price >= 0, discount_pct between 0 and 100.
5. Syntactic GSTIN validation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

TWO_PLACES = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")

# Indian GST State Codes (2-digit)
GST_STATE_CODES: dict[str, str] = {
    "01": "Jammu & Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "26": "Dadra & Nagar Haveli and Daman & Diu",
    "27": "Maharashtra",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman & Nicobar Islands",
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "38": "Ladakh",
}

GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")


def quantize_money(amount: Decimal | float | int | str) -> Decimal:
    """Quantize to 2 decimal places using ROUND_HALF_UP."""
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    return amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def validate_gstin(gstin: str | None) -> tuple[bool, str]:
    """
    Validate Indian GSTIN syntactically.
    Returns (is_valid, state_code_or_reason).
    """
    if not gstin:
        return False, "GSTIN is empty"
    cleaned = gstin.strip().upper()
    if len(cleaned) != 15:
        return False, f"Invalid length ({len(cleaned)}). GSTIN must be exactly 15 characters."
    if not GSTIN_REGEX.match(cleaned):
        return False, "Invalid GSTIN format. Expected: 2-digit state code + 10-char PAN + 1 entity num + 'Z' + 1 checksum char."
    state_code = cleaned[:2]
    if state_code not in GST_STATE_CODES:
        return False, f"Unknown state code '{state_code}' in GSTIN."
    return True, state_code


@dataclass
class CalculatedLineItem:
    description: str
    hsn_sac_code: str | None
    quantity: Decimal
    unit_price: Decimal
    discount_pct: Decimal
    tax_rate_pct: Decimal
    subtotal_before_discount: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal


@dataclass
class InvoiceCalculationResult:
    subtotal: Decimal
    discount_total: Decimal
    taxable_amount: Decimal
    tax_type: Literal["intra_state", "inter_state", "export"]
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_tax: Decimal
    grand_total: Decimal
    line_items: list[CalculatedLineItem] = field(default_factory=list)


def calculate_invoice_totals(
    line_items: list[dict],
    seller_state_code: str = "27",
    buyer_state_code: str = "27",
    is_export: bool = False,
    extra_discount_total: Decimal = Decimal("0.00"),
) -> InvoiceCalculationResult:
    """
    Deterministic calculation of invoice line items, GST splits, and totals.
    """
    seller_state = str(seller_state_code).zfill(2)
    buyer_state = str(buyer_state_code).zfill(2)

    if is_export:
        tax_type: Literal["intra_state", "inter_state", "export"] = "export"
    elif seller_state == buyer_state:
        tax_type = "intra_state"
    else:
        tax_type = "inter_state"

    subtotal_accum = Decimal("0.00")
    discount_accum = quantize_money(extra_discount_total)
    taxable_accum = Decimal("0.00")
    cgst_accum = Decimal("0.00")
    sgst_accum = Decimal("0.00")
    igst_accum = Decimal("0.00")
    total_tax_accum = Decimal("0.00")

    calculated_items: list[CalculatedLineItem] = []

    for item in line_items:
        desc = str(item.get("description", "Service / Product"))
        hsn = item.get("hsn_sac_code")
        qty = Decimal(str(item.get("quantity", "1.0")))
        rate = Decimal(str(item.get("unit_price", "0.00")))
        disc_pct = Decimal(str(item.get("discount_pct", "0.00")))
        tax_pct = Decimal(str(item.get("tax_rate_pct", "18.00")))

        if qty < Decimal("0.0"):
            raise ValueError(f"Quantity cannot be negative: {qty}")
        if rate < Decimal("0.0"):
            raise ValueError(f"Unit price cannot be negative: {rate}")
        if disc_pct < Decimal("0.0") or disc_pct > Decimal("100.0"):
            raise ValueError(f"Discount percentage must be between 0 and 100: {disc_pct}")
        if tax_pct < Decimal("0.0"):
            raise ValueError(f"Tax rate cannot be negative: {tax_pct}")

        line_subtotal_raw = qty * rate
        line_discount = quantize_money(line_subtotal_raw * (disc_pct / Decimal("100.0")))
        taxable_val = quantize_money(line_subtotal_raw - line_discount)

        if is_export or tax_pct == Decimal("0.0"):
            cgst_line = Decimal("0.00")
            sgst_line = Decimal("0.00")
            igst_line = Decimal("0.00")
            tax_line = Decimal("0.00")
        elif tax_type == "intra_state":
            half_rate = tax_pct / Decimal("2.0")
            cgst_line = quantize_money(taxable_val * (half_rate / Decimal("100.0")))
            sgst_line = quantize_money(taxable_val * (half_rate / Decimal("100.0")))
            igst_line = Decimal("0.00")
            tax_line = cgst_line + sgst_line
        else: # inter_state
            cgst_line = Decimal("0.00")
            sgst_line = Decimal("0.00")
            igst_line = quantize_money(taxable_val * (tax_pct / Decimal("100.0")))
            tax_line = igst_line

        line_total = taxable_val + tax_line

        subtotal_accum += quantize_money(line_subtotal_raw)
        discount_accum += line_discount
        taxable_accum += taxable_val
        cgst_accum += cgst_line
        sgst_accum += sgst_line
        igst_accum += igst_line
        total_tax_accum += tax_line

        calculated_items.append(
            CalculatedLineItem(
                description=desc,
                hsn_sac_code=hsn,
                quantity=qty,
                unit_price=quantize_money(rate),
                discount_pct=disc_pct,
                tax_rate_pct=tax_pct,
                subtotal_before_discount=quantize_money(line_subtotal_raw),
                discount_amount=line_discount,
                taxable_amount=taxable_val,
                tax_amount=tax_line,
                line_total=line_total,
            )
        )

    grand_total = taxable_accum + total_tax_accum

    return InvoiceCalculationResult(
        subtotal=subtotal_accum,
        discount_total=discount_accum,
        taxable_amount=taxable_accum,
        tax_type=tax_type,
        cgst_amount=cgst_accum,
        sgst_amount=sgst_accum,
        igst_amount=igst_accum,
        total_tax=total_tax_accum,
        grand_total=grand_total,
        line_items=calculated_items,
    )


def compute_payment_allocation(
    payment_amount: Decimal,
    current_amount_paid: Decimal,
    grand_total: Decimal,
) -> tuple[Decimal, Decimal, Decimal, str]:
    """
    Computes deterministic allocation of payment funds to an invoice.
    Returns:
      (allocated_to_invoice, new_amount_paid, new_amount_due, new_invoice_status)
    """
    p_amt = quantize_money(payment_amount)
    curr_paid = quantize_money(current_amount_paid)
    total = quantize_money(grand_total)
    
    current_due = quantize_money(total - curr_paid)
    if current_due <= Decimal("0.00"):
        return Decimal("0.00"), curr_paid, Decimal("0.00"), "paid"

    allocated = min(p_amt, current_due)
    new_paid = curr_paid + allocated
    new_due = max(Decimal("0.00"), total - new_paid)

    if new_due == Decimal("0.00"):
        new_status = "paid"
    else:
        new_status = "partially_paid"

    return allocated, new_paid, new_due, new_status
