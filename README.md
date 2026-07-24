# Harden MLflow Tracking After a Conflicted Rebase

[![Schema Version](https://img.shields.io/badge/schema-2.0-blue.svg)](task.toml)
[![Python](https://img.shields.io/badge/python-3.11-brightgreen.svg)](environment/Dockerfile)
[![MLflow](https://img.shields.io/badge/MLflow-2.14.1-orange.svg)](environment/Dockerfile)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An AI coding benchmark task designed to evaluate an agent's ability to resolve interrupted git rebase merge conflicts, enforce security policies for machine learning experiment tracking, and evaluate Hugging Face transformer models safely.

---

## 📋 Task Overview

During a security refactoring initiative, an interrupted git rebase left active merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) across the MLflow tracking harness. Additionally, legacy defaults exposed sensitive tokens (like Hugging Face API keys and passwords) in plaintext to unauthenticated network tracking servers.

An AI evaluation agent must consult the security documentation bundle in `docs/security_review_bundle.md`, resolve all git conflicts, redact secrets, enforce safe artifact storage, restrict parameter logging to approved fields, and track evaluation metrics for `sshleifer/tiny-gpt2`.

---

## 🛡️ Security Hardening Rules

| Security Area | Policy Requirement |
| :--- | :--- |
| **Git Conflict Resolution** | Eliminate all merge conflict markers across `tracking_harness.py` and `config.py`. |
| **Secret Redaction** | Mask HF tokens (`hf_...`), passwords, and API secrets prior to logging. |
| **Approved Metadata Whitelist** | Restrict logged parameters to: `model_name`, `model_type`, `num_parameters`, `eval_loss`, `eval_perplexity`, `git_commit_sha`. |
| **Authenticated Tracking URIs** | Prohibit unauthenticated HTTP endpoints (`http://0.0.0.0:5000`). Enforce authenticated file store URIs (`file:///app/mlruns`). |
| **Safe Artifact Locations** | Restrict artifact storage to sandbox isolated directory `/app/mlruns`. |
| **Static Security Analyzer** | Enforce zero violations when executing `security_analyzer.py`. |

---

## 📁 Repository Layout

```text
.
├── README.md                              # Repository overview & setup guide
├── instruction.md                          # Task prompt & agent instructions
├── task.toml                              # Benchmark metadata schema (version 2.0)
├── task.zip                               # Packaged benchmark archive
├── environment/
│   ├── Dockerfile                         # Python 3.11 environment setup
│   └── app/                               # Codebase with merge conflicts
│       ├── security_analyzer.py           # Static security policy analyzer
│       ├── docs/
│       │   └── security_review_bundle.md  # Security review & policy documentation
│       └── src/
│           ├── config.py                  # Conflicted configuration file
│           └── tracking_harness.py        # Conflicted MLflow tracking harness
├── solution/
│   └── solve.sh                           # Oracle solution script
└── tests/
    ├── test.sh                            # Verifier execution script
    └── test_outputs.py                    # Pytest verification test suite
```

---

## 🚀 Quickstart & Container Testing

### 1. Build the Task Container
```bash
docker build -t harden-mlflow-task environment/
```

### 2. Test Initial Unhardened / Conflicted State
```bash
docker run --rm harden-mlflow-task python security_analyzer.py
```
*(Fails intentionally with 10 security policy violations)*

### 3. Run Oracle Solution & Verification Suite
```bash
docker run --rm -v "${PWD}/solution/solve.sh:/solve.sh" -v "${PWD}/tests:/tests" harden-mlflow-task bash -c "bash /solve.sh && bash /tests/test.sh"
```
*(Resolves conflicts, evaluates `sshleifer/tiny-gpt2`, and reports 4 passed tests)*

---

## 🧪 Verification Results

```text
PASSED tests/test_outputs.py::test_no_conflict_markers
PASSED tests/test_outputs.py::test_security_analyzer_passes
PASSED tests/test_outputs.py::test_tracking_harness_execution
PASSED tests/test_outputs.py::test_mlflow_run_metadata_and_security
========================= 4 passed in 5.12s =========================
```
