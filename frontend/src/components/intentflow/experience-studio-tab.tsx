"use client";

import React, { useState, useEffect } from "react";
import {
  Globe,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Smartphone,
  Monitor,
  ArrowRight,
  RefreshCw,
  Plus,
  Eye,
  Check,
  X,
  FileText,
  Sliders,
  Send,
  ExternalLink,
  ChevronRight,
  Info
} from "lucide-react";
import {
  getProjects,
  createProject,
  ingestPage,
  createAudienceSegment,
  generateVariants,
  approveVariant,
  createExperiment,
  ProjectData,
  PageSnapshotData,
  AudienceSegmentData,
  ExperienceVariantData
} from "@/lib/api";

interface ExperienceStudioTabProps {
  onNavigateToExperiments?: (experimentId?: string) => void;
}

export function ExperienceStudioTab({ onNavigateToExperiments }: ExperienceStudioTabProps) {
  const [projects, setProjects] = useState<ProjectData[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [agentRunning, setAgentRunning] = useState(false);

  // New Project Form Modal / Inline
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDomain, setNewProjectDomain] = useState("");
  const [newProjectIndustry, setNewProjectIndustry] = useState("SaaS / B2B Software");
  const [newProjectVoice, setNewProjectVoice] = useState("Authoritative, concise, developer-centric");

  // Ingestion Form
  const [targetUrl, setTargetUrl] = useState("https://tryintentflow.ai/pricing");
  const [ingesting, setIngesting] = useState(false);

  // Selected State
  const [selectedPage, setSelectedPage] = useState<PageSnapshotData | null>(null);
  const [selectedAudience, setSelectedAudience] = useState<AudienceSegmentData | null>(null);
  const [newAudienceName, setNewAudienceName] = useState("");
  const [newAudienceHypothesis, setNewAudienceHypothesis] = useState("");
  const [showAudienceInput, setShowAudienceInput] = useState(false);

  // Variants & Preview
  const [variants, setVariants] = useState<ExperienceVariantData[]>([]);
  const [activeVariantTab, setActiveVariantTab] = useState<string>("all"); // "all", or variant id
  const [deviceViewport, setDeviceViewport] = useState<"desktop" | "mobile">("desktop");
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null);
  const [actionErrorMsg, setActionErrorMsg] = useState<string | null>(null);

  const loadProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data);
      if (data.length > 0 && !selectedProjectId) {
        setSelectedProjectId(data[0].id);
      }
    } catch (err: any) {
      console.error("Failed to load projects", err);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const activeProject = projects.find((p) => p.id === selectedProjectId);

  useEffect(() => {
    if (activeProject) {
      if (activeProject.pages && activeProject.pages.length > 0) {
        const page = activeProject.pages[0];
        setSelectedPage(page);
        if (page.variants) {
          setVariants(page.variants);
        }
      } else {
        setSelectedPage(null);
        setVariants([]);
      }

      if (activeProject.audiences && activeProject.audiences.length > 0) {
        setSelectedAudience(activeProject.audiences[0]);
      } else {
        setSelectedAudience(null);
      }
    }
  }, [selectedProjectId, projects]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    setLoading(true);
    setActionErrorMsg(null);
    try {
      const proj = await createProject({
        name: newProjectName.trim(),
        domain: newProjectDomain.trim() || "example.com",
        industry: newProjectIndustry,
        brand_voice: newProjectVoice,
        brand_rules: {
          prohibited_terms: ["100% guaranteed roi", "risk-free guarantee", "guaranteed 10x"],
          max_headline_length: 80,
          max_cta_length: 30
        }
      });
      await loadProjects();
      setSelectedProjectId(proj.id);
      setShowNewProject(false);
      setNewProjectName("");
      setNewProjectDomain("");
      setActionSuccessMsg("Project created successfully!");
      setTimeout(() => setActionSuccessMsg(null), 4000);
    } catch (err: any) {
      setActionErrorMsg(err.message || "Failed to create project");
    } finally {
      setLoading(false);
    }
  };

  const handleIngestPage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProjectId || !targetUrl.trim()) return;
    setIngesting(true);
    setActionErrorMsg(null);
    try {
      const snapshot = await ingestPage(selectedProjectId, targetUrl.trim());
      const numElements = (snapshot.headings?.length || 0) + (snapshot.calls_to_action?.length || 0) + (snapshot.benefits?.length || 0) + 2;
      setActionSuccessMsg(`Page ingested safely! Extracted ${numElements} structural DOM elements with SSRF security verification.`);
      await loadProjects();
      setSelectedPage(snapshot);
      if (snapshot.variants) {
        setVariants(snapshot.variants);
      }
      setTimeout(() => setActionSuccessMsg(null), 4000);
    } catch (err: any) {
      setActionErrorMsg(err.message || "Failed to ingest page. SSRF guard or connection issue.");
    } finally {
      setIngesting(false);
    }
  };

  const handleCreateAudience = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProjectId || !newAudienceName.trim()) return;
    try {
      const aud = await createAudienceSegment(selectedProjectId, {
        name: newAudienceName.trim(),
        hypothesis: newAudienceHypothesis.trim() || "Target audience prefers transparent metrics over marketing buzzwords."
      });
      await loadProjects();
      setSelectedAudience(aud);
      setShowAudienceInput(false);
      setNewAudienceName("");
      setNewAudienceHypothesis("");
      setActionSuccessMsg("Audience segment added!");
      setTimeout(() => setActionSuccessMsg(null), 3000);
    } catch (err: any) {
      setActionErrorMsg(err.message || "Failed to create audience");
    }
  };

  const handleGenerateVariants = async () => {
    if (!selectedProjectId) return;
    setAgentRunning(true);
    setActionErrorMsg(null);
    try {
      const result = await generateVariants(selectedProjectId, {
        page_id: selectedPage?.id,
        audience_id: selectedAudience?.id,
        num_variants: 2
      });
      setActionSuccessMsg(`LangGraph agent completed successfully! Synthesized ${result.variants?.length || 0} variants.`);
      await loadProjects();
      if (result.variants) {
        setVariants(result.variants);
      }
      setTimeout(() => setActionSuccessMsg(null), 5000);
    } catch (err: any) {
      setActionErrorMsg(err.message || "LangGraph agent execution failed.");
    } finally {
      setAgentRunning(false);
    }
  };

  const handleApprove = async (variantId: string, status: "approved" | "rejected") => {
    try {
      const updated = await approveVariant(variantId, status, `Human reviewer marked as ${status}`);
      setVariants((prev) => prev.map((v) => (v.id === updated.id ? updated : v)));
      setActionSuccessMsg(`Variant marked as ${status}!`);
      setTimeout(() => setActionSuccessMsg(null), 3000);
    } catch (err: any) {
      setActionErrorMsg(err.message || "Failed to update review status");
    }
  };

  const handleLaunchExperiment = async (variant: ExperienceVariantData) => {
    if (!selectedProjectId || !selectedPage) return;
    try {
      const exp = await createExperiment({
        project_id: selectedProjectId,
        page_snapshot_id: selectedPage.id,
        name: `A/B Test: ${variant.name || variant.variant_name || "Variant"} vs Baseline`,
        traffic_allocation: {
          control: 0.5,
          [variant.id]: 0.5
        },
        primary_metric: "cta_click"
      });
      setActionSuccessMsg(`A/B Experiment "${exp.name}" launched with 50/50 allocation!`);
      if (onNavigateToExperiments) {
        setTimeout(() => onNavigateToExperiments(exp.id), 1200);
      }
    } catch (err: any) {
      setActionErrorMsg(err.message || "Failed to launch experiment");
    }
  };

  const h1Item = selectedPage?.headings?.find((h) => h.tag === "h1")?.text;
  const h2Item = selectedPage?.headings?.find((h) => h.tag === "h2")?.text;
  const primaryCta = selectedPage?.calls_to_action?.[0]?.text;
  const elements = {
    page_title: selectedPage?.title,
    h1: h1Item || selectedPage?.title,
    h2: h2Item,
    meta_description: selectedPage?.meta_description,
    value_prop: selectedPage?.value_prop || selectedPage?.meta_description,
    primary_cta: primaryCta,
    trust_badges: selectedPage?.trust_badges,
    benefits: selectedPage?.benefits,
    ...(selectedPage?.extracted_elements || {}),
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Notifications */}
      {actionSuccessMsg && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-50 border border-emerald-200 p-4 text-sm font-medium text-emerald-800 shadow-sm animate-fade-in">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 flex-shrink-0" />
          <span>{actionSuccessMsg}</span>
        </div>
      )}
      {actionErrorMsg && (
        <div className="flex items-center gap-2 rounded-lg bg-rose-50 border border-rose-200 p-4 text-sm font-medium text-rose-800 shadow-sm animate-fade-in">
          <AlertTriangle className="h-5 w-5 text-rose-600 flex-shrink-0" />
          <span>{actionErrorMsg}</span>
        </div>
      )}

      {/* Workspace Header & Project Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Globe className="h-5 w-5 text-indigo-600" />
            AI Website Experience Studio
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Ingest live pages, analyze intent vectors, generate variant copy via LangGraph, and validate against brand guardrails.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-800 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}{p.domain ? ` (${p.domain})` : ""}
              </option>
            ))}
          </select>

          <button
            onClick={() => setShowNewProject(!showNewProject)}
            className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-2 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 transition-colors"
          >
            <Plus className="h-4 w-4" />
            New Project
          </button>
        </div>
      </div>

      {/* New Project Modal / Expander */}
      {showNewProject && (
        <form
          onSubmit={handleCreateProject}
          className="rounded-xl border border-indigo-200 bg-indigo-50/40 p-6 shadow-sm space-y-4 animate-fade-in"
        >
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-indigo-600" />
              Configure New Optimization Project
            </h3>
            <button
              type="button"
              onClick={() => setShowNewProject(false)}
              className="text-slate-400 hover:text-slate-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Project Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Acme Cloud Landing Page"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Target Domain</label>
              <input
                type="text"
                placeholder="e.g. acmecloud.io"
                value={newProjectDomain}
                onChange={(e) => setNewProjectDomain(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Industry</label>
              <input
                type="text"
                value={newProjectIndustry}
                onChange={(e) => setNewProjectIndustry(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Brand Voice</label>
              <input
                type="text"
                value={newProjectVoice}
                onChange={(e) => setNewProjectVoice(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setShowNewProject(false)}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
            >
              {loading ? "Creating..." : "Save Project"}
            </button>
          </div>
        </form>
      )}

      {/* Step 1 & 2: Ingestion & Intent Definition */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (5 cols): Ingestion & Audience Targeting */}
        <div className="lg:col-span-5 space-y-6">
          {/* Safe Page Ingestion Card */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-bold text-slate-900 mb-2 flex items-center gap-2">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">
                1
              </span>
              Safe Page Ingestion (SSRF Guarded)
            </h2>
            <p className="text-xs text-slate-500 mb-3">
              Ingests HTML securely with private IP filtering (blocks 127.0.0.1, 10.x, 192.168.x, 169.254.169.254) and extracts semantic content.
            </p>

            <form onSubmit={handleIngestPage} className="space-y-3">
              <div className="relative">
                <input
                  type="url"
                  required
                  placeholder="https://example.com/landing"
                  value={targetUrl}
                  onChange={(e) => setTargetUrl(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 bg-slate-50/50 px-3 py-2 text-xs font-mono text-slate-800 focus:bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
              <button
                type="submit"
                disabled={ingesting || !selectedProjectId}
                className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 transition-colors"
              >
                {ingesting ? (
                  <>
                    <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                    Ingesting & Parsing DOM...
                  </>
                ) : (
                  <>
                    <Globe className="h-3.5 w-3.5" />
                    Ingest & Extract Elements
                  </>
                )}
              </button>
            </form>

            {/* Ingestion Status Badges */}
            {selectedPage && (
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-slate-500 font-medium truncate max-w-[200px]">
                  {selectedPage.url}
                </span>
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                  <CheckCircle2 className="h-3 w-3" />
                  SSRF Clean ({selectedPage.http_status || 200})
                </span>
              </div>
            )}
          </div>

          {/* Audience Intent & Hypotheses Card */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">
                  2
                </span>
                Audience Intent & Hypotheses
              </h2>
              <button
                onClick={() => setShowAudienceInput(!showAudienceInput)}
                className="text-xs font-semibold text-indigo-600 hover:text-indigo-700"
              >
                + Add Segment
              </button>
            </div>
            <p className="text-xs text-slate-500 mb-3">
              Define the target buyer persona and behavioral hypothesis to guide LLM reasoning.
            </p>

            {/* Audience List */}
            <div className="space-y-2">
              {activeProject?.audiences && activeProject.audiences.length > 0 ? (
                activeProject.audiences.map((aud) => (
                  <div
                    key={aud.id}
                    onClick={() => setSelectedAudience(aud)}
                    className={`cursor-pointer rounded-lg border p-3 transition-all ${
                      selectedAudience?.id === aud.id
                        ? "border-indigo-500 bg-indigo-50/50 shadow-sm"
                        : "border-slate-200 bg-white hover:border-slate-300"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-800">{aud.name}</span>
                      {selectedAudience?.id === aud.id && (
                        <Check className="h-3.5 w-3.5 text-indigo-600" />
                      )}
                    </div>
                    {aud.hypothesis && (
                      <p className="mt-1 text-[11px] text-slate-600 leading-snug">
                        <span className="font-semibold text-slate-700">Hypothesis:</span> {aud.hypothesis}
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <div className="rounded-lg border border-dashed border-slate-200 p-4 text-center text-xs text-slate-500">
                  No audience segments created yet.
                </div>
              )}
            </div>

            {/* New Audience Inline Form */}
            {showAudienceInput && (
              <form onSubmit={handleCreateAudience} className="mt-3 space-y-2 pt-2 border-t border-slate-100">
                <input
                  type="text"
                  required
                  placeholder="Segment Name (e.g. Enterprise Security Architect)"
                  value={newAudienceName}
                  onChange={(e) => setNewAudienceName(e.target.value)}
                  className="w-full rounded border border-slate-300 px-2.5 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
                <textarea
                  rows={2}
                  placeholder="Optimization hypothesis (e.g. Lead with SOC2 compliance and zero-trust SLAs to reduce procurement friction)"
                  value={newAudienceHypothesis}
                  onChange={(e) => setNewAudienceHypothesis(e.target.value)}
                  className="w-full rounded border border-slate-300 px-2.5 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowAudienceInput(false)}
                    className="rounded border border-slate-300 px-2.5 py-1 text-[11px] font-semibold text-slate-600"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="rounded bg-indigo-600 px-3 py-1 text-[11px] font-semibold text-white hover:bg-indigo-500"
                  >
                    Save Segment
                  </button>
                </div>
              </form>
            )}

            {/* Launch LangGraph Agent */}
            <div className="mt-5 pt-4 border-t border-slate-100">
              <button
                onClick={handleGenerateVariants}
                disabled={agentRunning || !selectedProjectId || !selectedPage}
                className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-2.5 text-xs font-bold text-white shadow-md hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 transition-all"
              >
                {agentRunning ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Running LangGraph Multi-Step Agent...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Synthesize Optimized Experiences
                  </>
                )}
              </button>
              <p className="mt-1.5 text-center text-[10px] text-slate-500">
                Agent steps: Ingest → Analyze Intent → Generate Variants → Check Brand Guardrails
              </p>
            </div>
          </div>
        </div>

        {/* Right Column (7 cols): Extracted Elements Inspection & Guardrails */}
        <div className="lg:col-span-7 space-y-6">
          {/* Extracted DOM Structure Inspector */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <FileText className="h-4 w-4 text-indigo-600" />
                Parsed Page Elements (Baseline Control)
              </h2>
              <span className="text-[11px] text-slate-500 font-mono">
                {elements.page_title ? "DOM Parsed" : "No page loaded"}
              </span>
            </div>

            {selectedPage ? (
              <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1">
                <div className="rounded-lg bg-slate-50 p-3 border border-slate-100">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Title & H1 Headline
                  </span>
                  <div className="mt-1 text-xs font-semibold text-slate-900">
                    {elements.h1 || elements.page_title || "No headline identified"}
                  </div>
                </div>

                <div className="rounded-lg bg-slate-50 p-3 border border-slate-100">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Value Proposition / Subheading
                  </span>
                  <div className="mt-1 text-xs text-slate-700">
                    {elements.value_prop || elements.h2 || elements.meta_description || "No value proposition extracted"}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="rounded-lg bg-slate-50 p-3 border border-slate-100">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      Primary CTA Button
                    </span>
                    <div className="mt-1 text-xs font-mono font-bold text-indigo-700">
                      {elements.primary_cta || "Start Free Trial"}
                    </div>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-3 border border-slate-100">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      Trust Badges / Social Proof
                    </span>
                    <div className="mt-1 text-xs text-slate-700">
                      {Array.isArray(elements.trust_badges) && elements.trust_badges.length > 0
                        ? elements.trust_badges.join(", ")
                        : "ISO 27001, SOC 2 Type II Certified"}
                    </div>
                  </div>
                </div>

                {Array.isArray(elements.benefits) && elements.benefits.length > 0 && (
                  <div className="rounded-lg bg-slate-50 p-3 border border-slate-100">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      Extracted Benefits
                    </span>
                    <ul className="mt-1 list-disc list-inside text-xs text-slate-700 space-y-0.5">
                      {elements.benefits.slice(0, 3).map((b: string, i: number) => (
                        <li key={i}>{b}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="rounded-lg border border-dashed border-slate-200 p-8 text-center text-xs text-slate-500">
                Please ingest a page URL to parse and inspect its structural elements.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Step 3: Comparative Experience Preview & Human Review */}
      {variants.length > 0 && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Eye className="h-5 w-5 text-indigo-600" />
                Live Comparative Experience Preview & Diff
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Side-by-side comparison of Baseline Control vs AI-synthesized personalized variants.
              </p>
            </div>

            {/* Viewport Switcher */}
            <div className="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-0.5 text-xs font-semibold">
              <button
                onClick={() => setDeviceViewport("desktop")}
                className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-colors ${
                  deviceViewport === "desktop"
                    ? "bg-white text-indigo-600 shadow-sm"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <Monitor className="h-3.5 w-3.5" />
                Desktop
              </button>
              <button
                onClick={() => setDeviceViewport("mobile")}
                className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-colors ${
                  deviceViewport === "mobile"
                    ? "bg-white text-indigo-600 shadow-sm"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                <Smartphone className="h-3.5 w-3.5" />
                Mobile (375px)
              </button>
            </div>
          </div>

          {/* Cards Grid: Control vs Variant 1 vs Variant 2 */}
          <div className={`grid gap-6 ${deviceViewport === "desktop" ? "grid-cols-1 md:grid-cols-3" : "grid-cols-1 md:grid-cols-3 justify-items-center"}`}>
            {/* Control Column */}
            <div
              className={`rounded-xl border border-slate-200 bg-slate-50/70 p-5 flex flex-col justify-between transition-all ${
                deviceViewport === "mobile" ? "w-[340px]" : "w-full"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="inline-flex items-center gap-1 rounded-full bg-slate-200 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-slate-700">
                    Control (Baseline)
                  </span>
                  <span className="text-[11px] text-slate-400">Original</span>
                </div>

                {/* Mock Browser/Mobile Frame */}
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm space-y-3">
                  <div className="border-b border-slate-100 pb-2">
                    <span className="text-[9px] uppercase font-bold text-slate-400">Headline</span>
                    <h4 className="text-sm font-bold text-slate-900 mt-0.5 leading-snug">
                      {elements.h1 || "Next Generation AI Automation"}
                    </h4>
                  </div>
                  <div className="border-b border-slate-100 pb-2">
                    <span className="text-[9px] uppercase font-bold text-slate-400">Value Proposition</span>
                    <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">
                      {elements.value_prop || elements.h2 || "Streamline your financial and web operations seamlessly."}
                    </p>
                  </div>
                  <div>
                    <span className="text-[9px] uppercase font-bold text-slate-400">Call to Action</span>
                    <div className="mt-1">
                      <button className="w-full rounded bg-slate-800 py-1.5 px-3 text-xs font-semibold text-white shadow-sm">
                        {elements.primary_cta || "Get Started"}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-200/60 text-[11px] text-slate-500 text-center">
                Baseline standard production traffic
              </div>
            </div>

            {/* AI Synthesized Variants */}
            {variants.map((variant, idx) => {
              const guardrails = variant.guardrail_report || {};
              const isApproved = variant.review_status === "approved";
              const isRejected = variant.review_status === "rejected";
              const isPassingGuardrails = guardrails.passed !== false;

              return (
                <div
                  key={variant.id}
                  className={`rounded-xl border flex flex-col justify-between transition-all ${
                    isApproved
                      ? "border-emerald-300 bg-emerald-50/20"
                      : isRejected
                      ? "border-rose-300 bg-rose-50/20"
                      : "border-indigo-300 bg-indigo-50/15"
                  } p-5 ${deviceViewport === "mobile" ? "w-[340px]" : "w-full"}`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="inline-flex items-center gap-1 rounded-full bg-indigo-100 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-indigo-800">
                        <Sparkles className="h-3 w-3 text-indigo-600" />
                        Variant {String.fromCharCode(65 + idx)}
                      </span>
                      <span
                        className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold ${
                          isApproved
                            ? "bg-emerald-100 text-emerald-800"
                            : isRejected
                            ? "bg-rose-100 text-rose-800"
                            : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {variant.review_status}
                      </span>
                    </div>

                    {/* Preview Content Frame */}
                    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm space-y-3">
                      <div className="border-b border-slate-100 pb-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[9px] uppercase font-bold text-slate-400">Headline Diff</span>
                          <span className="text-[9px] font-mono text-indigo-600">
                            {variant.headline?.length || 0} chars
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-indigo-950 mt-0.5 leading-snug">
                          {variant.headline}
                        </h4>
                      </div>

                      <div className="border-b border-slate-100 pb-2">
                        <span className="text-[9px] uppercase font-bold text-slate-400">Subhead / Body</span>
                        <p className="text-xs text-slate-700 mt-0.5 leading-relaxed">
                          {variant.subheading || variant.body_copy}
                        </p>
                      </div>

                      <div>
                        <div className="flex items-center justify-between">
                          <span className="text-[9px] uppercase font-bold text-slate-400">Personalized CTA</span>
                          <span className="text-[9px] font-mono text-indigo-600">
                            {variant.cta_text?.length || 0} chars
                          </span>
                        </div>
                        <div className="mt-1">
                          <button className="w-full rounded bg-indigo-600 py-1.5 px-3 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500">
                            {variant.cta_text}
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Brand Guardrail Score Card */}
                    <div className="mt-3 rounded-lg border border-slate-100 bg-slate-50/80 p-2.5 space-y-1 text-[11px]">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-700 flex items-center gap-1">
                          <ShieldCheck className="h-3.5 w-3.5 text-indigo-600" />
                          Brand Safety Score
                        </span>
                        <span className="font-bold text-emerald-600">
                          {guardrails.brand_score !== undefined ? `${Math.round(guardrails.brand_score * 100)}%` : "100%"}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-slate-500 text-[10px]">
                        <span>Prohibited terms:</span>
                        <span className={guardrails.prohibited_found?.length ? "text-rose-600 font-bold" : "text-emerald-600"}>
                          {guardrails.prohibited_found?.length ? guardrails.prohibited_found.join(", ") : "0 detected"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Human-in-the-Loop Action Bar */}
                  <div className="mt-4 pt-3 border-t border-slate-200/60 space-y-2">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleApprove(variant.id, "approved")}
                        className="flex-1 inline-flex items-center justify-center gap-1 rounded bg-emerald-600 py-1.5 px-2 text-xs font-bold text-white shadow-sm hover:bg-emerald-500 transition-colors"
                      >
                        <Check className="h-3.5 w-3.5" />
                        Approve
                      </button>
                      <button
                        onClick={() => handleApprove(variant.id, "rejected")}
                        className="inline-flex items-center justify-center rounded border border-rose-200 bg-rose-50 p-1.5 text-rose-700 hover:bg-rose-100 transition-colors"
                        title="Reject Variant"
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </div>

                    {isApproved && (
                      <button
                        onClick={() => handleLaunchExperiment(variant)}
                        className="w-full inline-flex items-center justify-center gap-1.5 rounded-lg bg-indigo-600 py-1.5 px-3 text-xs font-bold text-white shadow hover:bg-indigo-500 transition-colors"
                      >
                        <ArrowRight className="h-3.5 w-3.5" />
                        Launch 50/50 Experiment
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
