#!/usr/bin/env python3
import os
import json
import requests

def get_ai_explanation(log_content, gemini_api_key):
    prompt = (
        "You're an expert in CI/CD/CT and DevOps. Please explain the error in the following log: \n\n"
        f"{log_content}\n\n"
        "Please explain only the error."
    )
    gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        resp = requests.post(gemini_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        resp.raise_for_status()
        ai_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return ai_text
    except Exception as e:
        return f"AI explanation failed: {str(e)}"

def send_teams_message(webhook_url, message_text):
    payload = {"text": message_text}
    try:
        resp = requests.post(webhook_url, headers={"Content-Type": "application/json"}, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send Teams message: {str(e)}")
        return False

def main():
    webhook_url = os.environ["TEAMS_WEBHOOK_URL"]
    repo = os.environ["REPO"]
    branch = os.environ["BRANCH"]
    actor = os.environ["ACTOR"]
    run_id = os.environ["RUN_ID"]
    run_number = os.environ["RUN_NUMBER"]
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    try:
        with open("error.log", "r", encoding="utf-8") as f:
            log_content = f.read()
    except Exception as e:
        log_content = None
        print(f"Could not read error.log: {str(e)}")

    ai_msg = "Could not read error.log for AI explanation."
    if log_content and gemini_api_key:
        ai_text = get_ai_explanation(log_content, gemini_api_key)
        ai_msg = f"AI Explanation:\n\n{ai_text}"
    elif not gemini_api_key:
        ai_msg = "GEMINI_API_KEY not set. Cannot provide AI explanation."

    error_log_url = f"https://devopsrehan.github.io/springboot-tictactoe/{branch}/{run_number}/error.log"
    workflow_url = f"https://github.com/{repo}/actions/runs/{run_id}"

    message = f"""Build Failed

{ai_msg}

Repository: {repo}
Branch: {branch}
Triggered by: {actor}
Run Number: {run_number}

View Details:
- Workflow Run: {workflow_url}
- Error Log: {error_log_url}

Action Required: Review logs and fix the issue."""

    send_teams_message(webhook_url, message)

if __name__ == "__main__":
    main()
