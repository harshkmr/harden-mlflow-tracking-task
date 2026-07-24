# Enterprise Security Review, Deployment Guidelines & Rebase Conflict Resolution Manual

## Section 1: Executive Summary & Rebase Context

### 1.1 Background
During a scheduled security audit of the Machine Learning Operations (MLOps) pipeline, multiple vulnerabilities were identified in the default MLflow experiment tracking harness. A refactoring initiative was launched under branch `feature/security-hardening` to replace legacy unauthenticated configurations with enterprise security controls.

During git rebase operations of `feature/security-hardening` onto `main`, merge conflicts occurred in `src/tracking_harness.py` and `src/config.py`. The rebase was interrupted, leaving active conflict markers across the codebase.

### 1.2 Required Task Outcomes
1. **Conflict Resolution**: All active merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) must be eliminated. Code must incorporate the security hardening specifications described in this manual.
2. **Secret Redaction**: No Hugging Face authentication tokens (`hf_...`), API credentials, passwords, or raw parameter dictionaries may be logged to MLflow.
3. **Approved Metadata Schema**: MLflow parameter and metric registration must be strictly constrained to the approved metadata fields:
   - `model_name`
   - `model_type`
   - `num_parameters`
   - `eval_loss`
   - `eval_perplexity`
   - `git_commit_sha`
4. **Secure Tracking URI**: Unauthenticated HTTP endpoints (such as `http://0.0.0.0:5000` or `http://localhost:5000`) are explicitly forbidden. Approved tracking URIs must use secure TLS schemes (`https://...`) or authenticated local file storage (`file:///app/mlruns`).
5. **Safe Artifact Storage**: Artifact storage locations must reside inside the sandbox filesystem (`/app/mlruns`). Paths starting with `/tmp/`, `/etc/`, or containing parent directory traversal (`..`) are strictly prohibited.
6. **Model Evaluation**: The evaluation pipeline must evaluate `sshleifer/tiny-gpt2` using Hugging Face `transformers` and `torch`.

---

## Section 2: Security Architecture & Threat Model

### 2.1 Threat Vectors in MLOps Tracking
MLflow tracking servers store parameters, metrics, artifacts, and tags produced during model training and evaluation runs. Left unhardened, MLflow tracking exposes several critical attack vectors:

- **Token Leakage via Parameter Logging**: ML engineers frequently pass Hugging Face hub tokens (`HF_TOKEN`) or API keys into scripts via environment variables or parameter dictionaries. If logged directly using `mlflow.log_param()` or `mlflow.log_dict()`, secrets are persisted in plaintext.
- **Unauthenticated Network Endpoints**: Default MLflow setups often listen on `http://0.0.0.0:5000`. In shared cloud environments, unauthenticated endpoints allow unauthorized actors to read experiment metrics or modify run metadata.
- **Arbitrary File Storage (Path Traversal)**: Specifying unvalidated local artifact storage paths like `/tmp/mlflow_artifacts` or `/var/log` risks directory pollution, privilege escalation, or unauthorized artifact retrieval.

### 2.2 Approved Metadata Schema Specification
To enforce compliance, any metadata emitted to MLflow must be strictly filtered against an explicit whitelist.

| Metadata Field | Type | Description | Mandatory |
| :--- | :--- | :--- | :--- |
| `model_name` | string | Name of the evaluated Hugging Face repository (e.g. `sshleifer/tiny-gpt2`) | Yes |
| `model_type` | string | Transformer architecture class (e.g. `gpt2`) | Yes |
| `num_parameters` | integer | Total trainable parameter count | Yes |
| `eval_loss` | float | Cross-entropy evaluation loss | Yes |
| `eval_perplexity` | float | Exponential of evaluation loss | Yes |
| `git_commit_sha` | string | Current git commit hash | Yes |

*Note*: Any dictionary entries matching `hf_token`, `raw_kwargs`, `user_credentials`, `system_env`, or `api_secret` must be stripped prior to calling `mlflow.log_param()` or `mlflow.log_dict()`.

---

## Section 3: Detailed Conflict Resolution Guidelines

### 3.1 Resolving `src/config.py` Conflicts
In `src/config.py`, choose the security-hardened definitions over legacy main branch defaults:

```python
# APPROVED HARDENED CONFIGURATION
import os

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "file:///app/mlruns")
ARTIFACT_LOCATION = os.getenv("MLFLOW_ARTIFACT_LOCATION", "/app/mlruns")
EXPERIMENT_NAME = "huggingface_eval_hardened"
APPROVED_METADATA_KEYS = {
    "model_name",
    "model_type",
    "num_parameters",
    "eval_loss",
    "eval_perplexity",
    "git_commit_sha",
}
```

### 3.2 Resolving `src/tracking_harness.py` Conflicts
In `src/tracking_harness.py`, implement secret redaction and metadata filtering:

```python
def redact_secrets(metadata: dict) -> dict:
    """Filter metadata dictionary to contain ONLY approved keys and remove sensitive values."""
    sanitized = {}
    for key, val in metadata.items():
        if key in APPROVED_METADATA_KEYS:
            sanitized[key] = val
    return sanitized
```

Ensure `mlflow.set_tracking_uri(TRACKING_URI)` receives `file:///app/mlruns` or an authenticated TLS URI, never `http://0.0.0.0:5000`.

---

## Section 4: Static Security Analyzer Compliance Matrix

The provided `security_analyzer.py` performs static analysis of all source files in `/app`. The checks executed include:

1. **Check 1: Conflict Markers**: Fails if `<<<<<<<`, `=======`, or `>>>>>>>` appear anywhere in non-git files.
2. **Check 2: Insecure Tracking URIs**: Fails if `http://0.0.0.0` or unauthenticated HTTP ports are configured.
3. **Check 3: Unsafe Artifact Paths**: Fails if paths reference `/tmp/`, `/var/`, `/etc/`, or `..`.
4. **Check 4: Secret & Token Leakage**: Fails if Hugging Face tokens, passwords, or secret parameter names appear in logging calls.
5. **Check 5: Target Model Validation**: Verifies that `sshleifer/tiny-gpt2` is evaluated.

---

## Section 5: Deployment Verification Procedure

To verify compliance, execute the following commands in sequence:

```bash
# 1. Run static security analysis
python /app/security_analyzer.py

# 2. Run tracking harness evaluation
python /app/src/tracking_harness.py
```

Both commands must exit with status `0`.
