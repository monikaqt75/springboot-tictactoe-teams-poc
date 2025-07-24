#!/usr/bin/env python3
import subprocess
import re
import sys
import os
from urllib.parse import urlparse

def get_first_remote_url() -> str:
    remotes = subprocess.check_output(["git", "remote"], text=True).splitlines()
    if not remotes:
        raise RuntimeError("No git remotes found")
    return subprocess.check_output(
        ["git", "remote", "get-url", remotes[0].strip()],
        text=True
    ).strip()

def extract_hostname(url: str) -> str:
    if url.startswith("git@") or url.startswith("ssh://"):
        m = re.match(r"(?:.*@)?([^:/]+)", url)
        return m.group(1)
    parsed = urlparse(url)
    return parsed.hostname or ""

def infer_server_name(host: str) -> str:
    parts = host.split(".")
    if len(parts) >= 2:
        return parts[-2].replace("-", " ").replace("_", " ").title()
    return host.title()

def detect_ci_vars() -> list[str]:
    """
    Return all env‑var names that look like CI/CD indicators:
      - name contains one of: CI, ACTION, BUILD, PIPELINE, JOB, WORKFLOW, TASK
      - and its value is truthy (non‑empty, often 'true'/'1')
    """
    tokens = ("CI", "ACTION", "BUILD", "PIPELINE", "WORKFLOW", "JOB", "TASK")
    found = []
    for k, v in os.environ.items():
        # only uppercase names
        if not k.isupper():
            continue
        # look for any token in the var name
        if any(tok in k for tok in tokens) and v:
            found.append(k)
    return sorted(found)

if __name__ == "__main__":
    try:
        url    = get_first_remote_url()
        host   = extract_hostname(url)
        server = infer_server_name(host)
        ci_vars = detect_ci_vars()

        print(f"Remote URL : {url}")
        print(f"Git Server : {server}")
        if ci_vars:
            print("CI/CD Indicator Env‑Vars:")
            for name in ci_vars:
                print(f"  • {name}")
        else:
            print("CI/CD Indicator Env‑Vars: (none detected — local run?)")

    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)