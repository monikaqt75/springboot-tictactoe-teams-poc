#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import json
from urllib.parse import urlparse

import requests
import zipfile
import io
import argparse

# --- Git Remote Detection ---
def get_first_remote_url() -> str:
    """Get the URL of the first Git remote."""
    remotes = subprocess.check_output(["git", "remote"], text=True).splitlines()
    if not remotes:
        raise RuntimeError("No git remotes found")
    remote_name = remotes[0].strip()
    return subprocess.check_output(
        ["git", "remote", "get-url", remote_name],
        text=True
    ).strip()


def extract_hostname(url: str) -> str:
    """Extract the hostname from a Git remote URL."""
    if url.startswith("git@") or url.startswith("ssh://"):
        match = re.match(r"(?:.*@)?([^:/]+)", url)
        return match.group(1) if match else ""
    parsed = urlparse(url)
    return parsed.hostname or ""


def infer_server_name(host: str) -> str:
    """Normalize and prettify known Git server hostnames."""
    if not host:
        return "Unknown"
    host_lc = host.lower()
    known = {
        "github": "GitHub",
        "gitlab": "GitLab",
        "bitbucket": "Bitbucket",
        "azure": "Azure DevOps",
        "visualstudio": "Azure DevOps",
    }
    for key, name in known.items():
        if key in host_lc:
            return name
    parts = host_lc.split('.')
    return parts[-2].title() if len(parts) >= 2 else host.title()

# --- CI/CD Detection ---
def detect_ci_tool() -> dict:
    """Detect the CI/CD environment by checking common env vars."""
    ci_env = {
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
    for name, var in ci_env.items():
        if os.getenv(var):
            return {"name": name, "env_var": var}
    return {"name": "Unknown / Local", "env_var": None}

# --- Log Fetching Handlers ---
REGISTRY = {}
def register(ci_name):
    """Decorator to register a log fetching handler."""
    def decorator(fn):
        REGISTRY[ci_name] = fn
        return fn
    return decorator

@register("GitHub Actions")
def fetch_github_actions_logs():
    token = os.getenv("GITHUB_TOKEN")
    run_id = os.getenv("GITHUB_RUN_ID")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not all([token, run_id, repo]):
        raise RuntimeError("Missing GITHUB_TOKEN, GITHUB_RUN_ID, or GITHUB_REPOSITORY")
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
    headers = {"Authorization": f"Bearer {token}"}
    print(f"📦 Fetching GitHub Actions logs from: {url}")
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        for name in z.namelist():
            print(f"\n=== {name} ===")
            print(z.read(name).decode(errors='ignore'))

@register("Jenkins")
def fetch_jenkins_logs():
    j_url = os.getenv("JENKINS_URL")
    job = os.getenv("JOB_NAME")
    build = os.getenv("BUILD_NUMBER")
    user = os.getenv("JENKINS_USER")
    token = os.getenv("JENKINS_API_TOKEN")
    if not all([j_url, job, build, user, token]):
        raise RuntimeError("Missing Jenkins environment variables")
    console_url = f"{j_url.rstrip('/')}/job/{job}/{build}/consoleText"
    print(f"📦 Fetching Jenkins console logs from: {console_url}")
    resp = requests.get(console_url, auth=(user, token))
    resp.raise_for_status()
    print(resp.text)

@register("GitLab CI")
def fetch_gitlab_logs():
    project_id = os.getenv("CI_PROJECT_ID")
    job_id = os.getenv("CI_JOB_ID")
    token = os.getenv("GITLAB_TOKEN")
    if not all([project_id, job_id, token]):
        raise RuntimeError("Missing GitLab CI environment variables")
    url = f"https://gitlab.com/api/v4/projects/{project_id}/jobs/{job_id}/trace"
    headers = {"PRIVATE-TOKEN": token}
    print(f"📦 Fetching GitLab CI logs from: {url}")
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    print(resp.text)

@register("Azure Pipelines")
def fetch_azure_logs():
    org = os.getenv("SYSTEM_COLLECTIONURI")
    project = os.getenv("SYSTEM_TEAMPROJECT")
    build = os.getenv("BUILD_BUILDID")
    token = os.getenv("AZURE_DEVOPS_TOKEN")
    if not all([org, project, build, token]):
        raise RuntimeError("Missing Azure DevOps environment variables")
    logs_api = f"{org}{project}/_apis/build/builds/{build}/logs?api-version=6.0"
    print(f"📦 Fetching Azure Pipelines logs list from: {logs_api}")
    resp = requests.get(logs_api, auth=('', token))
    resp.raise_for_status()
    for entry in resp.json().get('value', []):
        print(f"\n=== Log {entry['id']} ({entry.get('type')}) ===")
        r2 = requests.get(entry['url'], auth=('', token))
        r2.raise_for_status()
        print(r2.text)

@register("CircleCI")
def fetch_circleci_logs():
    org = os.getenv("CIRCLE_PROJECT_USERNAME")
    repo = os.getenv("CIRCLE_PROJECT_REPONAME")
    build = os.getenv("CIRCLE_BUILD_NUM")
    token = os.getenv("CIRCLECI_TOKEN")
    if not all([org, repo, build, token]):
        raise RuntimeError("Missing CircleCI environment variables")
    slug = f"gh/{org}/{repo}"
    url = f"https://circleci.com/api/v2/project/{slug}/job/{build}/steps"
    headers = {"Circle-Token": token}
    print(f"📦 Fetching CircleCI logs from: {url}")
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    for step in resp.json().get('items', []):
        print(f"\n=== Step: {step['name']} [{step['status']}] ===")
        for action in step.get('actions', []):
            out = action.get('output_url')
            if out:
                data = requests.get(out, headers=headers).json().get('message', [])
                for msg in data:
                    print(msg.get('message'))

# Generic fallback
@register("Generic")
def fetch_generic_logs():
    url = os.getenv("CI_LOG_URL")
    method = os.getenv("CI_LOG_METHOD", "GET").upper()
    token = os.getenv("CI_LOG_TOKEN")
    if not url:
        raise RuntimeError("No generic CI_LOG_URL provided")
    headers = {"Authorization": token} if token else {}
    print(f"📦 Fetching logs from generic CI_LOG_URL: {url}")
    resp = requests.request(method, url, headers=headers, stream=True)
    resp.raise_for_status()
    if 'zip' in resp.headers.get('Content-Type', ''):
        z = zipfile.ZipFile(io.BytesIO(resp.content))
        for name in z.namelist():
            print(f"\n=== {name} ===")
            print(z.read(name).decode(errors='ignore'))
    else:
        for line in resp.iter_lines(decode_unicode=True):
            print(line)

# --- Main Entry Point ---
def main():
    parser = argparse.ArgumentParser(description="Detect Git server and CI/CD tool, optionally fetch logs.")
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--fetch-logs', action='store_true', help='Fetch and print CI/CD logs if supported')
    args = parser.parse_args()

    try:
        # Detection
        url = get_first_remote_url()
        host = extract_hostname(url)
        server = infer_server_name(host)
        ci = detect_ci_tool()

        # Output detection
        if args.json:
            print(json.dumps({
                "remote_url": url,
                "git_server": server,
                "ci_cd_tool": ci['name'],
                "ci_env_var": ci['env_var']
            }, indent=2))
        else:
            print(f"Remote URL   : {url}")
            print(f"Git Server   : {server}")
            print(f"CI/CD Tool   : {ci['name']}")
            if ci['env_var']:
                print(f"Detected via : {ci['env_var']}")

        # Fetch logs if requested
        if args.fetch_logs:
            print("\n🔍 Fetching CI/CD logs...\n")
            handler = REGISTRY.get(ci['name'], REGISTRY['Generic'])
            handler()

    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()