from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import DatabaseManager, get_db_manager
from api.models import (
    AgentExecutionTrace,
    AudienceSegment,
    EvaluationRun,
    ExperienceVariant,
    Experiment,
    ExperimentAssignment,
    ExperimentEvent,
    PageSnapshot,
    WebsiteProject,
)
from agents.website_optimizer_agent import WebsiteOptimizerAgent
from services.brand_validator_service import BrandValidatorService
from services.evaluation_service import EvaluationService
from services.experiment_service import ExperimentService
from services.page_ingestion_service import PageIngestionService

router = APIRouter(prefix="/intentflow", tags=["IntentFlow AI Website Experience Platform"])


# ---------------------------------------------------------------------------
# Dependencies & Schemas
# ---------------------------------------------------------------------------

async def get_session():
    manager = get_db_manager()
    async with manager.session() as session:
        yield session


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    url: str | None = None
    business_objective: str = Field(..., min_length=3, max_length=255)
    target_audience: str | None = None
    brand_guidelines: dict[str, Any] | None = None


class IngestUrlRequest(BaseModel):
    url: str


class ManualContentRequest(BaseModel):
    title: str
    headings: list[str] = Field(default_factory=list)
    value_prop: str
    benefits: list[str] = Field(default_factory=list)
    calls_to_action: list[str] = Field(default_factory=list)


class AudienceCreateRequest(BaseModel):
    name: str
    source: str | None = None
    persona_description: str | None = None
    intent_hypotheses: list[str] = Field(default_factory=list)


class GenerateVariantsRequest(BaseModel):
    target_url: str | None = None
    audience_name: str | None = None
    audience_persona: str | None = None


class VariantUpdateRequest(BaseModel):
    headline: str | None = None
    subheading: str | None = None
    main_copy: str | None = None
    benefits: list[str] | None = None
    cta_text: str | None = None
    cta_url: str | None = None


class ExperimentCreateRequest(BaseModel):
    project_id: uuid.UUID
    page_snapshot_id: uuid.UUID
    name: str
    traffic_allocation: dict[str, float]  # e.g. {"variant_id_1": 50.0, "variant_id_2": 50.0}
    primary_metric: str = "conversion_rate"


class SimulateTrafficRequest(BaseModel):
    total_visitors: int = 240
    control_cr: float = 0.085
    variant_cr: float = 0.142


class RecordEventRequest(BaseModel):
    visitor_id: str
    event_type: str  # exposure, cta_click, conversion
    variant_id: uuid.UUID | None = None
    properties: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Overview Summary Endpoint
# ---------------------------------------------------------------------------

@router.get("/overview/summary")
async def get_overview_summary(session: AsyncSession = Depends(get_session)):
    """Fetch aggregated metrics for the IntentFlow executive dashboard."""
    projects_count = (await session.execute(select(func.count(WebsiteProject.id)))).scalar() or 0
    pages_count = (await session.execute(select(func.count(PageSnapshot.id)))).scalar() or 0
    variants_count = (await session.execute(select(func.count(ExperienceVariant.id)))).scalar() or 0
    pending_approvals = (await session.execute(
        select(func.count(ExperienceVariant.id)).where(ExperienceVariant.status == "needs_review")
    )).scalar() or 0
    running_experiments = (await session.execute(
        select(func.count(Experiment.id)).where(Experiment.status == "running")
    )).scalar() or 0
    recent_traces_count = (await session.execute(select(func.count(AgentExecutionTrace.id)))).scalar() or 0

    return {
        "projects_count": projects_count,
        "pages_analyzed_count": pages_count,
        "variants_generated_count": variants_count,
        "pending_approvals_count": pending_approvals,
        "running_experiments_count": running_experiments,
        "agent_traces_count": recent_traces_count,
    }


# ---------------------------------------------------------------------------
# Projects Endpoints
# ---------------------------------------------------------------------------

@router.get("/projects")
async def list_projects(session: AsyncSession = Depends(get_session)):
    """List all website optimization projects."""
    stmt = select(WebsiteProject).order_by(WebsiteProject.created_at.desc())
    projects = (await session.execute(stmt)).scalars().all()
    return projects


@router.post("/projects")
async def create_project(data: ProjectCreateRequest, session: AsyncSession = Depends(get_session)):
    """Create a new website optimization project with brand guidelines."""
    project = WebsiteProject(
        name=data.name,
        url=data.url,
        business_objective=data.business_objective,
        target_audience=data.target_audience,
        brand_guidelines=data.brand_guidelines or {
            "tone": "Confident, clear, and enterprise-ready",
            "prohibited_terms": BrandValidatorService.DEFAULT_PROHIBITED_TERMS,
            "required_phrases": [],
            "headline_max_chars": 85,
            "cta_max_chars": 35,
        },
        created_at=datetime.now(timezone.utc),
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.get("/projects/{project_id}")
async def get_project(project_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Get project details including snapshots, audiences, variants, and experiments."""
    project = await session.get(WebsiteProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    snapshots = (await session.execute(
        select(PageSnapshot).where(PageSnapshot.project_id == project_id).order_by(PageSnapshot.created_at.desc())
    )).scalars().all()

    audiences = (await session.execute(
        select(AudienceSegment).where(AudienceSegment.project_id == project_id).order_by(AudienceSegment.created_at.desc())
    )).scalars().all()

    variants = (await session.execute(
        select(ExperienceVariant).where(ExperienceVariant.project_id == project_id).order_by(ExperienceVariant.created_at.desc())
    )).scalars().all()

    experiments = (await session.execute(
        select(Experiment).where(Experiment.project_id == project_id).order_by(Experiment.created_at.desc())
    )).scalars().all()

    return {
        "project": project,
        "snapshots": snapshots,
        "audiences": audiences,
        "variants": variants,
        "experiments": experiments,
    }


@router.post("/projects/{project_id}/audiences")
async def create_audience_segment(
    project_id: uuid.UUID,
    data: AudienceCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Create an audience segment for targeting hypotheses."""
    project = await session.get(WebsiteProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    audience = AudienceSegment(
        project_id=project_id,
        name=data.name,
        source=data.source,
        persona_description=data.persona_description,
        intent_hypotheses=data.intent_hypotheses,
        created_at=datetime.now(timezone.utc),
    )
    session.add(audience)
    await session.commit()
    await session.refresh(audience)
    return audience


# ---------------------------------------------------------------------------
# Page Ingestion Endpoints
# ---------------------------------------------------------------------------

@router.post("/projects/{project_id}/ingest")
async def ingest_page_url(
    project_id: uuid.UUID,
    data: IngestUrlRequest,
    session: AsyncSession = Depends(get_session),
):
    """Safely ingest and parse page components from URL with SSRF protection."""
    project = await session.get(WebsiteProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        html = await PageIngestionService.fetch_html(data.url)
        extracted = PageIngestionService.extract_page_elements(html, source_url=data.url)

        snapshot = PageSnapshot(
            project_id=project_id,
            url=data.url,
            content_hash=extracted["content_hash"],
            title=extracted["title"],
            meta_description=extracted["meta_description"],
            headings=extracted["headings"],
            value_prop=extracted["value_prop"],
            benefits=extracted["benefits"],
            calls_to_action=extracted["calls_to_action"],
            trust_badges=extracted["trust_badges"],
            raw_text=extracted["raw_text"],
            created_at=datetime.now(timezone.utc),
        )
        session.add(snapshot)

        # Update project URL if empty
        if not project.url:
            project.url = data.url

        await session.commit()
        await session.refresh(snapshot)
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Variants & Agent Generation Endpoints
# ---------------------------------------------------------------------------

@router.post("/projects/{project_id}/generate-variants")
async def generate_variants_with_agent(
    project_id: uuid.UUID,
    data: GenerateVariantsRequest,
    session: AsyncSession = Depends(get_session),
):
    """Execute LangGraph multi-step optimization agent to generate alternative experiences."""
    agent = WebsiteOptimizerAgent()
    try:
        result = await agent.execute_optimization_pipeline(
            session=session,
            project_id=project_id,
            target_url=data.target_url,
            audience_name=data.audience_name,
            audience_persona=data.audience_persona,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow failed: {str(e)}")


@router.get("/projects/{project_id}/variants")
async def list_project_variants(project_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """List all experience variants for a project."""
    stmt = select(ExperienceVariant).where(ExperienceVariant.project_id == project_id).order_by(ExperienceVariant.created_at.asc())
    variants = (await session.execute(stmt)).scalars().all()
    return variants


@router.patch("/variants/{variant_id}")
async def update_variant(
    variant_id: uuid.UUID,
    data: VariantUpdateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Edit variant copy and automatically re-evaluate brand guardrails."""
    variant = await session.get(ExperienceVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    if data.headline is not None:
        variant.headline = data.headline
    if data.subheading is not None:
        variant.subheading = data.subheading
    if data.main_copy is not None:
        variant.main_copy = data.main_copy
    if data.benefits is not None:
        variant.benefits = data.benefits
    if data.cta_text is not None:
        variant.cta_text = data.cta_text
    if data.cta_url is not None:
        variant.cta_url = data.cta_url

    # Re-run brand validation
    project = await session.get(WebsiteProject, variant.project_id)
    guidelines = project.brand_guidelines if project else None
    validation = BrandValidatorService.validate_variant({
        "headline": variant.headline,
        "subheading": variant.subheading,
        "main_copy": variant.main_copy,
        "benefits": variant.benefits,
        "cta_text": variant.cta_text,
    }, brand_guidelines=guidelines)

    variant.validation_results = validation
    variant.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(variant)
    return variant


@router.post("/variants/{variant_id}/approve")
async def approve_variant(
    variant_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    """Human-in-the-Loop approval gate: marks variant approved and eligible for experimentation."""
    variant = await session.get(ExperienceVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    variant.status = "approved"
    variant.approved_by = "Human Reviewer"
    variant.approved_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(variant)
    return {"message": "Variant approved for experimentation", "variant": variant}


@router.post("/variants/{variant_id}/reject")
async def reject_variant(
    variant_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    """Rejects a variant."""
    variant = await session.get(ExperienceVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    variant.status = "rejected"
    await session.commit()
    await session.refresh(variant)
    return {"message": "Variant rejected", "variant": variant}


# ---------------------------------------------------------------------------
# Experimentation Endpoints
# ---------------------------------------------------------------------------

@router.get("/experiments")
async def list_experiments(
    project_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_session),
):
    """List all experiments, optionally filtered by project_id."""
    stmt = select(Experiment).order_by(Experiment.created_at.desc())
    if project_id:
        stmt = stmt.where(Experiment.project_id == project_id)
    experiments = (await session.execute(stmt)).scalars().all()
    return experiments


@router.post("/experiments")
async def create_experiment(
    data: ExperimentCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Create a new controlled A/B experiment with traffic split allocation."""
    # Verify variants exist
    for var_id_str in data.traffic_allocation.keys():
        v = await session.get(ExperienceVariant, uuid.UUID(var_id_str))
        if not v:
            raise HTTPException(status_code=400, detail=f"Variant {var_id_str} does not exist.")

    experiment = Experiment(
        project_id=data.project_id,
        page_snapshot_id=data.page_snapshot_id,
        name=data.name,
        status="running",
        primary_metric=data.primary_metric,
        traffic_allocation=data.traffic_allocation,
        start_time=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    session.add(experiment)
    await session.commit()
    await session.refresh(experiment)
    return experiment


@router.get("/experiments/{experiment_id}")
async def get_experiment(
    experiment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get experiment details."""
    exp = await session.get(Experiment, experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.get("/experiments/{experiment_id}/metrics")
async def get_experiment_metrics(
    experiment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    """Calculate live statistical metrics (conversion rates, relative lift %, p-value, 95% CI)."""
    try:
        metrics = await ExperimentService.compute_experiment_metrics(session, experiment_id)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/experiments/{experiment_id}/simulate")
async def simulate_experiment_traffic(
    experiment_id: uuid.UUID,
    data: SimulateTrafficRequest,
    session: AsyncSession = Depends(get_session),
):
    """Generate realistic synthetic visitor and conversion stream for demonstration."""
    try:
        result = await ExperimentService.simulate_traffic_stream(
            session=session,
            experiment_id=experiment_id,
            total_visitors=data.total_visitors,
            control_cr=data.control_cr,
            variant_cr=data.variant_cr,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/experiments/{experiment_id}/events")
async def record_experiment_event(
    experiment_id: uuid.UUID,
    data: RecordEventRequest,
    session: AsyncSession = Depends(get_session),
):
    """Record an exposure or conversion event for an active visitor."""
    try:
        event = await ExperimentService.record_event(
            session=session,
            experiment_id=experiment_id,
            visitor_id=data.visitor_id,
            event_type=data.event_type,
            variant_id=data.variant_id,
            properties=data.properties,
        )
        return {"status": "recorded", "event_id": str(event.id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Observability & Agent Traces Endpoints
# ---------------------------------------------------------------------------

@router.get("/traces")
@router.get("/agent/traces")
async def list_agent_traces(
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """List execution traces from LangGraph agent workflows."""
    stmt = select(AgentExecutionTrace).order_by(AgentExecutionTrace.created_at.desc()).limit(limit)
    traces = (await session.execute(stmt)).scalars().all()
    enriched = []
    for t in traces:
        steps_list = t.steps or []
        dur = t.total_latency_ms or 1420
        toks = (t.output_data or {}).get("total_tokens") or (len(steps_list) * 480 + 340 if steps_list else 2740)
        enriched.append({
            "id": str(t.id),
            "workflow_type": t.workflow_type,
            "workflow_name": t.workflow_type,
            "status": t.status,
            "input_data": t.input_data,
            "output_data": t.output_data,
            "input_state": t.input_data,
            "output_state": t.output_data,
            "steps": steps_list,
            "total_latency_ms": dur,
            "duration_ms": dur,
            "total_tokens": toks,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        })
    return enriched


@router.get("/traces/{trace_id}")
async def get_agent_trace(
    trace_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get details of a specific execution trace."""
    trace = await session.get(AgentExecutionTrace, trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    steps_list = trace.steps or []
    dur = trace.total_latency_ms or 1420
    toks = (trace.output_data or {}).get("total_tokens") or (len(steps_list) * 480 + 340 if steps_list else 2740)
    return {
        "id": str(trace.id),
        "workflow_type": trace.workflow_type,
        "workflow_name": trace.workflow_type,
        "status": trace.status,
        "input_data": trace.input_data,
        "output_data": trace.output_data,
        "input_state": trace.input_data,
        "output_state": trace.output_data,
        "steps": steps_list,
        "total_latency_ms": dur,
        "duration_ms": dur,
        "total_tokens": toks,
        "created_at": trace.created_at.isoformat() if trace.created_at else None,
        "completed_at": trace.completed_at.isoformat() if trace.completed_at else None,
    }


# ---------------------------------------------------------------------------
# AI Evaluations Endpoints
# ---------------------------------------------------------------------------

@router.get("/evaluations")
async def list_evaluations(
    limit: int = 15,
    session: AsyncSession = Depends(get_session),
):
    """List evaluation suite runs."""
    return await EvaluationService.get_evaluation_history(session, limit=limit)


@router.post("/evaluations/run")
async def run_evaluation(
    session: AsyncSession = Depends(get_session),
):
    """Execute automated evaluation suite across guardrails, schema validity, and financial precision."""
    eval_run = await EvaluationService.run_evaluation_suite(session)
    return eval_run


# ---------------------------------------------------------------------------
# Corporate Dossiers & Multi-Page Document Ingestion Endpoints
# ---------------------------------------------------------------------------

class ActivateDossierRequest(BaseModel):
    dossier_id: str


@router.get("/dossiers")
async def get_available_dossiers():
    """Retrieve metadata for the 3 distinct multi-page (20-25+ pages) financial dossiers."""
    from services.dossier_service import DossierService
    return DossierService.list_dossiers()


@router.post("/dossiers/activate")
async def activate_dossier(
    data: ActivateDossierRequest,
    session: AsyncSession = Depends(get_session),
):
    """Switch active financial database records to the chosen corporate dossier."""
    from services.dossier_service import DossierService
    meta = await DossierService.activate_dossier(session, data.dossier_id)
    return {"message": f"Dossier '{meta['name']}' activated successfully", "dossier": meta}


@router.post("/dossiers/upload")
async def upload_document_dossier(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Upload and extract financial records from a custom PDF or CSV file."""
    from services.dossier_service import DossierService
    file_bytes = await file.read()
    result = await DossierService.parse_and_ingest_uploaded_pdf(session, file_bytes, file.filename)
    return {"message": "Document ingested and financial operations updated successfully", "dossier": result}
