"""Predictive analysis module (patent ref: 108).

Estimates failure likelihood and probable root cause from extracted features.
Uses a pluggable backend: local heuristic baseline, or an LLM if configured.
"""
from __future__ import annotations
from dataclasses import dataclass
from src.features.feature_extractor import PipelineFeatures

ROOT_CAUSE_WEIGHTS = {
    "dependency_resolution": 0.85,
    "timeout": 0.6,
    "oom": 0.75,
    "auth": 0.5,
    "flaky_network": 0.55,
    "test_failure": 0.7,
}


@dataclass
class Prediction:
    failure_probability: float
    probable_root_cause: str | None
    rationale: str


class BaselinePredictor:
    """Deterministic local baseline: no external API required."""

    def predict(self, features: PipelineFeatures) -> Prediction:
        base = ROOT_CAUSE_WEIGHTS.get(features.error_signature or "", 0.1)
        # Blend with historical rolling failure rate for this step.
        probability = min(0.98, 0.5 * base + 0.5 * features.rolling_failure_rate
                           + (0.15 if features.dependency_files_touched else 0))
        rationale = (
            f"Detected signature='{features.error_signature}', "
            f"rolling_failure_rate={features.rolling_failure_rate:.2f}, "
            f"dependency_files_changed={features.dependency_files_touched}"
        )
        return Prediction(probability, features.error_signature, rationale)


class LLMPredictor:
    """Optional LLM-backed predictor. Requires an API client to be injected."""

    def __init__(self, client, fallback: BaselinePredictor | None = None):
        self.client = client
        self.fallback = fallback or BaselinePredictor()

    def predict(self, features: PipelineFeatures) -> Prediction:
        try:
            prompt = self._build_prompt(features)
            response = self.client.complete(prompt)
            return self._parse_response(response, features)
        except Exception:
            return self.fallback.predict(features)

    def _build_prompt(self, features: PipelineFeatures) -> str:
        return (
            "You are a CI/CD failure analysis assistant. Given these pipeline "
            f"features: {features}, estimate a failure probability (0-1) and "
            "the most probable root cause. Respond as 'probability|root_cause|rationale'."
        )

    def _parse_response(self, response: str, features: PipelineFeatures) -> Prediction:
        try:
            prob_str, cause, rationale = response.split("|", 2)
            return Prediction(float(prob_str), cause.strip(), rationale.strip())
        except Exception:
            return self.fallback.predict(features)
