#!/usr/bin/env python3
import os
import json
import requests

def get_ai_explanation(log_content, gemini_api_key):
    print(f"DEBUG: Calling Gemini API...")
    prompt = (
        "You're an expert in CI/CD/CT and DevOps. Please explain the error in the following log: \n\n"
        f"{log_content}\n\n"
        "Please explain only the error."
    )
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        print(f"DEBUG: Gemini URL: {gemini_url[:50]}...")
        resp = requests.post(gemini_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        print(f"DEBUG: Gemini response status: {resp.status_code}")
        resp.raise_for_status()
        ai_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"DEBUG: Got AI text: {ai_text[:100]}...")
        return ai_text
    except Exception as e:
        print(f"DEBUG: Gemini API error occurred")
        return f"AI explanation failed: Unable to connect to AI service"

def send_teams_message(webhook_url, adaptive_card):
    print(f"DEBUG: Sending Teams message...")
    print(f"DEBUG: Webhook URL: {webhook_url[:50]}...")
    
    try:
        print(f"DEBUG: Sending Adaptive Card")
        resp = requests.post(webhook_url, headers={"Content-Type": "application/json"}, json=adaptive_card, timeout=10)
        print(f"DEBUG: Teams response status: {resp.status_code}")
        print(f"DEBUG: Teams response: {resp.text}")
        resp.raise_for_status()
        print(f"DEBUG: Teams message sent successfully!")
        return True
    except Exception as e:
        print(f"DEBUG: Failed to send Teams message: {str(e)}")
        return False

def main():
    print(f"DEBUG: Script started")
    
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    print(f"DEBUG: TEAMS_WEBHOOK_URL exists: {webhook_url is not None}")
    
    repo = os.environ.get("REPO")
    branch = os.environ.get("BRANCH")
    actor = os.environ.get("ACTOR")
    run_id = os.environ.get("RUN_ID")
    run_number = os.environ.get("RUN_NUMBER")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    
    print(f"DEBUG: Environment variables loaded")
    print(f"DEBUG: REPO={repo}, BRANCH={branch}, ACTOR={actor}, RUN_ID={run_id}, RUN_NUMBER={run_number}")
    print(f"DEBUG: GEMINI_API_KEY exists: {gemini_api_key is not None}")

    try:
        print(f"DEBUG: Trying to read error.log...")
        with open("error.log", "r", encoding="utf-8") as f:
            log_content = f.read()
        print(f"DEBUG: error.log read successfully, length: {len(log_content)}")
    except Exception as e:
        log_content = None
        print(f"DEBUG: Could not read error.log: {str(e)}")

    ai_msg = "Could not read error.log for AI explanation."
    if log_content and gemini_api_key:
        print(f"DEBUG: Getting AI explanation...")
        ai_text = get_ai_explanation(log_content, gemini_api_key)
        ai_msg = f"{ai_text}"
    elif not gemini_api_key:
        print(f"DEBUG: GEMINI_API_KEY not set")
        ai_msg = "GEMINI_API_KEY not set. Cannot provide AI explanation."

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
                "type": "TextBlock",
                "text": f"Repository: {repo}",
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": f"Branch: {branch}",
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": f"Triggered by: {actor}",
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": f"Run Number: {run_number}",
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": "AI Explanation:",
                "weight": "bolder",
                "spacing": "medium"
            },
            {
                "type": "TextBlock",
                "text": ai_msg,
                "wrap": True,
                "style": "emphasis"
            },
            {
                "type": "TextBlock",
                "text": "View Details:",
                "weight": "bolder",
                "spacing": "medium"
            },
            {
                "type": "TextBlock",
                "text": f"[Workflow Run]({workflow_url})",
                "wrap": True
            },
            {
                "type": "TextBlock",
                "text": f"[Error Log]({error_log_url})",
                "wrap": True
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
