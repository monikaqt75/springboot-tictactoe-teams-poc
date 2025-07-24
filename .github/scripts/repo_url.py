#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from urllib.parse import urlparse

# These tokens appear in *every* CI/CD platform’s env‑var names:
CI_KEYWORDS = (
    "CI", "ACTION", "BUILD", "PIPELINE", "WORKFLOW", "JOB", "TASK", "DRONE",
    "RUNNER", "GITHUB", "GITLAB", "JENKINS", "TRAVIS", "CIRCLE", "TF_BUILD",
    "TEAMCITY", "BITBUCKET", "BUDDY", "APPVEYOR"
)

def get_first_remote_url() -> str:
    remotes = subprocess.check_output(["git", "remote"], text=True).splitlines()
    if not remotes:
        raise RuntimeError("No git remotes found")
    return subprocess.check_output(
        ["git", "remote", "get-url", remotes[0].strip()],
        text=True
    ).strip()

def extract_hostname(url: str) -> str:
    if url.startswith(("git@", "ssh://")):
        return re.match(r"(?:.*@)?([^:/]+)", url).group(1)
    parsed = urlparse(url)
    return parsed.hostname or ""

def infer_server_name(host: str) -> str:
    parts = host.split(".")
    return parts[-2].replace("-", " ").title() if len(parts) >= 2 else host.title()

def detect_ci_tool_name() -> str:
    # 1) Find all env‑vars that contain any CI_KEYWORD and are non‑empty
    candidates = [
        k for k,v in os.environ.items()
        if k.isupper() and v and any(tok in k for tok in CI_KEYWORDS)
    ]
    if not candidates:
        return "Local / Unknown"

    # 2) Prefer boolean flags ("true"/"1") over IDs or URLs
    bool_flags = [k for k in candidates if os.environ[k].strip().lower() in ("true","1")]
    pick_list = bool_flags or candidates

    # 3) From pick_list, choose the *longest* name (most specific)
    tool_var = max(pick_list, key=len)

    # 4) Pretty‑print: underscores→spaces, title‑case
    return tool_var.replace("_", " ").title()

if __name__ == "__main__":
    try:
        url    = get_first_remote_url()
        host   = extract_hostname(url)
        server = infer_server_name(host)
        ci_tool = detect_ci_tool_name()

        print(f"Remote URL : {url}")
        print(f"Git Server : {server}")
        print(f"CI/CD Tool : {ci_tool}")
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)