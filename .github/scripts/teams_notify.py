#!/usr/bin/env python3
import os
import requests

def get_ai_explanation(log_content, gemini_api_key):
    prompt = f"Explain this build error briefly:\n\n{log_content}"
    try:
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(gemini_url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "AI explanation unavailable"

def main():
    # Get from new Power Automate flow (we'll create next)
    webhook_url = os.environ["TEAMS_BUTTONS_WEBHOOK_URL"]
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ["GITHUB_REF_NAME"]
    actor = os.environ["GITHUB_ACTOR"]
    run_id = os.environ["GITHUB_RUN_ID"]
    run_number = os.environ["GITHUB_RUN_NUMBER"]
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    # Read error log
    try:
        with open("error.log", "r") as f:
            log_content = f.read()
    except:
        log_content = "No error log"

    ai_msg = get_ai_explanation(log_content, gemini_api_key)

    # Send to NEW Power Automate flow
    payload = {
        "repo": repo,
        "branch": branch,
        "actor": actor,
        "run_id": run_id,
        "run_number": run_number,
        "ai_explanation": ai_msg
    }

    try:
        resp = requests.post(webhook_url, json=payload)
        print(f"NEW Teams buttons notification sent: {resp.status_code}")
    except Exception as e:
        print(f"Failed to send NEW notification: {e}")

if __name__ == "__main__":
    main()
