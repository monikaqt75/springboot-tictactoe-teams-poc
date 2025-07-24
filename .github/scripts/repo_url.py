#!/usr/bin/env python3
import os
import re
import subprocess
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
        return re.match(r"(?:.*@)?([^:/]+)", url).group(1)
    return urlparse(url).hostname or ""

def infer_server_name(host: str) -> str:
    parts = host.split(".")
    return parts[-2].replace("-", " ").title() if len(parts) >= 2 else host.title()

def detect_ci_tool_name() -> str:
    # 1) collect all env‑vars set to "true"/"1" (case‑insensitive)
    bool_indicators = {
        k for k,v in os.environ.items()
        if v.strip().lower() in ("true","1")
    }
    # 2) drop the generic "CI" flag if present
    bool_indicators.discard("CI")
    if not bool_indicators:
        return "Local / Unknown"

    # 3) choose the longest‑named one (to avoid small vars like TF_BUILD)
    tool_var = max(bool_indicators, key=len)
    # 4) format e.g. "GITHUB_ACTIONS" -> "Github Actions"
    return tool_var.replace("_"," ").title()

if __name__ == "__main__":
    url    = get_first_remote_url()
    host   = extract_hostname(url)
    server = infer_server_name(host)
    ci_tool = detect_ci_tool_name()

    print(f"Remote URL : {url}")
    print(f"Git Server : {server}")
    print(f"CI/CD Tool : {ci_tool}")