import os
import re
import subprocess
from pathlib import Path
import pytest
import mlflow

APP_DIR = Path("/app") if Path("/app").exists() else Path(__file__).parent.parent / "environment" / "app"

def test_no_conflict_markers():
    """Verify all git merge conflict markers have been resolved."""
    conflict_pattern = re.compile(r'^(<<<<<<<|=======|>>>>>>>)', re.MULTILINE)
    for root, _, files in os.walk(APP_DIR):
        if '.git' in root or '__pycache__' in root or 'mlruns' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.yaml', '.yml', '.json', '.sh')):
                filepath = Path(root) / file
                content = filepath.read_text(encoding='utf-8')
                assert not conflict_pattern.search(content), f"Conflict marker found in {filepath}"

def test_security_analyzer_passes():
    """Verify static security analyzer executes and reports 0 violations."""
    analyzer_script = APP_DIR / "security_analyzer.py"
    assert analyzer_script.exists(), "security_analyzer.py missing"

    result = subprocess.run(
        [sys.executable if 'sys' in locals() else "python", str(analyzer_script)],
        capture_output=True,
        text=True,
        cwd=str(APP_DIR)
    )
    assert result.returncode == 0, f"Security analyzer failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

def test_tracking_harness_execution():
    """Verify tracking harness executes without error."""
    harness_script = APP_DIR / "src" / "tracking_harness.py"
    assert harness_script.exists(), "tracking_harness.py missing"

    result = subprocess.run(
        ["python", str(harness_script)],
        capture_output=True,
        text=True,
        cwd=str(APP_DIR)
    )
    assert result.returncode == 0, f"Tracking harness failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

def test_mlflow_run_metadata_and_security():
    """Verify MLflow runs contain only approved metadata and no secrets."""
    mlruns_dir = APP_DIR / "mlruns"
    assert mlruns_dir.exists(), "MLflow mlruns directory was not created"

    mlflow.set_tracking_uri(f"file://{mlruns_dir.as_posix()}")
    client = mlflow.tracking.MlflowClient()

    experiments = client.search_experiments()
    assert len(experiments) > 0, "No MLflow experiments found"

    runs = client.search_runs(experiment_ids=[e.experiment_id for e in experiments])
    assert len(runs) > 0, "No MLflow runs found"

    approved_keys = {
        "model_name",
        "model_type",
        "num_parameters",
        "eval_loss",
        "eval_perplexity",
        "git_commit_sha"
    }

    forbidden_tokens = ["hf_insecure", "password", "supersecretkey", "user_credentials", "raw_kwargs", "api_secret"]

    for run in runs:
        logged_params = run.data.params
        logged_metrics = run.data.metrics
        all_logged_keys = set(logged_params.keys()) | set(logged_metrics.keys())

        # Check that logged keys are a subset of approved keys
        unapproved = all_logged_keys - approved_keys
        assert not unapproved, f"Unapproved metadata fields logged in MLflow run: {unapproved}"

        # Verify model_name param
        assert logged_params.get("model_name") == "sshleifer/tiny-gpt2", f"Expected model_name sshleifer/tiny-gpt2, got {logged_params.get('model_name')}"

        # Verify no secret tokens logged in params or tags
        for val in list(logged_params.values()) + list(run.data.tags.values()):
            for forbidden in forbidden_tokens:
                assert forbidden not in str(val), f"Forbidden secret string '{forbidden}' found in MLflow logged value: {val}"
