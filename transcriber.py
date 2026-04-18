import whisper

def transcribe_audio(audio_path):
    """
    Transcribes an audio file using OpenAI Whisper 'tiny' model.
    Returns a dictionary with 'text' and 'segments'.
    """
    try:
        print(f"Loading Whisper tiny model...")
        # Load the tiny model (this downloads the model on first run)
        model = whisper.load_model("tiny")
        
        print(f"Transcribing {audio_path}...")
        # Perform transcription
        result = model.transcribe(audio_path)
        
        # result contains 'text' and 'segments'
        # segment is a list of dicts which includes 'start', 'end', and 'text'
        return {
            "text": result["text"],
            "segments": result["segments"]
        }
    except Exception as e:
        print(f"Error in transcriber: {e}")
        return {"text": "", "segments": []}
