"""Feedback module (patent ref: 118).

Records real-world outcomes of applied remediations to improve future predictions.
"""
from __future__ import annotations
import json
import os
from dataclasses import asdict, dataclass

@dataclass
class FeedbackEntry:
    timestamp: float
    root_cause: str
    predicted_probability: float
    remediation_applied: bool
    outcome_success: bool | None


class FeedbackStore:
    def __init__(self, path: str = "feedback_log.jsonl"):
        self.path = path

    def record(self, entry: FeedbackEntry) -> None:
        with open(self.path, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

    def load_all(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        with open(self.path) as f:
            return [json.loads(line) for line in f if line.strip()]

    def success_rate_by_cause(self) -> dict[str, float]:
        entries = self.load_all()
        by_cause: dict[str, list[bool]] = {}
        for e in entries:
            if e.get("outcome_success") is not None:
                by_cause.setdefault(e["root_cause"], []).append(e["outcome_success"])
        return {k: sum(v) / len(v) for k, v in by_cause.items() if v}
