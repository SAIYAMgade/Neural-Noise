from __future__ import annotations

import hashlib
import math
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import (
    ExperienceVariant,
    Experiment,
    ExperimentAssignment,
    ExperimentEvent,
)


def normal_cdf(z: float) -> float:
    """Standard normal cumulative distribution function (error function approximation)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


class ExperimentService:
    """Experimentation engine with deterministic assignment, event tracking, and statistical hypothesis testing."""

    @staticmethod
    def assign_variant(
        experiment_id: uuid.UUID,
        visitor_id: str,
        traffic_allocation: dict[str, int | float],
    ) -> str:
        """Deterministic hash-based traffic allocation for stable visitor assignment."""
        hash_input = f"{experiment_id}:{visitor_id}".encode("utf-8")
        hash_val = int(hashlib.md5(hash_input).hexdigest(), 16)
        bucket = hash_val % 100  # 0 to 99

        cumulative = 0.0
        sorted_variants = sorted(traffic_allocation.items(), key=lambda x: str(x[0]))
        for var_id_str, pct in sorted_variants:
            cumulative += float(pct)
            if bucket < cumulative:
                return var_id_str

        # Fallback to first variant if rounding edges occur
        return sorted_variants[0][0]

    @staticmethod
    async def get_or_create_assignment(
        session: AsyncSession,
        experiment_id: uuid.UUID,
        visitor_id: str,
    ) -> uuid.UUID:
        """Retrieve existing assigned variant or deterministically compute and persist a new assignment."""
        # 1. Check if visitor already has an assignment for this experiment
        stmt = select(ExperimentAssignment).where(
            ExperimentAssignment.experiment_id == experiment_id,
            ExperimentAssignment.visitor_id == visitor_id,
        )
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if existing:
            return existing.variant_id

        # 2. Load experiment traffic allocation
        exp = await session.get(Experiment, experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found.")

        # Compute deterministic variant ID
        assigned_var_str = ExperimentService.assign_variant(
            experiment_id=experiment_id,
            visitor_id=visitor_id,
            traffic_allocation=exp.traffic_allocation,
        )
        assigned_variant_id = uuid.UUID(assigned_var_str)

        assignment = ExperimentAssignment(
            experiment_id=experiment_id,
            visitor_id=visitor_id,
            variant_id=assigned_variant_id,
            assigned_at=datetime.now(timezone.utc),
        )
        session.add(assignment)
        await session.commit()
        return assigned_variant_id

    @staticmethod
    async def record_event(
        session: AsyncSession,
        experiment_id: uuid.UUID,
        visitor_id: str,
        event_type: str,
        variant_id: uuid.UUID | None = None,
        properties: dict[str, Any] | None = None,
    ) -> ExperimentEvent:
        """Record an experiment event (exposure, cta_click, conversion)."""
        if variant_id is None:
            variant_id = await ExperimentService.get_or_create_assignment(
                session=session,
                experiment_id=experiment_id,
                visitor_id=visitor_id,
            )

        event = ExperimentEvent(
            experiment_id=experiment_id,
            visitor_id=visitor_id,
            variant_id=variant_id,
            event_type=event_type,
            properties=properties or {},
            created_at=datetime.now(timezone.utc),
        )
        session.add(event)
        await session.commit()
        return event

    @staticmethod
    async def compute_experiment_metrics(
        session: AsyncSession,
        experiment_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Calculate statistical metrics: conversion rates, relative lifts, z-scores, p-values, and 95% CIs."""
        exp = await session.get(Experiment, experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found.")

        # Load all variants involved
        variant_ids = [uuid.UUID(k) for k in exp.traffic_allocation.keys()]
        stmt = select(ExperienceVariant).where(ExperienceVariant.id.in_(variant_ids))
        variants = (await session.execute(stmt)).scalars().all()
        variant_map = {str(v.id): v for v in variants}

        # Query exposures and conversions per variant
        results: dict[str, dict[str, Any]] = {}

        for var_id_str in exp.traffic_allocation.keys():
            var_uuid = uuid.UUID(var_id_str)

            # Exposures (distinct visitors exposed to variant)
            stmt_exp = select(func.count(func.distinct(ExperimentEvent.visitor_id))).where(
                ExperimentEvent.experiment_id == experiment_id,
                ExperimentEvent.variant_id == var_uuid,
                ExperimentEvent.event_type.in_(["exposure", "page_view"]),
            )
            exposures = (await session.execute(stmt_exp)).scalar() or 0

            # Conversions (distinct visitors who converted)
            stmt_conv = select(func.count(func.distinct(ExperimentEvent.visitor_id))).where(
                ExperimentEvent.experiment_id == experiment_id,
                ExperimentEvent.variant_id == var_uuid,
                ExperimentEvent.event_type.in_(["conversion", "cta_click"]),
            )
            conversions = (await session.execute(stmt_conv)).scalar() or 0

            conv_rate = (conversions / exposures) if exposures > 0 else 0.0

            results[var_id_str] = {
                "variant_id": var_id_str,
                "variant_name": variant_map.get(var_id_str).variant_name if var_id_str in variant_map else "Variant",
                "is_control": "control" in (variant_map.get(var_id_str).variant_name.lower() if var_id_str in variant_map else ""),
                "exposures": exposures,
                "conversions": conversions,
                "conversion_rate": round(conv_rate * 100, 2),  # percentage
                "raw_cr": conv_rate,
            }

        # Identify Control variant (first one or named "Control")
        control_id_str = None
        for vid, data in results.items():
            if data["is_control"]:
                control_id_str = vid
                break
        if not control_id_str and results:
            control_id_str = list(results.keys())[0]

        control_data = results.get(control_id_str, {})
        n_c = control_data.get("exposures", 0)
        c_c = control_data.get("conversions", 0)
        p_c = control_data.get("raw_cr", 0.0)

        # Compute Comparative Statistical Metrics against Control
        comparisons = []
        for vid, data in results.items():
            n_v = data["exposures"]
            c_v = data["conversions"]
            p_v = data["raw_cr"]

            if vid == control_id_str:
                data["relative_lift_pct"] = 0.0
                data["absolute_difference_pct"] = 0.0
                data["z_score"] = 0.0
                data["p_value"] = 1.0
                data["is_significant"] = False
                data["ci_lower"] = 0.0
                data["ci_upper"] = 0.0
                data["sample_size_warning"] = n_v < 30
                comparisons.append(data)
                continue

            # Absolute & Relative Lift
            abs_diff = p_v - p_c
            rel_lift = (abs_diff / p_c * 100.0) if p_c > 0 else 0.0

            # Two-proportion pooled Z-test
            p_value = 1.0
            z_score = 0.0
            ci_lower = 0.0
            ci_upper = 0.0
            is_significant = False

            if n_c > 0 and n_v > 0:
                p_pool = (c_c + c_v) / (n_c + n_v)
                se_pool = math.sqrt(p_pool * (1.0 - p_pool) * (1.0 / n_c + 1.0 / n_v))
                se_unpooled = math.sqrt((p_c * (1.0 - p_c) / n_c) + (p_v * (1.0 - p_v) / n_v))

                if se_pool > 0:
                    z_score = abs_diff / se_pool
                    # Two-sided p-value
                    p_value = 2.0 * (1.0 - normal_cdf(abs(z_score)))
                    is_significant = p_value < 0.05 and (n_c >= 30 and n_v >= 30)

                # 95% Confidence Interval for difference (1.96 * SE)
                ci_margin = 1.96 * se_unpooled
                ci_lower = round((abs_diff - ci_margin) * 100, 2)
                ci_upper = round((abs_diff + ci_margin) * 100, 2)

            data["relative_lift_pct"] = round(rel_lift, 2)
            data["absolute_difference_pct"] = round(abs_diff * 100, 2)
            data["z_score"] = round(z_score, 3)
            data["p_value"] = round(p_value, 4)
            data["confidence_level_pct"] = round((1.0 - p_value) * 100, 1) if p_value <= 1.0 else 0.0
            data["is_significant"] = is_significant
            data["ci_lower"] = ci_lower
            data["ci_upper"] = ci_upper
            data["sample_size_warning"] = (n_v < 30 or n_c < 30 or c_v < 5 or c_c < 5)

            comparisons.append(data)

        # Overall experiment health & recommendation
        total_exposures = sum(v["exposures"] for v in comparisons)
        total_conversions = sum(v["conversions"] for v in comparisons)

        recommendation = "Continue running experiment to collect sufficient statistical power (minimum 30 exposures per variant)."
        for v in comparisons:
            if not v["is_control"] and v["is_significant"] and v["relative_lift_pct"] > 0:
                recommendation = f"Statistically significant winner identified: {v['variant_name']} with +{v['relative_lift_pct']}% conversion lift (p={v['p_value']}). Recommend graduating to production."
                break

        return {
            "experiment_id": str(experiment_id),
            "experiment_name": exp.name,
            "status": exp.status,
            "primary_metric": exp.primary_metric,
            "total_exposures": total_exposures,
            "total_conversions": total_conversions,
            "control_variant_id": control_id_str,
            "variants": comparisons,
            "recommendation": recommendation,
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    async def simulate_traffic_stream(
        session: AsyncSession,
        experiment_id: uuid.UUID,
        total_visitors: int = 240,
        control_cr: float = 0.085,
        variant_cr: float = 0.142,
    ) -> dict[str, Any]:
        """Generate a realistic, labeled synthetic visitor & conversion stream for demonstration."""
        import random

        exp = await session.get(Experiment, experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found.")

        # Identify control and other variants
        variant_keys = list(exp.traffic_allocation.keys())
        if len(variant_keys) < 2:
            raise ValueError("Experiment must have at least 2 variants for simulation.")

        control_id_str = variant_keys[0]
        test_var_id_str = variant_keys[1]

        # Clear previous synthetic events for clean re-run if desired
        del_stmt = delete(ExperimentEvent).where(ExperimentEvent.experiment_id == experiment_id)
        await session.execute(del_stmt)

        events_created = 0
        conversions_created = 0

        for i in range(total_visitors):
            sim_visitor_id = f"sim_user_{uuid.uuid4().hex[:10]}"
            # Deterministic bucket assignment
            chosen_var_id_str = control_id_str if (i % 2 == 0) else test_var_id_str
            chosen_var_uuid = uuid.UUID(chosen_var_id_str)

            # 1. Record Exposure Event
            exp_event = ExperimentEvent(
                experiment_id=experiment_id,
                visitor_id=sim_visitor_id,
                variant_id=chosen_var_uuid,
                event_type="exposure",
                properties={"source": "synthetic_simulator", "is_synthetic": True},
                created_at=datetime.now(timezone.utc),
            )
            session.add(exp_event)
            events_created += 1

            # 2. Determine Conversion based on simulated CR
            target_cr = control_cr if chosen_var_id_str == control_id_str else variant_cr
            if random.random() < target_cr:
                conv_event = ExperimentEvent(
                    experiment_id=experiment_id,
                    visitor_id=sim_visitor_id,
                    variant_id=chosen_var_uuid,
                    event_type="conversion",
                    properties={"source": "synthetic_simulator", "is_synthetic": True, "goal": "cta_click"},
                    created_at=datetime.now(timezone.utc),
                )
                session.add(conv_event)
                conversions_created += 1

        exp.status = "running"
        await session.commit()

        metrics = await ExperimentService.compute_experiment_metrics(session, experiment_id)
        return {
            "message": f"Successfully simulated {total_visitors} synthetic visitors and {conversions_created} conversions.",
            "events_created": events_created + conversions_created,
            "metrics": metrics,
        }
