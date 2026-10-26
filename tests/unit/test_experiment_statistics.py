import uuid
import pytest
from services.experiment_service import ExperimentService, normal_cdf


def test_deterministic_visitor_assignment_stickiness():
    """Verify that the same visitor ID always receives the exact same variant across requests."""
    exp_id = uuid.uuid4()
    allocation = {
        "variant_control": 50,
        "variant_test_a": 50,
    }

    visitor_1 = "visitor_abc_123"
    visitor_2 = "visitor_xyz_789"

    # Repeated calls must yield identical assignments
    assignment_1_run1 = ExperimentService.assign_variant(exp_id, visitor_1, allocation)
    assignment_1_run2 = ExperimentService.assign_variant(exp_id, visitor_1, allocation)
    assignment_1_run3 = ExperimentService.assign_variant(exp_id, visitor_1, allocation)
    assert assignment_1_run1 == assignment_1_run2 == assignment_1_run3

    assignment_2_run1 = ExperimentService.assign_variant(exp_id, visitor_2, allocation)
    assignment_2_run2 = ExperimentService.assign_variant(exp_id, visitor_2, allocation)
    assert assignment_2_run1 == assignment_2_run2


def test_normal_cdf_approximation():
    """Verify accuracy of the standard normal error function CDF approximation."""
    assert abs(normal_cdf(0.0) - 0.5) < 1e-4
    assert abs(normal_cdf(1.96) - 0.975) < 1e-3
    assert abs(normal_cdf(-1.96) - 0.025) < 1e-3
