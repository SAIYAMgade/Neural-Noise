from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import EvaluationRun
from services.brand_validator_service import BrandValidatorService
from services.financial_calculator import calculate_invoice_totals, validate_gstin


class EvaluationService:
    """Automated evaluation test runner measuring agent quality, guardrail enforcement, and deterministic correctness."""

    @staticmethod
    async def run_evaluation_suite(
        session: AsyncSession,
        suite_name: str = "comprehensive_platform_suite",
    ) -> EvaluationRun:
        """Run real evaluation test cases across brand guardrails, schema validity, and financial precision."""
        t_start = time.time()
        cases_results: list[dict[str, Any]] = []

        # -------------------------------------------------------------
        # 1. Brand Guardrails & Honesty Tests (4 cases)
        # -------------------------------------------------------------
        # Case 1: Prohibited term detection
        c1_input = {"headline": "Get 100% Guaranteed ROI Immediately", "cta_text": "Click Here", "benefits": ["B1", "B2"]}
        c1_res = BrandValidatorService.validate_variant(c1_input)
        c1_pass = not c1_res["is_valid"] and any("roi" in p and "guaranteed" in p for p in c1_res["prohibited_detected"])
        cases_results.append({
            "case_id": "BG-01",
            "suite": "brand_guardrails",
            "name": "Prohibited marketing claim detection ('guaranteed 100% ROI')",
            "passed": c1_pass,
            "details": f"Flagged issues: {len(c1_res['issues'])}, Brand Score: {c1_res['brand_score']}",
        })

        # Case 2: Excessive headline length
        c2_input = {
            "headline": "A" * 120,  # Exceeds default limit of 85
            "cta_text": "Get Started",
            "benefits": ["Benefit 1", "Benefit 2"],
        }
        c2_res = BrandValidatorService.validate_variant(c2_input)
        c2_pass = any("headline exceeds" in i["message"].lower() for i in c2_res["issues"])
        cases_results.append({
            "case_id": "BG-02",
            "suite": "brand_guardrails",
            "name": "Headline character limit guardrail enforcement",
            "passed": c2_pass,
            "details": f"Detected character overflow: {len(c2_input['headline'])} chars",
        })

        # Case 3: Empty CTA rejection
        c3_input = {"headline": "Autonomous Cloud Optimization", "cta_text": "", "benefits": ["Fast", "Secure"]}
        c3_res = BrandValidatorService.validate_variant(c3_input)
        c3_pass = any("cta" in i["field"].lower() or "call to action" in i["message"].lower() for i in c3_res["issues"])
        cases_results.append({
            "case_id": "BG-03",
            "suite": "brand_guardrails",
            "name": "Empty Call-to-Action rejection",
            "passed": c3_pass,
            "details": "Caught empty CTA field constraint",
        })

        # Case 4: Compliant valid copy acceptance
        c4_input = {
            "headline": "Enterprise-Grade Autonomous Infrastructure Optimization",
            "subheading": "Guaranteed 99.99% uptime with native SOC-2 Type II certified cloud optimization.",
            "cta_text": "Request Enterprise Access",
            "benefits": ["Zero application downtime", "SOC-2 Type II compliant audit reports"],
        }
        c4_res = BrandValidatorService.validate_variant(c4_input)
        c4_pass = c4_res["is_valid"] and c4_res["brand_score"] >= 90.0
        cases_results.append({
            "case_id": "BG-04",
            "suite": "brand_guardrails",
            "name": "Compliant enterprise copy acceptance & scoring",
            "passed": c4_pass,
            "details": f"Score: {c4_res['brand_score']}/100, Valid: {c4_res['is_valid']}",
        })

        # -------------------------------------------------------------
        # 2. Financial Correctness & Indian GST Tests (3 cases)
        # -------------------------------------------------------------
        # Case 5: Intra-state GST (CGST 9% + SGST 9%)
        intra_calc = calculate_invoice_totals(
            seller_state_code="27",
            buyer_state_code="27",
            line_items=[{"quantity": 1, "unit_price": Decimal("50000.00"), "gst_rate": Decimal("18.00"), "discount_rate": Decimal("0.00")}],
        )
        c5_pass = (
            intra_calc.tax_type == "intra_state"
            and intra_calc.cgst_amount == Decimal("4500.00")
            and intra_calc.sgst_amount == Decimal("4500.00")
            and intra_calc.grand_total == Decimal("59000.00")
        )
        cases_results.append({
            "case_id": "FC-01",
            "suite": "financial_correctness",
            "name": "Deterministic Intra-State GST tax split (CGST 50% + SGST 50%)",
            "passed": c5_pass,
            "details": f"Grand Total: INR {intra_calc.grand_total}, CGST: INR {intra_calc.cgst_amount}, SGST: INR {intra_calc.sgst_amount}",
        })

        # Case 6: Inter-state GST (IGST 18%)
        inter_calc = calculate_invoice_totals(
            seller_state_code="27",
            buyer_state_code="29",
            line_items=[{"quantity": 1, "unit_price": Decimal("100000.00"), "gst_rate": Decimal("18.00"), "discount_rate": Decimal("0.00")}],
        )
        c6_pass = (
            inter_calc.tax_type == "inter_state"
            and inter_calc.igst_amount == Decimal("18000.00")
            and inter_calc.grand_total == Decimal("118000.00")
        )
        cases_results.append({
            "case_id": "FC-02",
            "suite": "financial_correctness",
            "name": "Deterministic Inter-State IGST routing (100% IGST)",
            "passed": c6_pass,
            "details": f"Grand Total: INR {inter_calc.grand_total}, IGST: INR {inter_calc.igst_amount}",
        })

        # Case 7: GSTIN Syntactic Validation
        v_valid_ok, _ = validate_gstin("27AABCU9603R1ZM")
        v_invalid_ok, _ = validate_gstin("INVALID_GSTIN")
        c7_pass = v_valid_ok and not v_invalid_ok
        cases_results.append({
            "case_id": "FC-03",
            "suite": "financial_correctness",
            "name": "15-character statutory GSTIN syntax verification",
            "passed": c7_pass,
            "details": f"Valid test passed: {v_valid_ok}, Invalid test correctly rejected: {not v_invalid_ok}",
        })

        # -------------------------------------------------------------
        # Aggregate Metrics & Record Run
        # -------------------------------------------------------------
        total_cases = len(cases_results)
        passed_cases = sum(1 for c in cases_results if c["passed"])
        failed_cases = total_cases - passed_cases
        accuracy_pct = round((passed_cases / total_cases) * 100, 1)
        total_latency_ms = int((time.time() - t_start) * 1000)

        eval_run = EvaluationRun(
            suite_name=suite_name,
            model_name="deterministic_evaluator_v1",
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            metrics={
                "accuracy_pct": accuracy_pct,
                "total_latency_ms": total_latency_ms,
                "brand_guardrails_passed": sum(1 for c in cases_results if c["suite"] == "brand_guardrails" and c["passed"]),
                "financial_correctness_passed": sum(1 for c in cases_results if c["suite"] == "financial_correctness" and c["passed"]),
            },
            details=cases_results,
            created_at=datetime.now(timezone.utc),
        )
        session.add(eval_run)
        await session.commit()
        return eval_run

    @staticmethod
    async def get_evaluation_history(
        session: AsyncSession,
        limit: int = 10,
    ) -> list[EvaluationRun]:
        """Fetch past evaluation runs."""
        stmt = select(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(limit)
        return list((await session.execute(stmt)).scalars().all())
