import pytest
from services.brand_validator_service import BrandValidatorService


def test_brand_validator_detects_prohibited_terms():
    """Verify that marketing hype, miracle claims, and prohibited phrases are flagged."""
    bad_variant = {
        "headline": "Unlock 100% Guaranteed ROI With This Secret Hack",
        "subheading": "Get unlimited free forever access with no risk whatsoever.",
        "cta_text": "Claim Miracle Solution",
        "benefits": ["Benefit 1", "Benefit 2"],
    }

    report = BrandValidatorService.validate_variant(bad_variant)
    assert not report["is_valid"]
    assert report["brand_score"] < 60.0
    assert len(report["prohibited_detected"]) >= 2
    assert any("guaranteed" in p and "roi" in p for p in report["prohibited_detected"])


def test_brand_validator_enforces_character_limits():
    """Verify that oversized headlines and CTAs trigger validation errors."""
    oversized = {
        "headline": "This headline is intentionally written to be absurdly long, exceeding reasonable character bounds for web typography and landing page headers",
        "subheading": "A normal subheading",
        "cta_text": "This Call To Action Button Label Has Too Many Words To Click",
        "benefits": ["Benefit 1", "Benefit 2"],
    }

    report = BrandValidatorService.validate_variant(oversized, brand_guidelines={"headline_max_chars": 80, "cta_max_chars": 30})
    assert not report["is_valid"]
    error_fields = [i["field"] for i in report["issues"] if i["type"] == "error"]
    assert "headline" in error_fields
    assert "cta_text" in error_fields


def test_brand_validator_accepts_compliant_variant():
    """Verify that clean, compliant, and professional copy passes with high score."""
    good_variant = {
        "headline": "Autonomous Cloud Infrastructure Optimization for Enterprise",
        "subheading": "Reduce compute costs by 40% with automated right-sizing and zero downtime.",
        "main_copy": "Used by 450+ global engineering organizations with SOC-2 Type II certification.",
        "benefits": [
            "Continuous automated Kubernetes right-sizing",
            "Zero downtime guarantee with safety-bounded policies",
            "Single-click SOC-2 compliant audit reporting",
        ],
        "cta_text": "Book Enterprise Demo",
    }

    report = BrandValidatorService.validate_variant(good_variant)
    assert report["is_valid"]
    assert report["brand_score"] >= 90.0
    assert len(report["prohibited_detected"]) == 0
