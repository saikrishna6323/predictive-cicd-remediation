# Adoption Guide

This guide explains how a team can adopt **predictive-cicd-remediation** in an existing CI/CD environment, and how the implementation maps to the architecture described in the underlying patent filing.

## Patent Reference

This project is a working prototype of the system described in:

- **Title:** A System and Method for Predictive CI/CD Failure Prevention and Automated Remediation Using Large Language Models
- **Application No.:** 202641038921 (India)
- **Filed:** March 29, 2026
- **Published:** April 10, 2026
- **Inventor:** Sivasaikrishna Suryadevara

The code in this repository is a reference implementation, not the patent document itself. Module boundaries below are named to mirror the patent's System 100 diagram for traceability, not as a claim that this exact code is part of the filed application.

## Module-to-Code Mapping

| Patent Module | Reference No. | Code Location |
|---|---|---|
| Data Ingestion Module | 102 | `src/features/feature_extractor.py` (ingestion helpers) |
| Preprocessing Module | 104 | `src/features/feature_extractor.py` |
| Feature Extraction Module | 106 | `src/features/feature_extractor.py` |
| Predictive Analysis Module | 108 | `src/prediction/predictor.py` |
| Remediation Generation Module | 112 | `src/remediation/remediation_generator.py` |
| Validation Module | 114 | `src/validation/sandbox_validator.py` |
| Automated Execution Module | 116 | `src/execution/executor.py` |
| Feedback Module | 118 | `src/feedback/feedback_store.py` |
| User Interface | 120 | `src/interface/api.py` |

## Adoption Stages

### Stage 1 — Shadow mode (read-only)
Run the pipeline analyzer against historical CI/CD logs without allowing it to take any remediation action. This validates prediction quality (module 108) against your own pipeline's failure history before trusting any automated step.

1. Install dependencies: `pip install -r requirements.txt`
2. Point `feature_extractor.py` at exported logs from your CI system (see `examples/sample_failing_workflow.yml` for the expected shape of a run record).
3. Review predictions and root-cause output manually; no remediation is generated or executed in this stage.

### Stage 2 — Suggest-only remediation
Enable the remediation generator (module 112) so it proposes fixes, but keep automated execution (module 116) disabled. A human reviews and applies suggested changes manually.

### Stage 3 — Sandbox-validated automation
Enable the validation module (114) so proposed remediations are tested in an isolated sandbox before being surfaced. Automated execution remains off; only validated suggestions are shown via the interface module (120).

### Stage 4 — Full automation with feedback loop
Enable automated execution (116) for low-risk, validated remediation classes only, and connect the feedback module (118) so outcomes (success/failure of an applied fix) feed back into future predictions.

## Integration Points

- **CI system:** GitHub Actions is the default target for the example workflows in `examples/`, but the ingestion layer accepts any structured log/build-metadata format, so other CI systems (Jenkins, GitLab CI, CircleCI) can be adapted by writing a small parser into `feature_extractor.py`.
- **Predictor backend:** `src/prediction/predictor.py` ships with a local heuristic/embedding baseline that requires no external API key, and is designed to be swapped for a hosted LLM by implementing the same interface.
- **Storage:** `src/feedback/feedback_store.py` uses a simple local store by default; swap in a database-backed implementation for multi-team or production use.

## Recommended Rollout Checklist

- [ ] Run Stage 1 against at least 4-6 weeks of historical pipeline data to establish a prediction-quality baseline.
- [ ] Get sign-off from the team owning the CI/CD pipeline before enabling Stage 2 suggestions.
- [ ] Define which remediation classes are "low risk" before enabling any automated execution in Stage 4.
- [ ] Set up monitoring/alerting on the feedback module so a spike in failed auto-remediations is caught quickly.

## Questions or Contributions

Issues and pull requests are welcome. If you adopt this project as part of an internal CI/CD pipeline, feel free to open a discussion describing your setup — real-world adoption notes are useful for improving the reference implementation.
