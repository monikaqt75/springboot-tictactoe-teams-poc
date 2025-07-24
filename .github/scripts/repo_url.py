#!/usr/bin/env python3
import subprocess
import re
import sys
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
    # SSH style     git@github.com:org/repo.git
    # SSH full URL  ssh://git@github.com/org/repo.git
    if url.startswith("git@") or url.startswith("ssh://"):
        m = re.match(r"(?:.*@)?([^:/]+)", url)
        return m.group(1)
    # HTTPS/HTTP style
    parsed = urlparse(url)
    if parsed.hostname:
        return parsed.hostname
    raise RuntimeError(f"Cannot parse hostname from URL: {url}")

def infer_server_name(host: str) -> str:
    """
    Take the penultimate domain segment as the 'server name'.
    Examples:
      - "github.com"       → "GitHub"
      - "gitlab.company.io"→ "Company"
      - "dev.azure.com"    → "Azure"
      - "bitbucket.org"    → "Bitbucket"
    """
    parts = host.split(".")
    if len(parts) >= 2:
        name = parts[-2]
    else:
        name = host
    # Capitalize and normalize
    return name.replace("-", " ").replace("_", " ").title()

if __name__ == "__main__":
    try:
        url  = get_first_remote_url()
        host = extract_hostname(url)
        server = infer_server_name(host)
        print(f"Remote URL: {url}")
        print(f"Server: {server}")
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

