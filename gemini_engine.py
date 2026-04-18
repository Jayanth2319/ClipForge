import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure GenAI with the API key
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found in environment.")

def analyze_transcript(transcript_text, peak_segments):
    """
    Use Google Gemini 1.5 Flash to select the best 60-second segment
    for a viral short based on the transcript and peak energy segments.
    """
    try:
        if not transcript_text or not peak_segments:
            raise ValueError("Transcript text or peak segments are empty.")

        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare the prompt
        prompt = f"""
You are a viral content expert. Given this video transcript and 3 high energy segments, pick the BEST 60 second clip for a viral short. 

High Energy Segments (Start and End in seconds):
{peak_segments}

Transcript:
{transcript_text}

Return ONLY valid JSON format with these exact keys:
- "best_segment": object with "start" and "end" in seconds (must be within one of the provided high energy segments)
- "hook_headline": string under 10 words, very catchy
- "captions": list of up to 10 objects each with "start", "end", "text" corresponding to the dialogue in the chosen segment
- "reasoning": one sentence why this clip is best

Do not include markdown tags like ```json or ```. Output raw JSON only.
"""
        print("Calling Gemini API...")
        # Generate content
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Strip potential markdown code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()
        
        # Parse the JSON
        result = json.loads(response_text)
        return result
        
    except json.JSONDecodeError as je:
        print(f"Error parsing Gemini JSON response: {je}")
        print(f"Raw response: {response_text}")
        return None
    except Exception as e:
        print(f"Error in gemini_engine: {e}")
        return None
