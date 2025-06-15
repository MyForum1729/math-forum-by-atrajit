import os
import json
import requests
from email_alert import send_email

# ========== Gemini Config ==========
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def check_inappropriate(content: str) -> bool:
    payload = {
        "contents": [
            {
                "parts": [{"text": content}]
            }
        ]
    }

    response = requests.post(
        GEMINI_API_URL,
        headers={"Content-Type": "application/json"},
        json=payload
    )

    if response.status_code != 200:
        print("Gemini API Error:", response.text)
        return False

    result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    print("Gemini moderation response:", result_text)
    return "yes" in result_text.lower()

# ========== GitHub Event Parsing ==========
with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
    event = json.load(f)

event_type = os.environ["GITHUB_EVENT_NAME"]
headers = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github+json"
}

if event_type == "discussion_comment":
    comment = event["comment"]["body"]
    user = event["comment"]["user"]["login"]
    comment_url = event["comment"]["html_url"]
    comment_id = event["comment"]["id"]

    prompt = f"Is the following comment disrespectful, harassing, or sexually inappropriate?\n\n\"{comment}\""
    flagged = check_inappropriate(prompt)

    if flagged:
        print("Flagged comment. Deleting.")
        url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/discussion_comments/{comment_id}"
        requests.delete(url, headers=headers)

    send_email(user, comment, comment_url, flagged, "Comment", "📝")

elif event_type == "discussion":
    title = event["discussion"]["title"]
    body = event["discussion"]["body"]
    user = event["discussion"]["user"]["login"]
    discussion_url = event["discussion"]["html_url"]
    discussion_node_id = event["discussion"]["node_id"]

    prompt = f"Is the following discussion title and content inappropriate, disrespectful, harassing, or sexually offensive?\n\nTitle: \"{title}\"\n\nContent:\n{body}\""
    flagged = check_inappropriate(prompt)

    if flagged:
        print("Flagged discussion. Deleting.")
        mutation = """
        mutation DeleteDiscussion($id: ID!) {
            deleteDiscussion(input: {discussionId: $id}) {
                clientMutationId
            }
        }
        """
        requests.post("https://api.github.com/graphql", json={
            "query": mutation,
            "variables": {"id": discussion_node_id}
        }, headers=headers)

    send_email(user, f"{title}\n\n{body}", discussion_url, flagged, "Discussion", "💬")
