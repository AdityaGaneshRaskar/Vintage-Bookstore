from fastapi import FastAPI, UploadFile, File
import shutil
import os
import requests
import json
import json5  # forgiving JSON parser
import re
from backend.stt_service import transcribe_audio

# Create FastAPI app
app = FastAPI()

# Load Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def clean_json_text(text: str) -> str:
    """Clean and fix JSON text from Gemini before parsing."""
    text = text.strip()

    # Remove code block wrappers
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    # Fix single quotes → double quotes
    text = text.replace("'", '"')

    # Escape quotes inside values properly
    import re
    text = re.sub(r'(\w)"(\w)', r'\1\\"\2', text)  # speaker"s → speaker\"s

    return text


def get_gemini_feedback(transcription: str) -> dict:
    """
    Send transcription to Gemini API for structured feedback.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    data = {
        "contents": [
            {"parts": [{"text": f"""
            Evaluate this extempore speech:

            {transcription}

            Respond ONLY in valid JSON format (double quotes required, no code blocks, no markdown).
            Escape quotes inside text (use \\").
            
            For each category, give:
            1. score (1-10),
            2. comment (2-3 sentences with detailed explanation),
            3. improvements (bullet point suggestions).

            Structure:
            {{
              "Clarity": {{"score": number, "comment": "detailed feedback", "improvements": ["point1", "point2"]}},
              "Arguments": {{"score": number, "comment": "detailed feedback", "improvements": ["point1", "point2"]}},
              "Grammar": {{"score": number, "comment": "detailed feedback", "improvements": ["point1", "point2"]}},
              "Delivery": {{"score": number, "comment": "detailed feedback", "improvements": ["point1", "point2"]}},
              "Overall": {{"score": number, "comment": "summary of performance", "improvements": ["point1", "point2"]}}
            }}
            """}]}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        resp_json = response.json()
        feedback_text = resp_json["candidates"][0]["content"]["parts"][0]["text"]

        feedback_text = clean_json_text(feedback_text)

        # Try parsing as JSON
        try:
            return json.loads(feedback_text)
        except Exception:
            try:
                return json5.loads(feedback_text)  # fallback
            except Exception:
                return {"Error": f"Invalid JSON from Gemini after cleaning: {feedback_text}"}
    else:
        return {"Error": f"Gemini API error {response.status_code}: {response.text}"}


@app.get("/")
def home():
    return {"message": "Backend is running with Faster-Whisper + Gemini!"}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 1: Transcribe audio (speech → text)
    transcription = transcribe_audio(temp_file)

    # Step 2: Get Gemini structured feedback
    feedback = get_gemini_feedback(transcription)

    return {
        "transcription": transcription,
        "feedback": feedback
    }
