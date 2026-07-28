import os
import ssl

# Bypass SSL locally for macOS, but keep it secure in production
if not os.getenv("GITHUB_ACTIONS"):
    ssl._create_default_https_context = ssl._create_unverified_context
import whisper

def extract_timestamps(audio_path: str):
    print("Transcribing master audio to map visual timestamps...")
    # Using 'tiny' or 'base' is crucial for GH Actions RAM limits
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)

    segments = []
    for segment in result["segments"]:
        segments.append({
            "text": segment["text"].strip(),
            "start": segment["start"],
            "end": segment["end"]
        })
    return segments