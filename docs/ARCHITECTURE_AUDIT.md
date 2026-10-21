# IntentFlow AI — Architectural Audit & Transformation Report

## 1. Executive Summary
This document presents the architectural audit of the base repository (`daniel-st3/ai-cfo-agent`) and details the full-stack engineering transformation undertaken to establish **IntentFlow AI**: a production-grade AI platform for website personalization, A/B experimentation, and deterministic financial operations.

This transformation bridges the capability requirements for:
1. **Fibr AI — AI Product Engineer**: AI-native website experience personalization, audience intent synthesis, LangGraph multi-step workflows, brand guardrails, comparative preview diffs, and A/B statistical experimentation.
2. **Variabl — Full-Stack Engineer (AI)**: Full-stack product architecture, PostgreSQL 18 persistence, typed REST APIs, deterministic decimal calculation engines, ReportLab PDF rendering, and idempotent workflows.

---

## 2. Baseline Repository Audit (`daniel-st3/ai-cfo-agent`)

### 2.1 Identified Assets & Strengths
- **FastAPI Scaffold**: Clean asynchronous endpoint structure.
- **Invoice PDF Generation**: Solid ReportLab integration for generating structured PDF invoices.
- **Next.js & Tailwind UI**: Modern component structure with Lucide icons.

### 2.2 Critical Deficiencies & Architectural Debt
- **Single-Domain Vulnerability**: Solely focused on financial reporting without enterprise personalization or marketing optimization capabilities.
- **Security Vulnerabilities**: Missing Server-Side Request Forgery (SSRF) defenses on external web requests (vulnerable to cloud metadata exfiltration at `169.254.169.254`).
- **Mathematical Imprecision**: Primitive floating-point math rather than fixed-point `Decimal` arithmetic for financial tax splits.
- **Absence of Guardrails**: No programmatic brand safety or prohibited claims enforcement.
- **Lack of Statistical Inference**: Absence of controlled experimentation, deterministic visitor partitioning, or z-test statistical hypothesis testing.
- **Missing Observability**: Agent steps executed without persistent trace logging, latency tracking, or automated evaluation test batteries.

---

## 3. The IntentFlow AI Transformation

### 3.1 Dual-Domain Enterprise Architecture
To satisfy both Fibr AI and Variabl role benchmarks without duplicating core agent infrastructure, IntentFlow AI was engineered as a shared platform powering two connected studios:
1. **Primary Experience (75% Priority): AI Website Experience Studio**
   - Safe SSRF-filtered web page ingestion with DOM structural component extraction.
   - Audience intent mapping and behavioral hypothesis formulation.
   - 6-step compiled LangGraph StateGraph variant generation.
   - Deterministic brand guardrails intercepting prohibited marketing claims.
   - Comparative Desktop / Mobile (375px) preview with copy diff highlighting.
   - Controlled A/B experimentation with sticky MD5 visitor allocation.
   - Statistical inference engine: two-proportion pooled z-tests, normal CDF p-values, 95% confidence intervals, and low-sample guards ($n < 30$).
   - 1-click synthetic traffic simulator for live demonstration.
2. **Secondary Experience (25% Priority): AI Finance Operations Studio**
   - Indian GST compliance (intra-state CGST 9% + SGST 9% vs inter-state IGST 18%).
   - Immutable double-entry client ledgers with running balance calculations.
   - ReportLab PDF invoice generation.
   - LangGraph CFO assistant with Human-in-the-Loop approval checkpoints.

### 3.2 Shared Platform Infrastructure
- **Persistence**: PostgreSQL 18 database with 39 normalized tables and ACID transactional boundaries.
- **Agent Orchestration**: LangGraph StateGraphs with typed states and deterministic tool execution.
- **Observability**: Real-time trace collection logging node transitions, latencies, and token counts.
- **Continuous AI Evaluation**: Automated test suite asserting brand safety, copy boundaries, schema validity, and financial precision.
