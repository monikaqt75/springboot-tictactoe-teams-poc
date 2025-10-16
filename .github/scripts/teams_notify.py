#!/usr/bin/env python3
import os
import json
import requests

def get_ai_explanation(log_content, gemini_api_key):
    prompt = f"You are an expert DevOps engineer. Please analyze this build failure log and provide a clear, professional explanation of what went wrong. Be concise and helpful.\n\nLog:\n{log_content}\n\nProvide only the error explanation in a professional tone."
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_api_key}"
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
                "url": f"https://default6be5b754cbd243939dc2d7050d353c.69.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/3e8a18e21b7947baaa67e00003c6dc52/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=xAIlxFGvSq_hcco41E6U-QsnZPqU6rtG1W9X02mfqko&run_number={run_number}"
            },
            {
                "type": "Action.OpenUrl",
                "title": "Re-run",
                "url": f"https://default6be5b754cbd243939dc2d7050d353c.69.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/ac327e16aca24d2cb930c63c007fc61f/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=MxRZep_gM-8oux-7zvjDUOTNvL0TtA-2hawn14F7LxA&run_id={run_id}"
            }
        ]
    }

    resp = requests.post(webhook_url, json=card)
    print(f"Teams notification sent: {resp.status_code}")

if __name__ == "__main__":
    main()
