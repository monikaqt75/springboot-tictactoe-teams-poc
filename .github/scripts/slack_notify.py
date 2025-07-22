#!/usr/bin/env python3
import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def main():
    # Load environment
    token      = os.environ["SLACK_BOT_TOKEN"]
    channel    = os.environ["SLACK_CHANNEL"]
    repo       = os.environ["REPO"]
    branch     = os.environ["BRANCH"]
    actor      = os.environ["ACTOR"]
    run_id     = os.environ["RUN_ID"]
    run_number = os.environ["RUN_NUMBER"]

    client = WebClient(token=token)

    # 1) Upload the error.log file (no initial_comment)
    try:
        upload_resp = client.files_upload_v2(
            channel=channel,
            file="error.log",
            title="🚨 Build Error Log",
            filename="error.log"
        )
        file_id = upload_resp["file"]["id"]
    except SlackApiError as e:
        print(f"⚠️ Failed to upload file: {e.response['error']}")
        return

    # 2) Prepare blocks: file first, then info and buttons
    file_block = {
        "type": "file",
        "block_id": "error_log",
        "external_id": file_id,
        "source": "remote"
    }

    info_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                f"*Repository:* `{repo}`\n"
                f"*Branch:* `{branch}`\n"
                f"*Triggered by:* `{actor}`"
            )
        }
    }

    action_block = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Explain"},
                "style": "primary",
                "url": f"https://devopsrehan.github.io/springboot-tictactoe/{run_number}",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Fix"},
                "style": "primary",
                "url": f"https://devopsrehan.github.io/springboot-tictactoe/{run_number}",
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

    # 3) Post the combined message
    try:
        client.chat_postMessage(
            channel=channel,
            text=":x: *Build Failed* — see log above",
            blocks=[file_block, info_block, action_block]
        )
    except SlackApiError as e:
        print(f"⚠️ Failed to post message: {e.response['error']}")

if __name__ == "__main__":
    main()
