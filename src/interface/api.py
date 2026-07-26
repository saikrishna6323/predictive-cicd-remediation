"""User interface module (patent ref: 120). FastAPI dashboard + API."""
from __future__ import annotations
from fastapi import FastAPI
from src.feedback.feedback_store import FeedbackStore

app = FastAPI(title="Predictive CI/CD Remediation Dashboard")
store = FeedbackStore()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/stats")
def stats():
    return {"success_rate_by_root_cause": store.success_rate_by_cause()}

@app.get("/feedback")
def feedback():
    return store.load_all()
