#!/usr/bin/env python3
import os
import json
import requests

# -----------------------------
# Load environment variables (from GitHub Secrets)
# -----------------------------
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")

TEAMS_WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_URL")
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL")

repo = os.environ.get("GITHUB_REPOSITORY", "unknown/repo")
branch = os.environ.get("GITHUB_REF_NAME", "unknown-branch")
actor = os.environ.get("GITHUB_ACTOR", "unknown-actor")
run_id = os.environ.get("GITHUB_RUN_ID", "0")
run_number = os.environ.get("GITHUB_RUN_NUMBER", "0")

# -----------------------------
# Function: Get AI explanation
# -----------------------------
def get_ai_explanation(log_content: str) -> str:
    """
    Sends the build log to Azure OpenAI GPT-35-Turbo and returns step-by-step fix suggestions
    """
    if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION]):
        return "⚠️ Azure OpenAI secrets not set."

    prompt = f"Analyze this build failure and provide step-by-step fix suggestions:\n\n{log_content}"

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY
    }

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ AI explanation failed: {str(e)}"

# -----------------------------
# Main function
# -----------------------------
def main():
    # Read error log
    try:
        with open("error.log", "r", encoding="utf-8") as f:
            log_content = f.read()
    except FileNotFoundError:
        log_content = "No error.log found."

    # Get AI explanation
    ai_msg = get_ai_explanation(log_content)

    # Prepare Teams message payload with buttons
    payload = {
        "repo": repo,
        "branch": branch,
        "actor": actor,
        "run_id": run_id,
        "run_number": run_number,
        "ai_explanation": ai_msg,
        "buttons": [
            {
                "type": "suggest-fix",
                "url": f"{FASTAPI_BASE_URL}/api/buttons/suggest-fix"
            },
            {
                "type": "rerun",
                "url": f"{FASTAPI_BASE_URL}/api/buttons/rerun"
            }
        ]
    }

    # Send notification to Teams webhook
    try:
        resp = requests.post(TEAMS_WEBHOOK_URL, headers={"Content-Type": "application/json"}, json=payload)
        if resp.status_code in [200, 201]:
            print(f"✅ Teams notification sent successfully!")
        else:
            print(f"⚠️ Teams notification failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"❌ Failed to send Teams notification: {e}")

if __name__ == "__main__":
    main()
