import os
import requests

def check_toxicity(text):
    prompt = f"""Check if the following comment is disrespectful, sexually inappropriate, harassing, or abusive. 
Respond with only "YES" if any issue is found, else "NO".

Comment: "{text}"
"""
    api_key = os.environ["GEMINI_API_KEY"]
    res = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        params={"key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )
    try:
        content = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        return "YES" in content.upper()
    except Exception as e:
        print("Error:", e)
        return False
