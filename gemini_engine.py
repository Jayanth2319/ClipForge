
import os
import json
from dotenv import load_dotenv

load_dotenv()

def analyze_with_gemini(transcript_text, peak_segments):
    try:
        # Try real API first
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        prompt = f"""You are a viral content expert. Given this video transcript and peak segments, pick the BEST 60 second clip.

Transcript:
{transcript_text}

Peak Segments (start, end in seconds):
{peak_segments}

Return ONLY valid JSON with no markdown, no backticks:
{{
  "best_segment": {{"start": 0, "end": 60}},
  "hook_headline": "catchy headline under 10 words",
  "captions": [
    {{"start": 0, "end": 8, "text": "caption one"}},
    {{"start": 8, "end": 16, "text": "caption two"}},
    {{"start": 16, "end": 24, "text": "caption three"}},
    {{"start": 24, "end": 32, "text": "caption four"}},
    {{"start": 32, "end": 40, "text": "caption five"}},
    {{"start": 40, "end": 48, "text": "caption six"}},
    {{"start": 48, "end": 54, "text": "caption seven"}},
    {{"start": 54, "end": 60, "text": "caption eight"}}
  ],
  "reasoning": "one sentence why this clip is best"
}}"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        print("Gemini API succeeded!")
        return result

    except Exception as e:
        print(f"Gemini API failed: {e}")
        print("Switching to intelligent mock response...")
        return get_mock_response(peak_segments)


def get_mock_response(peak_segments):
    # Smart mock that uses actual detected peak timestamps
    if peak_segments:
        start = peak_segments[0][0]
        end = peak_segments[0][1]
    else:
        start = 0
        end = 60

    duration = end - start
    chunk = duration / 8

    return {
        "best_segment": {
            "start": start,
            "end": end
        },
        "hook_headline": "This Moment Will Change Everything",
        "captions": [
            {"start": start, "end": start + chunk, "text": "This is the moment"},
            {"start": start + chunk, "end": start + chunk*2, "text": "that changes everything"},
            {"start": start + chunk*2, "end": start + chunk*3, "text": "pay close attention"},
            {"start": start + chunk*3, "end": start + chunk*4, "text": "this wisdom is rare"},
            {"start": start + chunk*4, "end": start + chunk*5, "text": "most people miss this"},
            {"start": start + chunk*5, "end": start + chunk*6, "text": "but not you"},
            {"start": start + chunk*6, "end": start + chunk*7, "text": "remember this always"},
            {"start": start + chunk*7, "end": end, "text": "share this with someone"}
        ],
        "reasoning": "This segment contains the highest emotional energy and most impactful content of the entire video."
    }
