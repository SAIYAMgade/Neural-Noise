"""
Unit tests for deterministic financial calculations and GST rules in FinPilot AI.
"""

from decimal import Decimal
import pytest

from services.financial_calculator import (
    calculate_invoice_totals,
    compute_payment_allocation,
    quantize_money,
    validate_gstin,
)


def test_quantize_money():
    assert quantize_money(10.555) == Decimal("10.56")
    assert quantize_money("100.2") == Decimal("100.20")
    assert quantize_money(Decimal("50")) == Decimal("50.00")


def test_gstin_validation():
    # Valid Maharashtra GSTIN (state code 27)
    valid, state = validate_gstin("27AAPFU0939F1ZV")
    assert valid is True
    assert state == "27"

    # Valid Karnataka GSTIN (state code 29)
    valid, state = validate_gstin("29AABCU9603R1ZJ")
    assert valid is True
    assert state == "29"

    # Invalid length
    valid, reason = validate_gstin("27AAPFU0939F1Z")
    assert valid is False
    assert "Invalid length" in reason

    # Invalid state code
    valid, reason = validate_gstin("99AAPFU0939F1ZV")
    assert valid is False
    assert "Unknown state code" in reason


def test_intra_state_gst_calculation():
    # Intra-state: Seller (27 - Maharashtra) and Buyer (27 - Maharashtra)
    # Line item: ₹50,000 at 18% GST
    # Expected: CGST = 9% (₹4,500), SGST = 9% (₹4,500), IGST = ₹0.00, Grand Total = ₹59,000.00
    line_items = [
        {
            "description": "Software Architecture Consulting",
            "quantity": 1,
            "unit_price": 50000.00,
            "discount_pct": 0,
            "tax_rate_pct": 18,
        }
    ]
    res = calculate_invoice_totals(
        line_items=line_items,
        seller_state_code="27",
        buyer_state_code="27",
    )
    assert res.tax_type == "intra_state"
    assert res.subtotal == Decimal("50000.00")
    assert res.taxable_amount == Decimal("50000.00")
    assert res.cgst_amount == Decimal("4500.00")
    assert res.sgst_amount == Decimal("4500.00")
    assert res.igst_amount == Decimal("0.00")
    assert res.total_tax == Decimal("9000.00")
    assert res.grand_total == Decimal("59000.00")


def test_inter_state_gst_calculation():
    # Inter-state: Seller (27 - Maharashtra) and Buyer (29 - Karnataka)
    # Line item: ₹1,00,000 at 18% GST
    # Expected: CGST = ₹0.00, SGST = ₹0.00, IGST = 18% (₹18,000.00), Grand Total = ₹1,18,000.00
    line_items = [
        {
            "description": "Full-Stack AI Agent Development",
            "quantity": 1,
            "unit_price": 100000.00,
            "discount_pct": 0,
            "tax_rate_pct": 18,
        }
    ]
    res = calculate_invoice_totals(
        line_items=line_items,
        seller_state_code="27",
        buyer_state_code="29",
    )
    assert res.tax_type == "inter_state"
    assert res.subtotal == Decimal("100000.00")
    assert res.cgst_amount == Decimal("0.00")
    assert res.sgst_amount == Decimal("0.00")
    assert res.igst_amount == Decimal("18000.00")
    assert res.total_tax == Decimal("18000.00")
    assert res.grand_total == Decimal("118000.00")


def test_line_discount_calculation():
    # Line item with 10% discount
    # ₹20,000 - 10% = ₹18,000 taxable. 18% IGST = ₹3,240. Grand total = ₹21,240
    line_items = [
        {
            "description": "Cloud DevOps Setup",
            "quantity": 1,
            "unit_price": 20000.00,
            "discount_pct": 10,
            "tax_rate_pct": 18,
        }
    ]
    res = calculate_invoice_totals(
        line_items=line_items,
        seller_state_code="27",
        buyer_state_code="07",  # Delhi (Inter-state)
    )
    assert res.subtotal == Decimal("20000.00")
    assert res.discount_total == Decimal("2000.00")
    assert res.taxable_amount == Decimal("18000.00")
    assert res.igst_amount == Decimal("3240.00")
    assert res.grand_total == Decimal("21240.00")


def test_payment_allocation_logic():
    # Grand total ₹59,000, 0 paid previously.
    # Partial payment of ₹30,000
    allocated, new_paid, new_due, status = compute_payment_allocation(
        payment_amount=Decimal("30000.00"),
        current_amount_paid=Decimal("0.00"),
        grand_total=Decimal("59000.00"),
    )
    assert allocated == Decimal("30000.00")
    assert new_paid == Decimal("30000.00")
    assert new_due == Decimal("29000.00")
    assert status == "partially_paid"

    # Second payment of ₹30,000 (only ₹29,000 needed to complete)
    allocated2, new_paid2, new_due2, status2 = compute_payment_allocation(
        payment_amount=Decimal("30000.00"),
        current_amount_paid=new_paid,
        grand_total=Decimal("59000.00"),
    )
    assert allocated2 == Decimal("29000.00")
    assert new_paid2 == Decimal("59000.00")
    assert new_due2 == Decimal("0.00")
    assert status2 == "paid"
