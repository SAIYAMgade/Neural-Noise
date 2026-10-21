import re

with open('api/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

models_code = '''

# ---------------------------------------------------------------------------
# IntentFlow AI Models (Website Personalization & Experimentation Engine)
# ---------------------------------------------------------------------------

class WebsiteProject(Base):
    """A website optimization project."""
    __tablename__ = "website_projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    business_objective: Mapped[str] = mapped_column(String(255), nullable=False)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand_guidelines: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    page_snapshots: Mapped[list["PageSnapshot"]] = relationship("PageSnapshot", back_populates="project", cascade="all, delete-orphan")
    audience_segments: Mapped[list["AudienceSegment"]] = relationship("AudienceSegment", back_populates="project", cascade="all, delete-orphan")
    variants: Mapped[list["ExperienceVariant"]] = relationship("ExperienceVariant", back_populates="project", cascade="all, delete-orphan")
    experiments: Mapped[list["Experiment"]] = relationship("Experiment", back_populates="project", cascade="all, delete-orphan")


class PageSnapshot(Base):
    """Ingested page snapshot with structured content components."""
    __tablename__ = "page_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("website_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    headings: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    value_prop: Mapped[str | None] = mapped_column(Text, nullable=True)
    benefits: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    calls_to_action: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    trust_badges: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["WebsiteProject"] = relationship("WebsiteProject", back_populates="page_snapshots")
    variants: Mapped[list["ExperienceVariant"]] = relationship("ExperienceVariant", back_populates="page_snapshot", cascade="all, delete-orphan")


class AudienceSegment(Base):
    """Audience persona and campaign intent definition."""
    __tablename__ = "audience_segments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("website_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    persona_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    intent_hypotheses: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["WebsiteProject"] = relationship("WebsiteProject", back_populates="audience_segments")
    variants: Mapped[list["ExperienceVariant"]] = relationship("ExperienceVariant", back_populates="audience_segment")


class ExperienceVariant(Base):
    """AI-generated alternative page experience with brand guardrails."""
    __tablename__ = "experience_variants"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("website_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    page_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("page_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    audience_segment_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("audience_segments.id", ondelete="SET NULL"), nullable=True)
    variant_name: Mapped[str] = mapped_column(String(100), nullable=False)
    headline: Mapped[str] = mapped_column(String(512), nullable=False)
    subheading: Mapped[str | None] = mapped_column(Text, nullable=True)
    main_copy: Mapped[str | None] = mapped_column(Text, nullable=True)
    benefits: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    cta_text: Mapped[str] = mapped_column(String(100), nullable=False)
    cta_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    validation_results: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["WebsiteProject"] = relationship("WebsiteProject", back_populates="variants")
    page_snapshot: Mapped["PageSnapshot"] = relationship("PageSnapshot", back_populates="variants")
    audience_segment: Mapped["AudienceSegment | None"] = relationship("AudienceSegment", back_populates="variants")


class Experiment(Base):
    """A/B or multi-variant live experiment."""
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("website_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    page_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("page_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    primary_metric: Mapped[str] = mapped_column(String(100), nullable=False, default="conversion_rate")
    traffic_allocation: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["WebsiteProject"] = relationship("WebsiteProject", back_populates="experiments")
    assignments: Mapped[list["ExperimentAssignment"]] = relationship("ExperimentAssignment", back_populates="experiment", cascade="all, delete-orphan")
    events: Mapped[list["ExperimentEvent"]] = relationship("ExperimentEvent", back_populates="experiment", cascade="all, delete-orphan")


class ExperimentAssignment(Base):
    """Sticky visitor assignment to a variant."""
    __tablename__ = "experiment_assignments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    visitor_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    variant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("experience_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="assignments")


class ExperimentEvent(Base):
    """Granular event collected during experiment execution."""
    __tablename__ = "experiment_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    visitor_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    variant_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("experience_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    properties: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="events")


class AgentExecutionTrace(Base):
    """Full execution trace of LangGraph agent workflows."""
    __tablename__ = "agent_execution_traces"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workflow_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    input_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    output_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    steps: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    total_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class EvaluationRun(Base):
    """Automated evaluation run measuring agent quality, guardrails, and correctness."""
    __tablename__ = "evaluation_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    suite_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, default="rule_based_deterministic_evaluator")
    total_cases: Mapped[int] = mapped_column(Integer, nullable=False)
    passed_cases: Mapped[int] = mapped_column(Integer, nullable=False)
    failed_cases: Mapped[int] = mapped_column(Integer, nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    details: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
'''

all_idx = text.find('__all__ = [')
if all_idx != -1:
    before_all = text[:all_idx].rstrip()
    updated_all = '''__all__ = [
    "WebsiteProject",
    "PageSnapshot",
    "AudienceSegment",
    "ExperienceVariant",
    "Experiment",
    "ExperimentAssignment",
    "ExperimentEvent",
    "AgentExecutionTrace",
    "EvaluationRun",
    "Client",
    "Invoice",
    "InvoiceLineItem",
    "Payment",
    "PaymentAllocation",
    "Expense",
    "AIConversation",
    "AIMessage",
    "ApprovalRequest",
    "AuditEvent",
    "IdempotencyRecord",
    "Base",
    "RawFinancial",
    "KPISnapshot",
    "Anomaly",
    "MarketSignal",
    "Report",
    "Integration",
    "SyncLog",
    "CashBalance",
    "CommittedExpense",
    "CashFlowForecast",
    "Contract",
    "DeferredRevenueSchedule",
    "BoardDeck",
    "SavedScenario",
    "FraudAlert",
    "CustomerProfile",
    "AgentObservation",
    "AgentPlan",
    "AgentAction",
]'''
    new_text = before_all + '\n' + models_code + '\n\n' + updated_all + '\n'
else:
    new_text = text + '\n' + models_code

with open('api/models.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Updated api/models.py successfully")
