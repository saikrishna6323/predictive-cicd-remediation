"""Remediation generation module (patent ref: 112).

Generates candidate fixes based on predicted root cause.
"""
from __future__ import annotations
from dataclasses import dataclass
from src.prediction.predictor import Prediction

@dataclass
class Remediation:
    root_cause: str
    description: str
    patch: str
    patch_target: str


TEMPLATES = {
    "dependency_resolution": Remediation(
        root_cause="dependency_resolution",
        description="Pin conflicting dependency to last known-good version and add resolver constraint.",
        patch="{package}=={last_known_good_version}\n",
        patch_target="requirements.txt",
    ),
    "timeout": Remediation(
        root_cause="timeout",
        description="Increase step timeout and add retry with exponential backoff.",
        patch="timeout-minutes: {new_timeout}\n",
        patch_target=".github/workflows/*.yml",
    ),
    "oom": Remediation(
        root_cause="oom",
        description="Increase runner memory allocation or split job into smaller matrix jobs.",
        patch="runs-on: ubuntu-latest-4-cores\n",
        patch_target=".github/workflows/*.yml",
    ),
    "flaky_network": Remediation(
        root_cause="flaky_network",
        description="Add retry-on-failure wrapper around network-dependent step.",
        patch="uses: nick-fields/retry@v3\nwith:\n  timeout_minutes: 5\n  max_attempts: 3\n",
        patch_target=".github/workflows/*.yml",
    ),
}


def generate_remediation(prediction: Prediction, context: dict) -> Remediation | None:
    template = TEMPLATES.get(prediction.probable_root_cause or "")
    if not template:
        return None
    patch = template.patch.format(**{**context, **_defaults()})
    return Remediation(template.root_cause, template.description, patch, template.patch_target)


def _defaults() -> dict:
    return {
        "package": "unknown-package",
        "last_known_good_version": "0.0.0",
        "new_timeout": 30,
    }
