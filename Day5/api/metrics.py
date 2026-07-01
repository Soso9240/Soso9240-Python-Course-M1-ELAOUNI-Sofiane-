"""System metrics collection using psutil."""

import psutil


def get_system_metrics() -> dict:
    """Return a snapshot of current CPU, memory, and disk usage.

    Uses interval=None for cpu_percent so the call is non-blocking
    (it compares against the last call instead of sleeping).
    """
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }
