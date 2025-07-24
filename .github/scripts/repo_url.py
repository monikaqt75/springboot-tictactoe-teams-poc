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
    remote = remotes[0].strip()
    return subprocess.check_output(
        ["git", "remote", "get-url", remote],
        text=True
    ).strip()

def extract_hostname(url: str) -> str:
    if url.startswith("git@") or url.startswith("ssh://"):
        match = re.match(r"(?:.*@)?([^:/]+)", url)
        return match.group(1)
    parsed = urlparse(url)
    return parsed.hostname or ""

def infer_server_name(host: str) -> str:
    parts = host.split(".")
    if len(parts) >= 2:
        return parts[-2].replace("-", " ").replace("_", " ").title()
    return host.title()

def detect_ci_tool() -> str:
    # Use the presence of CI-specific env vars
    ci_vars = {
        "GitHub Actions": "GITHUB_ACTIONS",
        "GitLab CI": "GITLAB_CI",
        "Jenkins": "JENKINS_HOME",
        "Azure Pipelines": "TF_BUILD",
        "Bitbucket Pipelines": "BITBUCKET_BUILD_NUMBER",
        "CircleCI": "CIRCLECI",
        "Travis CI": "TRAVIS",
        "TeamCity": "TEAMCITY_VERSION",
        "Drone CI": "DRONE",
        "Buddy": "BUDDY",
    }
    for name, env_var in ci_vars.items():
        if os.getenv(env_var):
            return name
    return "Unknown / Local"

if __name__ == "__main__":
    try:
        url = get_first_remote_url()
        host = extract_hostname(url)
        server = infer_server_name(host)
        ci_tool = detect_ci_tool()

        print(f"Remote URL : {url}")
        print(f"Git Server : {server}")
        print(f"CI/CD Tool : {ci_tool}")

    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)