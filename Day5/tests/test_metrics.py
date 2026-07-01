"""Tests for api/metrics.py."""

from api.metrics import get_system_metrics


def test_get_system_metrics_has_expected_fields():
    result = get_system_metrics()
    assert "cpu_percent" in result
    assert "memory_percent" in result
    assert "disk_percent" in result


def test_get_system_metrics_values_are_percentages():
    result = get_system_metrics()
    for key in ("cpu_percent", "memory_percent", "disk_percent"):
        assert 0 <= result[key] <= 100
