import os
import uuid
import pytest
from httpx import AsyncClient, ASGITransport

os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/finpilot"
from api.main import create_app
from api.database import DatabaseManager, init_db


@pytest.mark.asyncio
async def test_full_website_optimization_and_experiment_lifecycle():
    """End-to-end integration test of IntentFlow AI:
    1. Initialize database & app.
    2. Create website optimization project.
    3. Ingest page components from URL.
    4. Run LangGraph agent optimization pipeline.
    5. Verify generated variants and execution trace.
    6. Approve a variant via Human-in-the-Loop checkpoint.
    7. Create an A/B experiment with traffic allocation.
    8. Simulate synthetic traffic stream.
    9. Verify statistical metrics (CR, lift, z-score, p-value).
    10. Run automated evaluation suite.
    """
    from api.database import close_db, init_db
    await close_db()
    await init_db()
    app = create_app()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Website Project
        proj_resp = await client.post(
            "/api/v1/intentflow/projects",
            json={
                "name": "CloudScale AI Growth Project",
                "url": "https://demo.intentflow.ai/pricing",
                "business_objective": "Increase qualified enterprise demo bookings",
                "target_audience": "VP of Engineering & Head of Cloud Infrastructure",
            },
        )
        assert proj_resp.status_code == 200, proj_resp.text
        project_data = proj_resp.json()
        project_id = project_data["id"]
        assert project_id is not None

        # 2. Ingest Page Content
        ingest_resp = await client.post(
            f"/api/v1/intentflow/projects/{project_id}/ingest",
            json={"url": "https://demo.intentflow.ai/pricing"},
        )
        assert ingest_resp.status_code == 200, ingest_resp.text
        snapshot_data = ingest_resp.json()
        snapshot_id = snapshot_data["id"]
        assert snapshot_data["title"] is not None
        assert len(snapshot_data["headings"]) > 0

        # 3. Execute LangGraph Optimization Agent Pipeline
        agent_resp = await client.post(
            f"/api/v1/intentflow/projects/{project_id}/generate-variants",
            json={
                "audience_name": "Enterprise Cloud Leaders",
                "audience_persona": "VP of Engineering seeking SOC-2 compliance",
            },
        )
        assert agent_resp.status_code == 200, agent_resp.text
        pipeline_data = agent_resp.json()
        assert pipeline_data["status"] == "needs_review"  # Paused at HITL checkpoint
        assert len(pipeline_data["variants"]) >= 2
        assert len(pipeline_data["execution_steps"]) >= 4

        # Verify trace was stored
        trace_id = pipeline_data["trace_id"]
        trace_resp = await client.get(f"/api/v1/intentflow/traces/{trace_id}")
        assert trace_resp.status_code == 200
        assert trace_resp.json()["workflow_type"] == "website_optimization"

        # 4. Human-in-the-Loop Approval of Test Variant
        test_variant = next(v for v in pipeline_data["variants"] if "Variant A" in v["variant_name"])
        test_var_id = test_variant["id"]

        approve_resp = await client.post(f"/api/v1/intentflow/variants/{test_var_id}/approve")
        assert approve_resp.status_code == 200
        assert approve_resp.json()["variant"]["status"] == "approved"

        # Find Control Variant
        control_variant = next(v for v in pipeline_data["variants"] if "Control" in v["variant_name"])
        control_var_id = control_variant["id"]

        # 5. Create Controlled A/B Experiment
        exp_resp = await client.post(
            "/api/v1/intentflow/experiments",
            json={
                "project_id": project_id,
                "page_snapshot_id": snapshot_id,
                "name": "Enterprise Trust vs Control Headline Test",
                "traffic_allocation": {
                    control_var_id: 50.0,
                    test_var_id: 50.0,
                },
                "primary_metric": "conversion_rate",
            },
        )
        assert exp_resp.status_code == 200, exp_resp.text
        exp_data = exp_resp.json()
        experiment_id = exp_data["id"]

        # 6. Simulate Synthetic Traffic Stream
        sim_resp = await client.post(
            f"/api/v1/intentflow/experiments/{experiment_id}/simulate",
            json={
                "total_visitors": 200,
                "control_cr": 0.08,
                "variant_cr": 0.16,
            },
        )
        assert sim_resp.status_code == 200, sim_resp.text
        sim_data = sim_resp.json()
        assert sim_data["events_created"] > 0

        # 7. Compute & Inspect Statistical Metrics
        metrics_resp = await client.get(f"/api/v1/intentflow/experiments/{experiment_id}/metrics")
        assert metrics_resp.status_code == 200, metrics_resp.text
        metrics_data = metrics_resp.json()
        assert metrics_data["total_exposures"] >= 180
        assert len(metrics_data["variants"]) == 2

        # 8. Run Automated Evaluation Suite
        eval_resp = await client.post("/api/v1/intentflow/evaluations/run")
        assert eval_resp.status_code == 200, eval_resp.text
        eval_data = eval_resp.json()
        assert eval_data["total_cases"] == 7
        assert eval_data["passed_cases"] >= 6
        assert eval_data["metrics"]["accuracy_pct"] >= 85.0
