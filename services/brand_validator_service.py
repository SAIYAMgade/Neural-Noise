from __future__ import annotations

import re
from typing import Any


class BrandValidatorService:
    """Deterministic and rule-based validator enforcing brand guardrails and copy constraints."""

    DEFAULT_PROHIBITED_TERMS = [
        "guaranteed 100% roi",
        "100% guaranteed roi",
        "unlimited free forever",
        "no risk whatsoever",
        "zero effort needed",
        "cheat code",
        "miracle solution",
        "unbeatable guaranteed",
        "secret hack",
    ]

    @staticmethod
    def validate_variant(
        variant_data: dict[str, Any],
        brand_guidelines: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Validate variant copy against prohibited terms, required claims, and character bounds."""
        guidelines = brand_guidelines or {}
        prohibited = [
            term.lower().strip()
            for term in guidelines.get("prohibited_terms", BrandValidatorService.DEFAULT_PROHIBITED_TERMS)
            if term
        ]
        required_phrases = [
            phrase.lower().strip()
            for phrase in guidelines.get("required_phrases", [])
            if phrase
        ]

        headline_limit = int(guidelines.get("headline_max_chars", 85))
        subheading_limit = int(guidelines.get("subheading_max_chars", 220))
        cta_limit = int(guidelines.get("cta_max_chars", 35))

        issues: list[dict[str, str]] = []
        score = 100.0

        headline = str(variant_data.get("headline", "")).strip()
        subheading = str(variant_data.get("subheading", "")).strip()
        main_copy = str(variant_data.get("main_copy", "")).strip()
        cta_text = str(variant_data.get("cta_text", "")).strip()
        benefits = variant_data.get("benefits", []) or []

        all_text = f"{headline} {subheading} {main_copy} {' '.join(benefits)} {cta_text}".lower()

        # 1. Structural / Empty checks
        if not headline:
            issues.append({"type": "error", "field": "headline", "message": "Headline cannot be empty."})
            score -= 40.0
        if not cta_text:
            issues.append({"type": "error", "field": "cta_text", "message": "Call to action text cannot be empty."})
            score -= 30.0

        # 2. Length Bounds
        if len(headline) > headline_limit:
            issues.append({
                "type": "error",
                "field": "headline",
                "message": f"Headline exceeds maximum limit of {headline_limit} characters (current: {len(headline)}).",
            })
            score -= 15.0

        if subheading and len(subheading) > subheading_limit:
            issues.append({
                "type": "warning",
                "field": "subheading",
                "message": f"Subheading exceeds recommended {subheading_limit} characters (current: {len(subheading)}).",
            })
            score -= 10.0

        if len(cta_text) > cta_limit:
            issues.append({
                "type": "error",
                "field": "cta_text",
                "message": f"CTA text exceeds limit of {cta_limit} characters (current: {len(cta_text)}).",
            })
            score -= 15.0

        # 3. Prohibited Terms Check
        found_prohibited = []
        for term in prohibited:
            if term in all_text:
                found_prohibited.append(term)
                issues.append({
                    "type": "error",
                    "field": "content",
                    "message": f"Prohibited marketing term detected: '{term}'. Violates brand honesty guidelines.",
                })
                score -= 25.0

        # 4. Required Phrases Check
        missing_required = []
        for phrase in required_phrases:
            if phrase not in all_text:
                missing_required.append(phrase)
                issues.append({
                    "type": "warning",
                    "field": "content",
                    "message": f"Missing required brand phrase: '{phrase}'.",
                })
                score -= 10.0

        # 5. Benefits count
        if len(benefits) < 2:
            issues.append({
                "type": "warning",
                "field": "benefits",
                "message": "At least 2 clear value proposition benefits should be provided.",
            })
            score -= 5.0

        score = max(0.0, min(100.0, score))
        has_critical_errors = any(i["type"] == "error" for i in issues)

        return {
            "is_valid": not has_critical_errors,
            "brand_score": round(score, 1),
            "issues": issues,
            "prohibited_detected": found_prohibited,
            "missing_required": missing_required,
            "checked_at": variant_data.get("updated_at") or "",
        }
