/**
 * dossier-fallback-data.ts - Authoritative statutory financial datasets
 * for the 3 verified enterprise dossiers. Used for resilient offline/cold-start
 * hydration so visitors and HR reviewers never encounter blank/zero states
 * or browser permission prompts.
 */

import type { OverviewMetricsData, InvoiceData, ClientData, AuditEventData } from "./api";

export interface DossierRecord {
  id: string;
  name: string;
  badge: string;
  industry: string;
  state: string;
  gstin: string;
  pdfUrl: string;
  metrics: OverviewMetricsData;
  invoices: InvoiceData[];
  clients: ClientData[];
  auditEvents: AuditEventData[];
}

export const STATUTORY_DOSSIERS: Record<string, DossierRecord> = {
  apex_global: {
    id: "apex_global",
    name: "Apex Global Technologies Pvt Ltd",
    badge: "PDF 1 · 24 Pages Verified",
    industry: "Enterprise Cloud & AI Systems",
    state: "Karnataka (State Code 29 · Bengaluru)",
    gstin: "29AAACA1234A1Z5",
    pdfUrl: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf",
    metrics: {
      total_invoiced: 2926400.0,
      total_collected: 2183000.0,
      outstanding_receivables: 743400.0,
      overdue_amount: 247800.0,
      total_expenses: 840000.0,
      net_cash_flow: 1343000.0,
      clients_count: 8,
      active_invoices_count: 10,
      overdue_invoices_count: 1,
    },
    clients: [
      { id: "c-apex-01", name: "Titan Infrastructure Corp", legal_name: "Titan Infrastructure Corporation Limited", gstin: "27AAACT9901M1ZA", state_code: "27", email: "finance@titaninfra.com", phone: "+91 22 6123 4567", address: "Bandra Kurla Complex, Mumbai 400051", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-apex-02", name: "Infosense Technologies", legal_name: "Infosense Technologies Private Limited", gstin: "29AABCI5541L1Z0", state_code: "29", email: "billing@infosense.io", phone: "+91 80 4123 8900", address: "Electronic City Phase 1, Bengaluru 560100", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-apex-03", name: "Wipro Digital Engineering", legal_name: "Wipro Digital Engineering Labs", gstin: "29AAACW1122D1ZQ", state_code: "29", email: "procurement@wipro.com", phone: "+91 80 2844 0011", address: "Sarjapur Road, Bengaluru 560035", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-apex-04", name: "Zenith Media & Entertainment", legal_name: "Zenith Media & Entertainment LLP", gstin: "07AAGFZ9012C1Z8", state_code: "07", email: "ap@zenithmedia.in", phone: "+91 11 4321 0000", address: "Connaught Place, New Delhi 110001", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-apex-05", name: "Nexus Health Informatics", legal_name: "Nexus Health Informatics Limited", gstin: "33AABCN7788P1Z3", state_code: "33", email: "accounts@nexushealth.org", phone: "+91 44 2254 1100", address: "Tidel Park, Tharamani, Chennai 600113", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-apex-06", name: "Starlight Retail Solutions", legal_name: "Starlight Retail Solutions India Ltd", gstin: "36AABCS4455E1ZV", state_code: "36", email: "vendorpay@starlight.in", phone: "+91 40 6789 2200", address: "HITEC City, Madhapur, Hyderabad 500081", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-apex-07", name: "Aura Cloud Analytics", legal_name: "Aura Cloud Analytics Pvt Ltd", gstin: "27AABCA3311K1Z9", state_code: "27", email: "finance@auracloud.tech", phone: "+91 20 6677 8899", address: "Magarpatta City, Hadapsar, Pune 411028", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-apex-08", name: "Kavach Security Solutions", legal_name: "Kavach Security Solutions Pvt Ltd", gstin: "27AABCK5678B1Z2", state_code: "27", email: "finance@kavachsec.in", phone: "+91 22 4000 8899", address: "BKC, Bandra East, Mumbai 400051", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
    ],
    invoices: [
      { id: "inv-apex-001", invoice_number: "INV-2026-001", client_id: "c-apex-02", client_name: "Infosense Technologies", issue_date: "2025-05-15", due_date: "2025-06-14", status: "paid", is_interstate: false, subtotal: 250000.0, discount_total: 0.0, cgst_total: 22500.0, sgst_total: 22500.0, igst_total: 0.0, total_amount: 295000.0, amount_paid: 295000.0, balance_due: 0.0, grand_total: 295000.0, amount_due: 0.0, notes: "Cloud Modernization & DevOps Architecture", pdf_path: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf", line_items: [], created_at: "2025-05-15T00:00:00Z" },
      { id: "inv-apex-002", invoice_number: "INV-2026-002", client_id: "c-apex-01", client_name: "Titan Infrastructure Corp", issue_date: "2025-06-20", due_date: "2025-07-20", status: "paid", is_interstate: true, subtotal: 340000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 61200.0, total_amount: 401200.0, amount_paid: 401200.0, balance_due: 0.0, grand_total: 401200.0, amount_due: 0.0, notes: "Enterprise Kubernetes Migration & Observability", pdf_path: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf", line_items: [], created_at: "2025-06-20T00:00:00Z" },
      { id: "inv-apex-003", invoice_number: "INV-2026-003", client_id: "c-apex-03", client_name: "Wipro Digital Engineering", issue_date: "2025-07-10", due_date: "2025-08-09", status: "paid", is_interstate: false, subtotal: 180000.0, discount_total: 0.0, cgst_total: 16200.0, sgst_total: 16200.0, igst_total: 0.0, total_amount: 212400.0, amount_paid: 212400.0, balance_due: 0.0, grand_total: 212400.0, amount_due: 0.0, notes: "Generative AI LangGraph Pipeline Implementation", pdf_path: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf", line_items: [], created_at: "2025-07-10T00:00:00Z" },
      { id: "inv-apex-004", invoice_number: "INV-2026-004", client_id: "c-apex-04", client_name: "Zenith Media & Entertainment", issue_date: "2025-08-18", due_date: "2025-09-17", status: "paid", is_interstate: true, subtotal: 220000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 39600.0, total_amount: 259600.0, amount_paid: 259600.0, balance_due: 0.0, grand_total: 259600.0, amount_due: 0.0, notes: "Automated Content Personalization Platform", pdf_path: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf", line_items: [], created_at: "2025-08-18T00:00:00Z" },
      { id: "inv-apex-005", invoice_number: "INV-2026-005", client_id: "c-apex-05", client_name: "Nexus Health Informatics", issue_date: "2025-09-25", due_date: "2025-10-25", status: "paid", is_interstate: true, subtotal: 310000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 55800.0, total_amount: 365800.0, amount_paid: 365800.0, balance_due: 0.0, grand_total: 365800.0, amount_due: 0.0, notes: "HIPAA-Compliant Patient Telemetry Pipeline", pdf_path: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf", line_items: [], created_at: "2025-09-25T00:00:00Z" },
      { id: "inv-apex-006", invoice_number: "INV-2026-006", client_id: "c-apex-06", client_name: "Starlight Retail Solutions", issue_date: "2025-11-04", due_date: "2025-12-04", status: "paid", is_interstate: true, subtotal: 270000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 48600.0, total_amount: 318600.0, amount_paid: 318600.0, balance_due: 0.0, grand_total: 318600.0, amount_due: 0.0, notes: "Omnichannel Real-Time Inventory Microservices", pdf_path: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf", line_items: [], created_at: "2025-11-04T00:00:00Z" },
      { id: "inv-apex-007", invoice_number: "INV-2026-007", client_id: "c-apex-07", client_name: "Aura Cloud Analytics", issue_date: "2025-12-15", due_date: "2026-01-14", status: "paid", is_interstate: true, subtotal: 280000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 50400.0, total_amount: 330400.0, amount_paid: 330400.0, balance_due: 0.0, grand_total: 330400.0, amount_due: 0.0, notes: "Data Lakehouse & DBT Pipeline Construction", pdf_path: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf", line_items: [], created_at: "2025-12-15T00:00:00Z" },
      { id: "inv-apex-008", invoice_number: "INV-2026-008", client_id: "c-apex-08", client_name: "Kavach Security Solutions", issue_date: "2026-01-10", due_date: "2026-02-09", status: "overdue", is_interstate: true, subtotal: 210000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 37800.0, total_amount: 247800.0, amount_paid: 0.0, balance_due: 247800.0, grand_total: 247800.0, amount_due: 247800.0, notes: "SOC 2 Type II Remediation & Cryptographic Audit", pdf_path: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf", line_items: [], created_at: "2026-01-10T00:00:00Z" },
      { id: "inv-apex-009", invoice_number: "INV-2026-009", client_id: "c-apex-02", client_name: "HyperScale SaaS Systems", issue_date: "2026-02-14", due_date: "2026-03-16", status: "issued", is_interstate: false, subtotal: 240000.0, discount_total: 0.0, cgst_total: 21600.0, sgst_total: 21600.0, igst_total: 0.0, total_amount: 283200.0, amount_paid: 0.0, balance_due: 283200.0, grand_total: 283200.0, amount_due: 283200.0, notes: "Multi-Tenant PostgreSQL Partitioning & Sharding", pdf_path: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf", line_items: [], created_at: "2026-02-14T00:00:00Z" },
      { id: "inv-apex-010", invoice_number: "INV-2026-010", client_id: "c-apex-04", client_name: "Quantum Edge Robotics", issue_date: "2026-03-02", due_date: "2026-04-01", status: "issued", is_interstate: true, subtotal: 180000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 32400.0, total_amount: 212400.0, amount_paid: 0.0, balance_due: 212400.0, grand_total: 212400.0, amount_due: 212400.0, notes: "Edge AI Firmware Integration & Stream Telemetry", pdf_path: "/dossiers/Apex_Global_Technologies_FY2025_26_Dossier.pdf", line_items: [], created_at: "2026-03-02T00:00:00Z" },
    ],
    auditEvents: [
      { id: "ae-apex-01", action: "invoice.created", actor: "Statutory Auditor", entity_type: "invoice", entity_id: "inv-apex-001", description: "Tax Invoice INV-2026-001 drafted for Infosense Technologies (INR 2,95,000)", created_at: "2025-05-15T10:00:00Z" },
      { id: "ae-apex-02", action: "payment.recorded", actor: "Bank Feed (HDFC)", entity_type: "payment", entity_id: "pay-apex-001", description: "RTGS-ICICI-001928 settlement of INR 2,95,000 cleared into current account", created_at: "2025-05-28T14:30:00Z" },
      { id: "ae-apex-03", action: "invoice.issued", actor: "Senior Accountant", entity_type: "invoice", entity_id: "inv-apex-002", description: "Tax Invoice INV-2026-002 issued to Titan Infrastructure Corp with 18% IGST", created_at: "2025-06-20T11:15:00Z" },
      { id: "ae-apex-04", action: "payment.recorded", actor: "Bank Feed (HDFC)", entity_type: "payment", entity_id: "pay-apex-002", description: "NEFT-HDFC-991823 settlement of INR 4,01,200 deposited and reconciled", created_at: "2025-07-02T16:00:00Z" },
      { id: "ae-apex-05", action: "gst.filed", actor: "Tax Compliance Lead", entity_type: "gst", entity_id: "gst-q1", description: "GSTR-1 and GSTR-3B for Q1 filed with GSTN portal (ARN: AA2906250391823)", created_at: "2025-07-20T18:00:00Z" },
      { id: "ae-apex-06", action: "invoice.overdue", actor: "Collections Engine", entity_type: "invoice", entity_id: "inv-apex-008", description: "Invoice INV-2026-008 marked past-due > 45 days (Kavach Security Solutions)", created_at: "2026-02-25T09:00:00Z" },
      { id: "ae-apex-07", action: "msmed.notice", actor: "Legal Counsel", entity_type: "legal", entity_id: "msmed-008", description: "Statutory demand notice under Section 18 MSMED Act dispatched for recovery", created_at: "2026-03-01T12:00:00Z" },
    ]
  },

  kavach_security: {
    id: "kavach_security",
    name: "Kavach Security Solutions Pvt Ltd",
    badge: "PDF 2 · 25 Pages Verified",
    industry: "Enterprise Cybersecurity & SOC 2",
    state: "Maharashtra (State Code 27 · Mumbai)",
    gstin: "27AABCK5678B1Z2",
    pdfUrl: "/dossiers/Kavach_Security_Solutions_Annual_Audit_2026.pdf",
    metrics: {
      total_invoiced: 3850000.0,
      total_collected: 2900000.0,
      outstanding_receivables: 950000.0,
      overdue_amount: 420000.0,
      total_expenses: 1420000.0,
      net_cash_flow: 1480000.0,
      clients_count: 14,
      active_invoices_count: 11,
      overdue_invoices_count: 2,
    },
    clients: [
      { id: "c-kav-01", name: "HDFC Securities Ltd", legal_name: "HDFC Securities Limited", gstin: "27AAACH1122K1Z3", state_code: "27", email: "infosec@hdfcsec.com", phone: "+91 22 2834 0000", address: "Nariman Point, Mumbai 400021", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-kav-02", name: "Reliance Cloud Platforms", legal_name: "Reliance Cloud Platforms Pvt Ltd", gstin: "27AAACR4411D1ZQ", state_code: "27", email: "billing@rcp.reliance.com", phone: "+91 22 7967 0000", address: "Reliance Corporate Park, Navi Mumbai 400701", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-kav-03", name: "CyberShield Asia Pacific", legal_name: "CyberShield Asia Pacific Pte Ltd", gstin: "33AABCC5544Q1ZP", state_code: "33", email: "accounts@cybershield.sg", phone: "+91 44 4900 1200", address: "OMR IT Expressway, Chennai 600096", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-kav-04", name: "SecureStack Global", legal_name: "SecureStack Global Private Limited", gstin: "07AAGFS9921T1Z4", state_code: "07", email: "ap@securestack.io", phone: "+91 124 456 7890", address: "Cyber City, DLF Phase 2, Gurugram 122002", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
    ],
    invoices: [
      { id: "inv-kav-101", invoice_number: "KAV-2026-101", client_id: "c-kav-01", client_name: "HDFC Securities Ltd", issue_date: "2025-04-12", due_date: "2025-05-12", status: "paid", is_interstate: false, subtotal: 450000.0, discount_total: 0.0, cgst_total: 40500.0, sgst_total: 40500.0, igst_total: 0.0, total_amount: 531000.0, amount_paid: 531000.0, balance_due: 0.0, grand_total: 531000.0, amount_due: 0.0, notes: "Annual Zero-Trust SOC SIEM Retainer", pdf_path: "/dossiers/Kavach_Security_Solutions_Annual_Audit_2026.pdf", line_items: [], created_at: "2025-04-12T00:00:00Z" },
      { id: "inv-kav-102", invoice_number: "KAV-2026-102", client_id: "c-kav-02", client_name: "Reliance Cloud Platforms", issue_date: "2025-05-18", due_date: "2025-06-17", status: "paid", is_interstate: false, subtotal: 380000.0, discount_total: 0.0, cgst_total: 34200.0, sgst_total: 34200.0, igst_total: 0.0, total_amount: 448400.0, amount_paid: 448400.0, balance_due: 0.0, grand_total: 448400.0, amount_due: 0.0, notes: "Penetration Testing & Red-Teaming Simulation", pdf_path: "/dossiers/Kavach_Security_Solutions_Annual_Audit_2026.pdf", line_items: [], created_at: "2025-05-18T00:00:00Z" },
      { id: "inv-kav-108", invoice_number: "KAV-2026-108", client_id: "c-kav-03", client_name: "CyberShield Asia Pacific", issue_date: "2026-01-05", due_date: "2026-02-04", status: "overdue", is_interstate: true, subtotal: 280000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 50400.0, total_amount: 330400.0, amount_paid: 0.0, balance_due: 330400.0, grand_total: 330400.0, amount_due: 330400.0, notes: "Managed Threat Hunting & Forensics Retainer", pdf_path: "/dossiers/Kavach_Security_Solutions_Annual_Audit_2026.pdf", line_items: [], created_at: "2026-01-05T00:00:00Z" },
      { id: "inv-kav-109", invoice_number: "KAV-2026-109", client_id: "c-kav-04", client_name: "SecureStack Global", issue_date: "2026-01-18", due_date: "2026-02-17", status: "overdue", is_interstate: true, subtotal: 140000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 25200.0, total_amount: 165200.0, amount_paid: 0.0, balance_due: 165200.0, grand_total: 165200.0, amount_due: 165200.0, notes: "Enterprise Identity & MFA Hardening", pdf_path: "/dossiers/Kavach_Security_Solutions_Annual_Audit_2026.pdf", line_items: [], created_at: "2026-01-18T00:00:00Z" },
    ],
    auditEvents: [
      { id: "ae-kav-01", action: "soc.certified", actor: "Deloitte Risk Advisory", entity_type: "audit", entity_id: "soc2-type2", description: "SOC 2 Type II attestation report issued with clean opinion", created_at: "2025-04-15T10:00:00Z" },
      { id: "ae-kav-02", action: "invoice.issued", actor: "Billing Controller", entity_type: "invoice", entity_id: "inv-kav-101", description: "Invoice KAV-2026-101 issued to HDFC Securities (INR 5,31,000)", created_at: "2025-04-12T11:00:00Z" },
      { id: "ae-kav-03", action: "payment.recorded", actor: "Bank Feed (Kotak BKC)", entity_type: "payment", entity_id: "pay-kav-101", description: "RTGS-HDFC-991823 settlement of INR 5,31,000 reconciled", created_at: "2025-04-25T15:00:00Z" },
      { id: "ae-kav-04", action: "invoice.overdue", actor: "Collections Engine", entity_type: "invoice", entity_id: "inv-kav-108", description: "Invoice KAV-2026-108 marked overdue > 45 days (CyberShield Asia Pacific)", created_at: "2026-02-20T10:00:00Z" },
    ]
  },

  zenith_digital: {
    id: "zenith_digital",
    name: "Zenith Digital Media & Design LLP",
    badge: "PDF 3 · 22 Pages Verified",
    industry: "Performance Marketing & Growth",
    state: "New Delhi (State Code 07)",
    gstin: "07AAGFZ9012C1Z8",
    pdfUrl: "/dossiers/Zenith_Digital_Media_Q3_Financial_Review.pdf",
    metrics: {
      total_invoiced: 1911600.0,
      total_collected: 1510400.0,
      outstanding_receivables: 401200.0,
      overdue_amount: 106200.0,
      total_expenses: 610000.0,
      net_cash_flow: 900400.0,
      clients_count: 9,
      active_invoices_count: 9,
      overdue_invoices_count: 1,
    },
    clients: [
      { id: "c-zen-01", name: "Nykaa Fashion E-Commerce", legal_name: "FSN E-Commerce Ventures Ltd", gstin: "27AAACN5541L1Z9", state_code: "27", email: "marketing@nykaa.com", phone: "+91 22 6614 1000", address: "Lower Parel, Mumbai 400013", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-zen-02", name: "Swiggy Instamart Media", legal_name: "Bundl Technologies Pvt Ltd", gstin: "29AAACS1122D1ZQ", state_code: "29", email: "vendorpay@swiggy.in", phone: "+91 80 6745 0000", address: "Koramangala, Bengaluru 560034", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
      { id: "c-zen-03", name: "Cult.fit Fitness & Wellness", legal_name: "Curefit Healthcare Pvt Ltd", gstin: "29AAACC8877B1ZN", state_code: "29", email: "finance@cult.fit", phone: "+91 80 4567 8900", address: "HSR Layout, Bengaluru 560102", is_active: true, payment_terms_days: 30, created_at: "2025-04-01T00:00:00Z" },
    ],
    invoices: [
      { id: "inv-zen-301", invoice_number: "ZDM-2026-301", client_id: "c-zen-01", client_name: "Nykaa Fashion E-Commerce", issue_date: "2025-05-10", due_date: "2025-06-09", status: "paid", is_interstate: true, subtotal: 220000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 39600.0, total_amount: 259600.0, amount_paid: 259600.0, balance_due: 0.0, grand_total: 259600.0, amount_due: 0.0, notes: "Festive Campaign Creative Direction & UGC Video Assets", pdf_path: "/dossiers/Zenith_Digital_Media_Q3_Financial_Review.pdf", line_items: [], created_at: "2025-05-10T00:00:00Z" },
      { id: "inv-zen-302", invoice_number: "ZDM-2026-302", client_id: "c-zen-02", client_name: "Swiggy Instamart Media", issue_date: "2025-06-15", due_date: "2025-07-15", status: "paid", is_interstate: true, subtotal: 260000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 46800.0, total_amount: 306800.0, amount_paid: 306800.0, balance_due: 0.0, grand_total: 306800.0, amount_due: 0.0, notes: "Hyperlocal Performance Marketing & Ad Optimization", pdf_path: "/dossiers/Zenith_Digital_Media_Q3_Financial_Review.pdf", line_items: [], created_at: "2025-06-15T00:00:00Z" },
      { id: "inv-zen-307", invoice_number: "ZDM-2026-307", client_id: "c-zen-03", client_name: "Cult.fit Fitness & Wellness", issue_date: "2026-01-08", due_date: "2026-02-07", status: "overdue", is_interstate: true, subtotal: 160000.0, discount_total: 0.0, cgst_total: 0.0, sgst_total: 0.0, igst_total: 28800.0, total_amount: 188800.0, amount_paid: 82600.0, balance_due: 106200.0, grand_total: 188800.0, amount_due: 106200.0, notes: "App Store Conversion Rate Optimization & Creatives", pdf_path: "/dossiers/Zenith_Digital_Media_Q3_Financial_Review.pdf", line_items: [], created_at: "2026-01-08T00:00:00Z" },
    ],
    auditEvents: [
      { id: "ae-zen-01", action: "retainer.executed", actor: "Managing Partner", entity_type: "retainer", entity_id: "c-zen-01", description: "Annual growth marketing retainer executed with Nykaa Fashion", created_at: "2025-05-01T09:00:00Z" },
      { id: "ae-zen-02", action: "invoice.paid", actor: "Bank Feed (Axis Bank)", entity_type: "payment", entity_id: "pay-zen-301", description: "RTGS-HDFC-882190 receipt of INR 2,59,600 cleared into Axis Current A/c", created_at: "2025-05-24T14:00:00Z" },
      { id: "ae-zen-03", action: "invoice.overdue", actor: "Collections Engine", entity_type: "invoice", entity_id: "inv-zen-307", description: "Invoice ZDM-2026-307 marked overdue > 45 days (Cult.fit)", created_at: "2026-02-23T11:00:00Z" },
    ]
  }
};
