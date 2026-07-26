"""Validation module (patent ref: 114).

Validates a candidate remediation in an isolated sandbox before it's applied.
"""
from __future__ import annotations
import subprocess
import tempfile
import os
from dataclasses import dataclass
from src.remediation.remediation_generator import Remediation

@dataclass
class ValidationResult:
    passed: bool
    output: str


def validate_in_sandbox(remediation: Remediation, repo_path: str, test_command: str) -> ValidationResult:
    """Applies the patch to a temporary clone of the repo and runs the test command
    inside a Docker container, so nothing touches the real branch until validated."""
    with tempfile.TemporaryDirectory() as tmp:
        clone_result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_path, tmp],
            capture_output=True, text=True,
        )
        if clone_result.returncode != 0:
            return ValidationResult(False, clone_result.stderr)

        target = os.path.join(tmp, remediation.patch_target.replace("*", "ci"))
        try:
            with open(target, "a") as f:
                f.write(remediation.patch)
        except OSError as e:
            return ValidationResult(False, f"Could not apply patch: {e}")

        run = subprocess.run(
            ["docker", "run", "--rm", "-v", f"{tmp}:/workspace", "-w", "/workspace",
             "python:3.11-slim", "bash", "-c", test_command],
            capture_output=True, text=True, timeout=300,
        )
        return ValidationResult(run.returncode == 0, run.stdout + run.stderr)
