import subprocess

# get the first remote name (e.g. “origin”, “upstream”, etc.)
first_remote = subprocess.check_output(
    ["git", "remote"],
    text=True
).splitlines()[0].strip()

url = subprocess.check_output(
    ["git", "remote", "get-url", first_remote],
    text=True,
).strip()

print(url)
