# IntentFlow AI — Security Model & Threat Mitigation

## 1. Threat Landscape & Security Posture
IntentFlow AI operates in dual domains with high operational risk:
1. **Dynamic Web Scraping & Ingestion**: Processing untrusted third-party URLs provided by users.
2. **Autonomous Agent Operations**: Directing generative AI to produce customer-facing copy and financial records.

This document articulates the defense-in-depth security model implemented in `services/page_ingestion_service.py`, `services/brand_validator_service.py`, and `services/invoice_service.py`.

---

## 2. Server-Side Request Forgery (SSRF) Defense

### 2.1 Threat Vector
An adversary provides internal URLs (e.g., `http://169.254.169.254/latest/meta-data/`, `http://localhost:5432`, or `http://10.0.0.1/admin`) to extract cloud credentials, pivot across internal subnets, or probe microservices.

### 2.2 Mitigation Strategy (`services/page_ingestion_service.py`)
IntentFlow AI enforces multi-layered pre-fetch IP inspection:

1. **Protocol Whitelisting**:
   - Only `http://` and `https://` schemes are permitted. File, FTP, gopher, and custom schemes are rejected immediately.
2. **DNS Resolution & Subnet Filtering**:
   - Hostnames are resolved to IP addresses prior to initiating the HTTP socket connection.
   - Evaluated via Python's standard `ipaddress` module against blocked CIDR ranges:
     - **Loopback**: `127.0.0.0/8`, `::1`
     - **Private RFC 1918**: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
     - **Link-Local & Cloud Metadata**: `169.254.0.0/16`, `fe80::/10` (specifically neutralizing AWS/GCP metadata endpoints: `169.254.169.254`)
3. **Payload Buffering Cap**:
   - Streaming HTTP responses terminate if response bodies exceed 2,097,152 bytes (2 MB), preventing memory exhaustion / denial of service.
4. **Enforced Timeouts**:
   - Total network timeout is capped at 10.0 seconds to prevent slowloris connection-holding attacks.
5. **Redirect Inspection**:
   - Subsequent redirect locations are recursively passed through the same validation pipeline.

---

## 3. Brand & Marketing Claim Safety Guardrails

### 3.1 Threat Vector
LLMs hallucinate illegal, deceptive, or non-compliant marketing claims (e.g. "100% guaranteed ROI", "risk-free guarantee") that expose customers to regulatory liability under FTC / advertising standards.

### 3.2 Mitigation Strategy (`services/brand_validator_service.py`)
- **Deterministic String Matching**: Before any copy reaches the user or human reviewer, it is scanned against project-configured prohibited terms.
- **Punctuation-Agnostic Normalization**: Substring analysis handles punctuation and symbol boundaries (e.g. `%` in `100% guaranteed roi`).
- **Strict Brand Score Penalization**: Detection of any prohibited term deducts 40 points from the brand score and sets `is_valid: False`.

---

## 4. Financial Determinism & Transaction Isolation

### 4.1 Threat Vector
- Floating-point arithmetic errors leading to compounding tax or currency balance discrepancies.
- Concurrent double-spending or duplicate invoice issuance on network retries.

### 4.2 Mitigation Strategy
- **`Decimal` Math**: All monetary amounts and GST calculations use Python `Decimal` with `ROUND_HALF_UP` precision.
- **ACID Transactions**: Database mutations utilize PostgreSQL transactions (`async with session.begin():`).
- **Idempotency Keys**: Invoice issuance endpoints enforce idempotency keys to ensure duplicate submissions return the original created record without state corruption.
- **Human-in-the-Loop Confirmation**: AI agents are strictly prohibited from issuing invoices directly to clients; they may only create drafts in `needs_review` state.
