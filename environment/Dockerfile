FROM python:3.11-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        tmux \
        asciinema \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5 \
    mlflow==2.14.1 \
    transformers==4.42.4 \
    torch==2.3.1 --extra-index-url https://download.pytorch.org/whl/cpu \
    huggingface_hub==0.23.4

# Pre-download sshleifer/tiny-gpt2 model and tokenizer into HF cache
RUN python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('sshleifer/tiny-gpt2'); AutoModelForCausalLM.from_pretrained('sshleifer/tiny-gpt2')"

WORKDIR /app

# Copy application files into /app
COPY app /app

# Initialize git repo and setup conflict state
RUN git config --global user.name "Security Bot" \
    && git config --global user.email "security@company.internal" \
    && git init \
    && git add . \
    && git commit -m "Initial commit with security documentation and harness"
