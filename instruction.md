# Harden MLflow Tracking After a Conflicted Rebase

## Overview
A security refactoring branch was being rebased onto `main`, but an interrupted git rebase left several conflicted files in the repository at `/app`. Furthermore, the MLflow tracking harness exposes insecure defaults and fails security compliance checks.

The repository includes a security review documentation bundle at `/app/docs/security_review_bundle.md`. You must consult this documentation bundle to understand the security requirements, conflict resolution policies, approved MLflow metadata fields, secret redaction rules, allowed tracking URIs, and artifact path safety constraints.

## Requirements

1. **Resolve Git Rebase Conflicts**:
   - Resolve all merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) across all files in `/app` (including `src/tracking_harness.py` and `src/config.py`).
   - Ensure the git repository state in `/app` is clean and free of unresolved merge conflict markers.

2. **Security Compliance & Hardening**:
   - Consult `/app/docs/security_review_bundle.md` for security compliance standards.
   - **Token Leakage & Secret Redaction**: Ensure HF tokens (`hf_...`), API keys, passwords, and authorization headers are stripped/masked before logging any MLflow parameters, tags, or metrics.
   - **Authenticated Tracking URIs**: Prevent unauthenticated HTTP tracking URIs (e.g., insecure defaults like `http://0.0.0.0:5000` or `http://localhost:5000` without auth). Ensure tracking URIs use approved schemes (`https://...` or authenticated local file store URI such as `file:///app/mlruns`).
   - **Safe Artifact Paths**: Prevent unsafe artifact store locations (e.g. path traversal or arbitrary external directories like `/tmp/` or `/etc/`). Validate and restrict artifact storage to approved directories (`/app/mlruns` or relative subdirectories under `/app/artifacts`).
   - **Approved Metadata Registration**: Ensure MLflow runs register *only* approved metadata fields:
     - `model_name`
     - `model_type`
     - `num_parameters`
     - `eval_loss`
     - `eval_perplexity`
     - `git_commit_sha`
     Any unapproved parameter or tag must be excluded from logging.

3. **Hugging Face Model Evaluation**:
   - Ensure `/app/src/tracking_harness.py` downloads and evaluates the model `sshleifer/tiny-gpt2` from Hugging Face using `transformers`.
   - Calculate model evaluation metrics (`eval_loss` and `eval_perplexity`) and log them along with model metadata under an active MLflow experiment.

4. **Static Security Analyzer Verification**:
   - Verify your fixes by executing `python /app/security_analyzer.py`. It must run cleanly and report zero security violations.
   - Verify execution by running `python /app/src/tracking_harness.py`. It must run to completion and log the model evaluation run securely.
