FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        tmux \
        asciinema \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5 \
    transformers==4.47.1 \
    "torch>=2.3.1" --extra-index-url https://download.pytorch.org/whl/cpu \
    "huggingface_hub>=0.23.4" \
    "pyarrow>=16.0.0" \
    "numpy>=2.0.0" \
    Flask \
    alembic \
    cachetools \
    click \
    cloudpickle \
    docker \
    entrypoints \
    gitpython \
    graphene \
    importlib-metadata \
    markdown \
    opentelemetry-api \
    opentelemetry-sdk \
    protobuf \
    pyyaml \
    querystring_parser \
    requests \
    sqlparse

RUN python -m pip install --no-cache-dir --no-deps \
    mlflow==2.14.1

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
