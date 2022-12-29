"""Stores defaults"""
from __future__ import annotations


def allowed_actions() -> list[str]:
    """Return a list of allowed actions."""
    return ["all", "prepare", "generalize", "qc"]


def default_log_level() -> str:
    """Return default log level."""
    return "WARNING"


def log_levels() -> list[str]:
    """Return a list of log levels."""
    return ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def default_model() -> str:
    """Return default model."""
    return "1to6"


def available_models() -> list[str]:
    """Return a list of available models."""
    return [
        "1_guided_fixations",
        "2_pursuit",
        "3_openclosed",
        "3_pursuit",
        "4_pursuit",
        "5_free_viewing",
        "1to5",
        "1to6",
    ]
