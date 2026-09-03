import json
import urllib.request


import json
import urllib.request

# Configuration
API_KEY = ""  # Replace with your actual API key
#MODEL_NAME = "gemini-3.1-flash-lite"  # Easy to change to gemini-1.5-pro, etc.
MODEL_NAME = 'gemini-flash-lite-latest'
PROMPT = "Tell me what is the sum of the 3rd fibonnaci value and the 10th fibonacci value. Your answer should be only one number and nothing else."

# Dynamic URL using f-string
url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"

payload = {
    "contents": [{"parts": [{"text": PROMPT}]}]
}

data = json.dumps(payload).encode("utf-8")
headers = {"Content-Type": "application/json"}

req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        print(result["candidates"][0]["content"]["parts"][0]["text"])
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}\n{e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")