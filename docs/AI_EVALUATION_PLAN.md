# IntentFlow AI — AI Evaluation Plan & Quality Guardrails

## 1. Executive Summary
IntentFlow AI implements automated, continuous evaluation suites to prevent model drift, hallucinated claims, formatting corruption, and calculation regressions across its dual application workflows:
1. **AI Website Experience Studio** (Landing page optimization, brand safety, structured JSON outputs)
2. **AI Financial Operations Studio** (Deterministic GST calculations, client ledger integrity, invoice compliance)

All evaluations are orchestrated through `services/evaluation_service.py`, persisted in PostgreSQL `evaluation_runs`, and exposed both programmatically and through the interactive **AI Evals** dashboard.

---

## 2. Evaluation Suites & Benchmark Test Cases

### Suite 1: Brand Safety & Prohibited Claims Guardrails
- **Objective**: Ensure that synthesized variants never contain unsubstantiated guarantees, deceptive ROI metrics, or non-compliant claims.
- **Test Case `brand_prohibited_terms_detected`**:
  - Injects a synthetic variant with the phrase `"100% guaranteed roi"`.
  - Asserts that `BrandValidatorService.validate_variant()` flags `is_valid: False`, detects `"100% guaranteed roi"`, and penalizes the brand score.
- **Pass Criterion**: Zero prohibited terms evade detection.

### Suite 2: Copy Length & Character Boundary Guardrails
- **Objective**: Guarantee that generated headlines, subheadings, and CTAs strictly adhere to layout constraints (e.g. mobile viewports, hero banners).
- **Test Case `character_length_boundaries`**:
  - Evaluates headlines $> 85$ characters and CTA text $> 35$ characters.
  - Asserts validation failure with explicit field-level warning messages.
- **Pass Criterion**: 100% boundary violations intercepted before publishing.

### Suite 3: Structured Output Schema Conformance
- **Objective**: Verify that LLM responses parse into strict Pydantic / LangGraph state models without missing fields or unexpected types.
- **Test Case `structured_json_schema_validity`**:
  - Validates presence of `headline`, `cta_text`, `subheading`, `main_copy`, and `benefits`.
- **Pass Criterion**: 100% schema compliance.

### Suite 4: Financial Operations Determinism (Shared Platform)
- **Objective**: Ensure that financial calculations, tax rate splits, and currency conversions retain mathematical determinism.
- **Test Case `gst_calculation_precision`**:
  - Validates Intra-state transaction (Karnataka $\to$ Karnataka) calculates CGST (9%) and SGST (9%).
  - Validates Inter-state transaction (Karnataka $\to$ Maharashtra) calculates IGST (18%).
  - Asserts exact rounding to 2 decimal places using Python `Decimal` objects.
- **Pass Criterion**: Zero penny rounding discrepancy across all invoice lines.

---

## 3. Evaluation Metrics & Thresholds

| Metric | Target | Failure Action |
| :--- | :--- | :--- |
| **Brand Guardrail Recall** | 100% | Block deployment; reject variant generation |
| **Character Bound Accuracy** | 100% | Flag for user review |
| **Structured Output Validity** | 100% | Trigger LangGraph retry with repair prompt |
| **Financial Math Precision** | 100% | Immediate transaction rollback |
| **Evaluation Suite Latency** | $< 500$ ms | Log performance warning |

---

## 4. Operationalization & CI/CD Integration
- **Automated Regression**: Executed on every test run via `pytest tests/unit/test_evaluation_service.py` and `tests/integration/test_vertical_workflow.py`.
- **Runtime Monitoring**: Every production variant generation triggers automatic evaluation against active project guidelines.
- **Human-in-the-Loop Override**: If an evaluation flags a borderline case, the variant enters `needs_review` status, requiring explicit human approval before any A/B experiment can be launched.
