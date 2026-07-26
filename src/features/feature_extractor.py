"""Feature extraction module (patent ref: 106).

Extracts contextual and temporal features from normalized pipeline records:
error signatures, dependency relationships, and execution patterns.
"""
from __future__ import annotations
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

ERROR_PATTERNS = {
    "dependency_resolution": re.compile(r"(ResolutionImpossible|ERESOLVE|version conflict)", re.I),
    "timeout": re.compile(r"(timed? ?out|ETIMEDOUT|context deadline exceeded)", re.I),
    "test_failure": re.compile(r"(AssertionError|FAILED|test.*failed)", re.I),
    "oom": re.compile(r"(OutOfMemory|OOMKilled|killed.*memory)", re.I),
    "auth": re.compile(r"(401 Unauthorized|403 Forbidden|authentication failed)", re.I),
    "flaky_network": re.compile(r"(connection reset|ECONNRESET|network is unreachable)", re.I),
}


@dataclass
class PipelineFeatures:
    step_name: str
    error_signature: str | None
    dependency_files_touched: list[str]
    rolling_failure_rate: float
    recent_error_counts: dict[str, int] = field(default_factory=dict)


def detect_error_signature(log_text: str) -> str | None:
    for label, pattern in ERROR_PATTERNS.items():
        if pattern.search(log_text):
            return label
    return None


def rolling_failure_rate(history: Iterable[dict], step_name: str, window: int = 20) -> float:
    """Fraction of the last `window` runs of a given step that failed."""
    runs = [r for r in history if r.get("step_name") == step_name][-window:]
    if not runs:
        return 0.0
    failures = sum(1 for r in runs if r.get("conclusion") == "failure")
    return failures / len(runs)


def extract_dependency_files(commit_files: list[str]) -> list[str]:
    dep_patterns = ("requirements.txt", "package.json", "package-lock.json",
                    "poetry.lock", "pyproject.toml", "go.mod", "pom.xml")
    return [f for f in commit_files if f.endswith(dep_patterns)]


def extract_features(run_record: dict, history: list[dict]) -> PipelineFeatures:
    log_text = run_record.get("log_text", "")
    step_name = run_record.get("step_name", "unknown")
    signature = detect_error_signature(log_text)
    dep_files = extract_dependency_files(run_record.get("changed_files", []))
    rate = rolling_failure_rate(history, step_name)
    recent = Counter(
        detect_error_signature(r.get("log_text", "")) or "none"
        for r in history[-20:]
    )
    return PipelineFeatures(
        step_name=step_name,
        error_signature=signature,
        dependency_files_touched=dep_files,
        rolling_failure_rate=rate,
        recent_error_counts=dict(recent),
    )
