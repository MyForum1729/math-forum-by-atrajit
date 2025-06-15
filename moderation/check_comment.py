import sys
from gemini_check import check_toxicity
from email_alert import send_email
import requests
import os

comment_body, username, discussion_url, comment_node_id, repo = sys.argv[1:]

is_bad = check_toxicity(comment_body)

# Always notify by email
send_email(username, comment_body, discussion_url, is_bad)

if is_bad:
    token = os.environ["GITHUB_TOKEN"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    delete_url = f"https://api.github.com/repos/{repo}/discussion_comments/{comment_node_id}"
    r = requests.delete(delete_url, headers=headers)

    if r.status_code == 204:
        print("Comment deleted.")
    else:
        print("Failed to delete comment:", r.text)
