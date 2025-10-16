#!/usr/bin/env python3
import os
import json
import requests

def get_ai_explanation(log_content, gemini_api_key):
    prompt = f"You're an expert in CI/CD/CT and DevOps. Please explain the error in the following log: \n\n{log_content}\n\nPlease explain only the error."
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        resp = requests.post(gemini_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        resp.raise_for_status()
        ai_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return ai_text
    except Exception as e:
        return f"⚠️ AI explanation failed: {str(e)}"

def main():
    webhook_url = os.environ["TEAMS_WEBHOOK_URL"]
    repo = os.environ["REPO"]
    branch = os.environ["BRANCH"]
    actor = os.environ["ACTOR"]
    run_id = os.environ["RUN_ID"]
    run_number = os.environ["RUN_NUMBER"]
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    fastapi_url = os.environ["FASTAPI_HANDLER_URL"]

    try:
        with open("error.log", "r", encoding="utf-8") as f:
            log_content = f.read()
    except Exception as e:
        log_content = None

    ai_msg = "⚠️ Could not read error.log"
    if log_content and gemini_api_key:
        ai_msg = get_ai_explanation(log_content, gemini_api_key)

    card = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {"type": "TextBlock", "text": "🚨 Build Failed", "weight": "Bolder", "size": "Large", "color": "Attention"},
                    {"type": "TextBlock", "text": f"**Repository:** {repo}", "wrap": True},
                    {"type": "TextBlock", "text": f"**Branch:** {branch}", "wrap": True},
                    {"type": "TextBlock", "text": f"**Triggered by:** {actor}", "wrap": True},
                    {"type": "TextBlock", "text": "💡 **AI Explanation:**", "weight": "Bolder", "wrap": True},
                    {"type": "TextBlock", "text": ai_msg, "wrap": True, "separator": True}
                ],
                "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "Suggestion Fix",
                        "url": f"{fastapi_url}/teams/fix?run_number={run_number}"
                    },
                    {
                        "type": "Action.OpenUrl",
                        "title": "Re-run",
                        "url": f"{fastapi_url}/teams/rerun?run_id={run_id}"
                    }
                ]
            }
        }]
    }

    resp = requests.post(webhook_url, json=card)
    print(f"Teams notification sent: {resp.status_code}")

if __name__ == "__main__":
    main()
