#!/usr/bin/env python3
import sys
import re
import os
from pathlib import Path

def check_conflict_markers(app_dir: Path):
    violations = []
    conflict_pattern = re.compile(r'^(<<<<<<<|=======|>>>>>>>)', re.MULTILINE)
    for root, _, files in os.walk(app_dir):
        if '.git' in root or '__pycache__' in root or 'mlruns' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.yaml', '.yml', '.json', '.sh')):
                filepath = Path(root) / file
                try:
                    content = filepath.read_text(encoding='utf-8')
                    if conflict_pattern.search(content):
                        violations.append(f"Unresolved git conflict markers found in {filepath}")
                except Exception as e:
                    pass
    return violations

def check_security_rules(app_dir: Path):
    violations = []
    harness_path = app_dir / "src" / "tracking_harness.py"
    config_path = app_dir / "src" / "config.py"

    if not harness_path.exists():
        return [f"Missing required file: {harness_path}"]

    harness_code = harness_path.read_text(encoding='utf-8')
    config_code = config_path.read_text(encoding='utf-8') if config_path.exists() else ""

    combined_code = harness_code + "\n" + config_code

    # Check 1: Insecure Tracking URIs
    insecure_uri_patterns = [
        r'http://0\.0\.0\.0',
        r'http://127\.0\.0\.1:5000(?!\s*#|\s*/\?auth)',
        r'http://localhost:5000',
        r'http://[a-zA-Z0-9.-]+:5000'
    ]
    for pattern in insecure_uri_patterns:
        if re.search(pattern, combined_code):
            violations.append(f"Insecure unauthenticated HTTP tracking URI detected matching pattern: {pattern}")

    # Check 2: Unsafe Artifact Paths
    unsafe_artifact_patterns = [
        r'["\']/tmp/[^"\']*["\']',
        r'["\']/var/[^"\']*["\']',
        r'["\']/etc/[^"\']*["\']',
        r'\.\./\.\.'
    ]
    for pattern in unsafe_artifact_patterns:
        if re.search(pattern, combined_code):
            violations.append(f"Unsafe artifact path detected: {pattern}")

    # Check 3: Plaintext Secret / Token Leakage in Logging
    secret_leak_patterns = [
        r'hf_[a-zA-Z0-9]{20,}',
        r'log_param\s*\(\s*["\'](token|password|secret|api_key|hf_token|bearer)["\']',
        r'log_params\s*\(\s*.*(?:token|password|secret|api_key|hf_token|bearer)',
        r'["\']hf_token["\']\s*:\s*',
        r'mlflow\.log_dict\s*\(\s*.*(?:token|password|secret|env)'
    ]
    for pattern in secret_leak_patterns:
        if re.search(pattern, combined_code, re.IGNORECASE):
            violations.append(f"Potential plaintext secret / token logging detected: {pattern}")

    # Check 4: Approved Metadata Enforcement
    # Approved metadata keys: model_name, model_type, num_parameters, eval_loss, eval_perplexity, git_commit_sha
    unapproved_keys = ['raw_kwargs', 'user_credentials', 'system_env', 'hf_token', 'api_secret', 'internal_ip', 'debug_flags']
    for unapproved in unapproved_keys:
        if re.search(rf'["\']?{unapproved}["\']?\s*[:=]', harness_code):
            violations.append(f"Unapproved metadata field detected in tracking code: '{unapproved}'")

    # Check 5: Target Model Usage
    if 'sshleifer/tiny-gpt2' not in combined_code:
        violations.append("Tracking harness must load and evaluate model 'sshleifer/tiny-gpt2'")

    return violations

def main():
    app_dir = Path("/app") if Path("/app").exists() else Path(__file__).parent
    print(f"[Security Analyzer] Inspecting repository at {app_dir}...")
    
    conflict_violations = check_conflict_markers(app_dir)
    security_violations = check_security_rules(app_dir)
    
    all_violations = conflict_violations + security_violations

    if all_violations:
        print("[FAIL] Security & Policy Violations Found:")
        for v in all_violations:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print("[PASS] No security violations detected. Repository compliance verified.")
        sys.exit(0)

if __name__ == "__main__":
    main()
