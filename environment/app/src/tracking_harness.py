import math
import os

from config import APPROVED_METADATA_KEYS, EXPERIMENT_NAME
import mlflow
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


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
# <<<<<<< HEAD
        "hf_token": os.getenv("HF_TOKEN", "hf_insecure_token_1234567890abcdefghijklmnopqrstuvwxyz"),
        "raw_kwargs": {"debug": True, "api_secret": "supersecretkey"},
        "user_credentials": "admin:password123",
# =======
        # Security hardening branch: Filter unapproved metadata and prevent token leakage
# >>>>>>> feature/security-hardening
    }

    return raw_metadata


def main():
# <<<<<<< HEAD
    # Insecure default tracking URI and artifact location from main branch
    mlflow.set_tracking_uri("http://0.0.0.0:5000")
    mlflow.set_experiment(EXPERIMENT_NAME)

    metadata = evaluate_model()

    with mlflow.start_run():
        # Insecurely logging all parameters including secrets
        for k, v in metadata.items():
            mlflow.log_param(k, str(v))
        mlflow.log_dict(metadata, "eval_metadata.json")
# =======
    # Hardened tracking URI and artifact path setup
    # mlflow.set_tracking_uri(config.TRACKING_URI)
    # mlflow.set_experiment(EXPERIMENT_NAME)

    # raw_metadata = evaluate_model()
    # clean_metadata = redact_secrets(raw_metadata)

    # with mlflow.start_run():
    #     for k, v in clean_metadata.items():
    #         if isinstance(v, (int, float)):
    #             mlflow.log_metric(k, float(v))
    #         else:
    #             mlflow.log_param(k, str(v))
# >>>>>>> feature/security-hardening

    print("Model evaluation and tracking complete.")


if __name__ == "__main__":
    main()
