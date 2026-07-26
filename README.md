# Predictive CI/CD Failure Prevention & Automated Remediation

A working prototype implementing the system described in Indian Patent Application
No. 202641038921, "A System and Method for Predictive CI/CD Failure Prevention and
Automated Remediation Using Large Language Models" (filed March 29, 2026).

## Architecture

This implements the modules from the patent's System 100:

| Module | Patent Ref | Code |
|---|---|---|
| Data Ingestion | 102 | `src/ingestion/` |
| Preprocessing | 104 | `src/preprocessing/` |
| Feature Extraction | 106 | `src/features/` |
| Predictive Analysis (LLM) | 108 | `src/prediction/` |
| Remediation Generation | 112 | `src/remediation/` |
| Validation | 114 | `src/validation/` |
| Automated Execution | 116 | `src/execution/` |
| Feedback | 118 | `src/feedback/` |
| User Interface | 120 | `src/interface/` |

## How it works

1. `ingestion` pulls recent workflow runs from a GitHub Actions repo via the GitHub API (build logs, step statuses, commit metadata).
2. `preprocessing` normalizes raw logs into structured records.
3. `features` extracts error signatures, dependency relationships, and historical execution patterns (rolling failure rate per step).
4. `prediction` scores failure likelihood and probable root cause. Uses a pluggable backend: a local heuristic/embedding baseline by default, or an LLM (OpenAI/Anthropic/local via Ollama) if an API key is configured.
5. `remediation` generates candidate fixes (dependency pin, retry/backoff config, config patch) as structured diffs.
6. `validation` re-runs the affected step in an isolated Docker sandbox before anything is applied.
7. `execution` opens a pull request with the validated fix (never pushes directly to a protected branch).
8. `feedback` records whether the fix worked, building a dataset for future improvement.
9. `interface` is a small FastAPI + CLI dashboard to review predictions and remediations.

## Quickstart

```bash
pip install -r requirements.txt
export GITHUB_TOKEN=your_token
export GITHUB_REPO=owner/repo
python -m src.interface.api
```

See `examples/` for a worked example using a sample workflow with an intentional flaky-dependency failure.

## Status

Prototype / research implementation accompanying the above patent application.
Contributions and issues welcome.
