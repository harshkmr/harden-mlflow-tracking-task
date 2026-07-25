import os

# <<<<<<< HEAD
# Legacy main configuration (Insecure defaults)
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://0.0.0.0:5000")
ARTIFACT_LOCATION = os.getenv("MLFLOW_ARTIFACT_LOCATION", "/tmp/mlflow_artifacts")
EXPERIMENT_NAME = "huggingface_eval_main"
APPROVED_METADATA_KEYS = ["model_name", "model_type", "num_parameters", "eval_loss", "eval_perplexity", "git_commit_sha", "hf_token", "raw_kwargs"]
# =======
# Security Hardened Configuration
# TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "file:///app/mlruns")
# ARTIFACT_LOCATION = os.getenv("MLFLOW_ARTIFACT_LOCATION", "/app/mlruns")
# EXPERIMENT_NAME = "huggingface_eval_hardened"
# APPROVED_METADATA_KEYS = {
#     "model_name",
#     "model_type",
#     "num_parameters",
#     "eval_loss",
#     "eval_perplexity",
#     "git_commit_sha",
# }
# >>>>>>> feature/security-hardening
