#!/usr/bin/env python3
import os
import json
import requests

def get_ai_explanation(log_content, gemini_api_key):
    print(f"DEBUG: Calling Gemini API...")
    prompt = (
        "You're an expert in CI/CD/CT and DevOps. Please explain the error in the following log: \n\n"
        f"{log_content}\n\n"
        "Please explain only the error in a concise way."
    )
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        resp = requests.post(gemini_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        print(f"DEBUG: Gemini response status: {resp.status_code}")
        resp.raise_for_status()
        ai_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"DEBUG: Got AI explanation")
        return ai_text
    except Exception as e:
        print(f"DEBUG: Gemini API error occurred: {e}")
        return "Unable to get AI explanation at this time."

def send_teams_message(webhook_url, adaptive_card):
    print(f"DEBUG: Sending Teams message...")
    try:
        resp = requests.post(webhook_url, headers={"Content-Type": "application/json"}, json=adaptive_card, timeout=10)
        print(f"DEBUG: Teams response status: {resp.status_code}")
        resp.raise_for_status()
        print(f"DEBUG: Teams message sent successfully!")
        return True
    except Exception as e:
        print(f"DEBUG: Failed to send Teams message: {e}")
        return False

def main():
    print(f"DEBUG: Script started")

    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    repo = os.environ.get("REPO")
    branch = os.environ.get("BRANCH")
    actor = os.environ.get("ACTOR")
    run_id = os.environ.get("RUN_ID")
    run_number = os.environ.get("RUN_NUMBER")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    print(f"DEBUG: Environment variables loaded")

    try:
        print(f"DEBUG: Reading error.log...")
        with open("error.log", "r", encoding="utf-8") as f:
            log_content = f.read()
        print(f"DEBUG: error.log read successfully")
    except Exception as e:
        log_content = None
        print(f"DEBUG: Could not read error.log: {e}")

    ai_explanation = "Could not read error logs."
    if log_content and gemini_api_key:
        print(f"DEBUG: Getting AI explanation...")
        ai_explanation = get_ai_explanation(log_content, gemini_api_key)
    elif not gemini_api_key:
        ai_explanation = "GEMINI_API_KEY not configured."

    error_log_url = f"https://monikaqt75.github.io/springboot-tictactoe-teams-poc/{branch}/{run_number}/error.log"
    workflow_url = f"https://github.com/{repo}/actions/runs/{run_id}"

    adaptive_card = {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "text": "Build Failed",
                "weight": "bolder",
                "size": "large",
                "color": "attention"
            },
            {
                "type": "FactSet",
                "facts": [
                    {
                        "title": "Repository:",
                        "value": repo
                    },
                    {
                        "title": "Branch:",
                        "value": branch
                    },
                    {
                        "title": "Triggered by:",
                        "value": actor
                    },
                    {
                        "title": "Run Number:",
                        "value": str(run_number)
                    }
                ]
            },
            {
                "type": "TextBlock",
                "text": "AI Explanation:",
                "weight": "bolder",
                "spacing": "medium"
            },
            {
                "type": "TextBlock",
                "text": ai_explanation,
                "wrap": True,
                "separator": True
            }
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Suggestion Fix",
                "data": {
                    "action": "button_click",
                    "button_type": "suggest_fix",
                    "run_id": str(run_id),
                    "user": actor,
                    "repo": repo,
                    "run_number": str(run_number)
                }
            },
            {
                "type": "Action.Submit",
                "title": "Re-run Workflow",
                "data": {
                    "action": "button_click",
                    "button_type": "rerun",
                    "run_id": str(run_id),
                    "user": actor,
                    "repo": repo
                }
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4"
    }

    print(f"DEBUG: Adaptive card prepared")
    send_teams_message(webhook_url, adaptive_card)
    print(f"DEBUG: Script completed")

if __name__ == "__main__":
    main()
