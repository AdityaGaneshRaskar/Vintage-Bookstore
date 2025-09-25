import os
import requests

# Load your API key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Did you set the environment variable?")

# Gemini API endpoint
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

# Define headers + request
headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY
}

data = {
    "contents": [
        {"parts": [{"text": "Give me feedback on this short speech: Hello everyone, today I will talk about AI in education."}]}
    ]
}

# Send request
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print("✅ Gemini Response:")
    print(result["candidates"][0]["content"]["parts"][0]["text"])
else:
    print("❌ Error:", response.status_code, response.text)
