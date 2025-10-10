#!/usr/bin/env python3
import os
import json
import requests
import sys 

# --- HELPER FUNCTIONS ---

def get_ai_explanation(log_content, gemini_api_key):
    """Calls Gemini API to get a concise explanation of the error."""
    prompt = (
        "You're an expert in CI/CD/CT and DevOps. Please explain the error in the following log: \n\n"
        f"{log_content}\n\n"
        "Please explain only the error."
    )
    # This URL uses the correct Gemini API endpoint
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
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
        print(f"AI explanation failed: {str(e)}", file=sys.stderr)
        return f"AI explanation failed: {str(e)}"

# --- CORE FUNCTION: ADAPTIVE CARD GENERATOR ---

def create_adaptive_card(repo, branch, actor, run_id, run_number, ai_msg, workflow_url, error_log_url):
    """Generates the Adaptive Card JSON payload for Teams with interactive buttons."""
    
    # These parameters are what the buttons send to your Render/FastAPI service
    log_params = {
        "run_number": str(run_number), 
        "branch": branch, 
        "user": actor
    }

    # The Adaptive Card JSON definition - includes the 3 Action.Http buttons
    card_content = {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "size": "Medium",
                "weight": "Bolder",
                "text": "🚨 CI/CD Build Failed: AI Diagnostic 🚨",
                "color": "Attention",
                "wrap": True
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Repository:", "value": repo},
                    {"title": "Branch:", "value": branch},
                    {"title": "Triggered by:", "value": actor},
                    {"title": "Run Number:", "value": str(run_number)}
                ],
                "spacing": "Medium"
            },
            {
                "type": "TextBlock",
                "text": f"**Initial AI Analysis:**\n\n{ai_msg}",
                "wrap": True,
                "separator": True
            },
            {
                "type": "ActionSet",
                "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "View Workflow Run",
                        "url": workflow_url
                    },
                    {
                        "type": "Action.OpenUrl",
                        "title": "View Full Error Log",
                        "url": error_log_url
                    }
                ]
            }
        ],
        "actions": [
            # RERUN Button - sends 'run_id'
            {
                "type": "Action.Http",
                "title": "🛠️ Rerun Build",
                "method": "POST",
                "url": "https://fastapi-teams-handler.onrender.com/teams/interact",
                "body": json.dumps({"action": "rerun", "run_id": run_id, "user": actor}) 
            },
            # EXPLAIN Button - sends 'run_number' and 'branch'
            {
                "type": "Action.Http",
                "title": "🔍 Full Explanation",
                "method": "POST",
                "url": "https://fastapi-teams-handler.onrender.com/teams/interact",
                "body": json.dumps({"action": "explain", **log_params}) 
            },
            # FIX Button - sends 'run_number' and 'branch'
            {
                "type": "Action.Http",
                "title": "💡 Suggest Fix",
                "method": "POST",
                "url": "https://fastapi-teams-handler.onrender.com/teams/interact",
                "body": json.dumps({"action": "fix", **log_params}) 
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.2"
    }

    # Teams requires the Adaptive Card to be wrapped in this specific JSON structure
    teams_payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": card_content
            }
        ]
    }
    return teams_payload

# --- UPDATED: send_teams_message ---

def send_teams_message(webhook_url, payload):
    """Sends the message payload (Adaptive Card JSON) to the Power Automate webhook."""
    try:
        # We send the raw JSON to the Power Automate flow
        resp = requests.post(webhook_url, headers={"Content-Type": "application/json"}, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send Teams message: {str(e)}", file=sys.stderr)
        # Fallback to a simple text message in case the flow fails
        try:
            fallback_message = {"text": f"FATAL: Failed to send rich Teams notification card. Check Power Automate (Error: {str(e)})."}
            requests.post(webhook_url, headers={"Content-Type": "application/json"}, json=fallback_message, timeout=5)
        except:
            print("Fallback message also failed.", file=sys.stderr)
        return False

# --- UPDATED: main function ---

def main():
    # Environment variables are loaded by GitHub Actions
    webhook_url = os.environ["TEAMS_WEBHOOK_URL"]
    repo = os.environ["REPO"]
    branch = os.environ["BRANCH"]
    actor = os.environ["ACTOR"]
    run_id = os.environ["RUN_ID"]
    run_number = os.environ["RUN_NUMBER"]
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    # Log file retrieval (same as before)
    try:
        with open("error.log", "r", encoding="utf-8") as f:
            log_content = f.read()
    except Exception as e:
        log_content = None
        print(f"Could not read error.log: {str(e)}", file=sys.stderr)

    # Initial AI message (same as before)
    ai_msg = "Could not read error.log for initial AI explanation."
    if log_content and gemini_api_key:
        ai_msg = get_ai_explanation(log_content, gemini_api_key)
    elif not gemini_api_key:
        ai_msg = "GEMINI_API_KEY not set. Cannot provide AI explanation."

    # URL Generation 
    repo_owner = repo.split('/')[0]
    repo_name = repo.split('/')[1]
    # This URL points to the log file deployed via GitHub Pages
    error_log_url = f"https://{repo_owner}.github.io/{repo_name}/{branch}/{run_number}/error.log"
    workflow_url = f"https://github.com/{repo}/actions/runs/{run_id}"

    # --- Generate and Send the Adaptive Card ---
    teams_payload = create_adaptive_card(
        repo=repo,
        branch=branch,
        actor=actor,
        run_id=run_id, 
        run_number=run_number,
        ai_msg=ai_msg,
        workflow_url=workflow_url,
        error_log_url=error_log_url
    )

    send_teams_message(webhook_url, teams_payload)

if __name__ == "__main__":
    main()
