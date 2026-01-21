#!/usr/bin/env python3
import os
import json
import requests

# -----------------------------
# Load environment variables from GitHub Secrets
# -----------------------------
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")

TEAMS_BUTTONS_WEBHOOK_URL = os.environ.get("TEAMS_BUTTONS_WEBHOOK_URL")
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL")

repo = os.environ.get("GITHUB_REPOSITORY", "unknown/repo")
branch = os.environ.get("GITHUB_REF_NAME", "unknown-branch")
actor = os.environ.get("GITHUB_ACTOR", "unknown-actor")
run_id = os.environ.get("GITHUB_RUN_ID", "0")
run_number = os.environ.get("GITHUB_RUN_NUMBER", "0")

# -----------------------------
# Function: Get AI explanation from Azure OpenAI
# -----------------------------
def get_ai_explanation(log_content: str) -> str:
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
# Main function: Send Teams notification
# -----------------------------
def main():
    # Read last 50 lines of error log if it exists
    try:
        with open("error.log", "r", encoding="utf-8") as f:
            log_content = f.read()
    except FileNotFoundError:
        log_content = "No error.log found."

    # Get AI explanation
    ai_msg = get_ai_explanation(log_content)

    # Adaptive Card for Teams
    card = {
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {"type": "TextBlock", "text": "🚨 Build Failed", "weight": "Bolder", "size": "Large", "color": "Attention"},
            {"type": "TextBlock", "text": f"**Repository:** {repo}", "wrap": True},
            {"type": "TextBlock", "text": f"**Branch:** {branch}", "wrap": True},
            {"type": "TextBlock", "text": f"**Triggered by:** {actor}", "wrap": True},
            {"type": "TextBlock", "text": "💡 **AI Fix Suggestions:**", "weight": "Bolder", "wrap": True, "separator": True},
            {"type": "TextBlock", "text": ai_msg, "wrap": True, "separator": True}
        ],
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "Suggestion Fix",
                "url": f"{FASTAPI_BASE_URL}/api/buttons/suggest-fix?run_number={run_number}"
            },
            {
                "type": "Action.OpenUrl",
                "title": "Re-run",
                "url": f"{FASTAPI_BASE_URL}/api/buttons/rerun?run_id={run_id}"
            }
        ]
    }

    # Send notification
    if not TEAMS_BUTTONS_WEBHOOK_URL:
        print("❌ TEAMS_BUTTONS_WEBHOOK_URL not set. Cannot send notification.")
        return

    try:
        resp = requests.post(TEAMS_WEBHOOK_URL, headers={"Content-Type": "application/json"}, json=card)
        if resp.status_code in [200, 201]:
            print("✅ Teams notification sent successfully!")
        else:
            print(f"⚠️ Teams notification failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"❌ Failed to send Teams notification: {e}")

if __name__ == "__main__":
    main()
