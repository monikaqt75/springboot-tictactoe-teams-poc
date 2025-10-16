import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Read environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TEAMS_WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_URL")

# Function to get AI explanation from Gemini
def get_ai_explanation(log_content):
    if not GEMINI_API_KEY or not log_content:
        return "AI explanation not available due to missing API key or log content."

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Explain the following build error log:\n{log_content}"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
        response.raise_for_status()
        candidates = response.json().get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", [])
            if parts:
                return parts[0].get("text", "No explanation found.")
        return "No valid AI explanation received."
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Unable to get AI explanation at this time."

# FastAPI endpoint to receive notification
@app.post("/notify")
async def notify_teams(request: Request):
    data = await request.json()

    # Extract data from payload
    repo_name = data.get("repo_name", "Unknown Repo")
    branch = data.get("branch", "Unknown Branch")
    workflow_url = data.get("workflow_url", "#")
    logs_url = data.get("logs_url", "#")
    suggestion_url = data.get("suggestion_url", "#")
    run_id = data.get("run_id", "")
    error_log = data.get("error_log", "")

    # Get AI explanation
    ai_explanation = get_ai_explanation(error_log)

    # Construct Adaptive Card payload
    card_payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": f"🚨 Build Failed: **{repo_name}** on branch **{branch}**",
                            "wrap": True,
                            "weight": "Bolder",
                            "size": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"**AI Explanation:**\n{ai_explanation}",
                            "wrap": True
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.OpenUrl",
                            "title": "🔍 View Workflow",
                            "url": workflow_url
                        },
                        {
                            "type": "Action.OpenUrl",
                            "title": "📄 View Logs",
                            "url": logs_url
                        },
                        {
                            "type": "Action.OpenUrl",
                            "title": "💡 Suggestion Fix",
                            "url": suggestion_url
                        },
                        {
                            "type": "Action.OpenUrl",
                            "title": "🔁 Re-run Workflow",
                            "url": f"https://github.com/{repo_name}/actions/runs/{run_id}"
                        }
                    ]
                }
            }
        ]
    }

    # Send to Teams
    if TEAMS_WEBHOOK_URL:
        try:
            response = requests.post(TEAMS_WEBHOOK_URL, json=card_payload)
            response.raise_for_status()
            print("✅ Notification sent to Teams.")
        except Exception as e:
            print(f"❌ Failed to send to Teams: {e}")
    else:
        print("⚠️ TEAMS_WEBHOOK_URL not set. Card preview:")
        print(card_payload)

    return JSONResponse({"status": "ok", "ai_explanation": ai_explanation})
