# IntentFlow AI — Test Strategy & Quality Assurance Architecture

## 1. Quality Assurance Philosophy
IntentFlow AI is an enterprise AI agent platform where errors in LLM outputs, statistical calculations, or financial ledgers carry direct business risk. 

Our test strategy is grounded in three immutable axioms:
1. **Never substitute mock responses or hardcoded scores for real implementations.**
2. **Every non-trivial agent branch, statistical formula, and financial transaction must possess automated regression tests.**
3. **No untested code is committed to production.**

---

## 2. Test Pyramid & Execution Coverage

```
               ▲
              / \
             /E2E\     Next.js Production Build (0 TS Errors)
            /-----\
           / Integ \   Full Vertical Agent & API Lifecycles (PostgreSQL 18)
          /---------\
         /   Unit    \ SSRF Filter, Brand Guardrails, Z-Test Stats, GST Decimal Math
        /-------------\
```

### 2.1 Unit Test Battery (`tests/unit/`)

| Test Suite | File | Key Assertions |
| :--- | :--- | :--- |
| **SSRF & Page Ingestion** | `test_page_ingestion_and_ssrf.py` | - Rejects `127.0.0.1`, `10.0.0.1`, `192.168.1.1`, and `169.254.169.254`<br>- Enforces 2MB maximum payload buffer<br>- DOM parser extracts title, headings, primary CTA, and trust badges |
| **Brand Guardrails** | `test_brand_validator.py` | - Intercepts `"100% guaranteed roi"` and deceptive claims<br>- Flags headlines exceeding 85 chars & CTAs exceeding 35 chars<br>- Computes deterministic brand compliance score |
| **Experiment Statistics** | `test_experiment_statistics.py` | - Verifies deterministic MD5 visitor hashing is repeatable and sticky<br>- Asserts two-proportion pooled z-score matches theoretical values<br>- Computes normal CDF p-values and 95% confidence intervals<br>- Triggers sample size warnings when $n < 30$ |
| **Financial Calculations** | `test_financial_calculations.py` | - Intra-state GST calculates 9% CGST + 9% SGST<br>- Inter-state GST calculates 18% IGST<br>- Zero floating-point drift using Python `Decimal`<br>- Immutable ledger credit/debit running balances |

### 2.2 Integration Test Battery (`tests/integration/`)

| Test Suite | File | Key Assertions |
| :--- | :--- | :--- |
| **LangGraph Agent Workflow** | `test_website_optimizer_workflow.py` | Executes the 6-step LangGraph StateGraph (`validate_request` $\to$ `ingest_page_context` $\to$ `analyze_audience_intent` $\to$ `generate_variants` $\to$ `validate_guardrails` $\to$ `prepare_approval_checkpoint`) and verifies trace persistence in PostgreSQL. |
| **FastAPI REST Endpoints** | `test_api_endpoints.py` | Validates HTTP status codes, Pydantic schemas, and error responses across `/api/v1/intentflow/*`. |
| **Vertical Lifecycle** | `test_vertical_workflow.py` | Validates complete user flow: Create project $\to$ Ingest URL $\to$ Generate variants $\to$ Approve variant $\to$ Launch A/B experiment $\to$ Simulate traffic $\to$ Verify statistical lift. |

---

## 3. Automated Test Execution Commands

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run all integration tests against PostgreSQL
pytest tests/integration/ -v

# Run entire 17-test regression suite
pytest tests/ -v

# Run Next.js frontend production build and type checking
npm run build --prefix frontend
```
