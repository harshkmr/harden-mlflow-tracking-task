#!/bin/bash
set -e

echo "Starting solution to resolve git rebase conflicts and harden MLflow tracking harness..."

# Step 1: Write resolved src/config.py
cat << 'EOF' > /app/src/config.py
import os

# Hardened Configuration
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
EOF

# Step 2: Write resolved src/tracking_harness.py
cat << 'EOF' > /app/src/tracking_harness.py
import os
import sys
import math
import mlflow
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import TRACKING_URI, EXPERIMENT_NAME, ARTIFACT_LOCATION, APPROVED_METADATA_KEYS

def redact_secrets(metadata: dict) -> dict:
    """Filter metadata dictionary to contain ONLY approved keys and remove sensitive values."""
    sanitized = {}
    for key, val in metadata.items():
        if key in APPROVED_METADATA_KEYS:
            sanitized[key] = val
    return sanitized

def evaluate_model(model_name: str = "sshleifer/tiny-gpt2"):
    print(f"Loading model and tokenizer for: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    test_text = "The quick brown fox jumps over the lazy dog."
    inputs = tokenizer(test_text, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss.item()
        perplexity = math.exp(loss)

    num_params = sum(p.numel() for p in model.parameters())

    raw_metadata = {
        "model_name": model_name,
        "model_type": model.config.model_type,
        "num_parameters": num_params,
        "eval_loss": loss,
        "eval_perplexity": perplexity,
        "git_commit_sha": os.getenv("GIT_COMMIT_SHA", "main-commit-9f82a1"),
    }

    return raw_metadata

def main():
    # Hardened tracking URI and experiment configuration
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    
    raw_metadata = evaluate_model()
    clean_metadata = redact_secrets(raw_metadata)
    
    with mlflow.start_run():
        for k, v in clean_metadata.items():
            if isinstance(v, (int, float)):
                mlflow.log_metric(k, float(v))
            else:
                mlflow.log_param(k, str(v))

    print("Model evaluation and tracking complete.")

if __name__ == "__main__":
    main()
EOF

# Step 3: Verify static policy analyzer
python /app/policy_analyzer.py

# Step 4: Verify execution of tracking harness
python /app/src/tracking_harness.py

echo "Solution completed successfully!"
