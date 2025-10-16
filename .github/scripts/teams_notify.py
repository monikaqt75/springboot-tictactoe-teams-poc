import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Read Gemini API key from environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_ai_explanation(log_content):
    """
    Call Gemini API to generate AI explanation for build errors.
    Returns a string explanation, or a safe fallback message.
    """
    if not log_content:
        return "Could not read error logs."

    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY not configured."

    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": GEMINI_API_KEY}
        data = {
            "contents": [{"parts": [{"text": f"Explain this build error:\n{log_content}"}]}]
        }

        response = requests.post(url, headers=headers, params=params, json=data)

        # Debug logging
        print("DEBUG: Gemini API status code:", response.status_code)
        print("DEBUG: Gemini API response:", response.text)

        response.raise_for_status()
        ai_text = response.json()["candidates"][0]["content"][0]["text"]
        return ai_text

    except Exception as e:
        print(f"AI explanation failed: {e}")
        return "Unable to get AI explanation at this time."


@app.post("/notify")
async def notify_teams(request: Request):
    """
    FastAPI endpoint to receive GitHub Actions workflow failure
    and send a Teams Adaptive Card with AI explanation.
    """
    payload = await request.json()

    # Extract useful info from GitHub payload
    repo_name = payload.get("repository", {}).get("name", "Unknown Repository")
    branch = payload.get("branch", "Unknown Branch")
    workflow_url = payload.get("workflow_url", "#")
    logs_url = payload.get("logs_url", "#")
    error_log = payload.get("error_log", "")

    # Get AI explanation for the error log
    ai_explanation = get_ai_explanation(error_log)

    # Build Adaptive Card payload
    card_payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {"type": "TextBlock", "size": "Medium", "weight": "Bolder",
                         "text": f"Build Failed: {repo_name} ({branch})"},
                        {"type": "TextBlock", "text": ai_explanation, "wrap": True}
                    ],
                    "actions": [
                        {"type": "Action.OpenUrl", "title": "View Workflow", "url": workflow_url},
                        {"type": "Action.OpenUrl", "title": "View Logs", "url": logs_url}
                    ]
                }
            }
        ]
    }

    # Send the card to Teams (replace with your webhook URL)
    teams_webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if teams_webhook_url:
        try:
            r = requests.post(teams_webhook_url, json=card_payload)
            print(f"Teams response status: {r.status_code}")
        except Exception as e:
            print(f"Failed to send Teams card: {e}")
    else:
        print("TEAMS_WEBHOOK_URL not configured. Printing card payload:")
        print(card_payload)

    return JSONResponse({"status": "ok", "ai_explanation": ai_explanation})
