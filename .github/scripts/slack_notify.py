#!/usr/bin/env python3
import os
import json
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests

def get_ai_explanation(log_content, gemini_api_key):
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
        resp = requests.post(gemini_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        resp.raise_for_status()
        ai_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return ai_text
    except Exception as e:
        return f"⚠️ AI explanation failed: {str(e)}"

def main():
    token = os.environ["SLACK_BOT_TOKEN"]
    channel = os.environ["SLACK_CHANNEL"]
    repo = os.environ["REPO"]
    branch = os.environ["BRANCH"]
    actor = os.environ["ACTOR"]
    run_id = os.environ["RUN_ID"]
    run_number = os.environ["RUN_NUMBER"]
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    client = WebClient(token=token)

    # 1) Upload the error.log file
    try:
        upload_resp = client.files_upload_v2(
            channel=channel,
            file="error.log",
            title="🚨 Build Error Log",
            filename="error.log",
            initial_comment=":x: Build failed. Here's the full error log."
        )
        file_id = upload_resp["file"]["id"]
    except SlackApiError as e:
        print(f"Failed to upload file: {e.response['error']}")
        file_id = None

    # 2) Automatically post AI explanation
    try:
        with open("error.log", "r", encoding="utf-8") as f:
            log_content = f.read()
    except Exception as e:
        log_content = None

    ai_msg = "⚠️ Could not read error.log for AI explanation."
    if log_content and gemini_api_key:
        ai_text = get_ai_explanation(log_content, gemini_api_key)
        ai_msg = f"💡 *AI Explanation of the error:*\n```{ai_text}```"
    elif not gemini_api_key:
        ai_msg = "⚠️ GEMINI_API_KEY not set. Cannot provide AI explanation."

    # Wait for a moment to ensure the file is uploaded
    time.sleep(2)    

    # 3) Post the message with Fix and Re-run buttons only
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Repository:* `{repo}`\n"
                    f"*Branch:* `{branch}`\n"
                    f"*Triggered by:* `{actor}`"
                )
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ai_msg
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Fix"},
                    "style": "primary",
                    "value": f"https://devopsrehan.github.io/springboot-tictactoe/{run_number}",
                    "action_id": "fix_click"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Re-run"},
                    "style": "danger",
                    "value": json.dumps({"run_id": run_id}),
                    "action_id": "rerun_click"
                }
            ]
        }
    ]

    try:
        client.chat_postMessage(
            channel=channel,
            text=":x: *Build Failed*",
            blocks=blocks
        )
    except SlackApiError as e:
        print(f"Failed to post message: {e.response['error']}")

if __name__ == "__main__":
    main()