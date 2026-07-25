import os
import whisper
from gtts import gTTS

def generate_audio_and_timestamps(text, output_dir):
    audio_path = os.path.join(output_dir, "voiceover.mp3")

    # 1. Generate Audio (Using gTTS for simplicity; replace with Kokoro/MMS as needed)
    tts = gTTS(text=text, lang='en')
    tts.save(audio_path)

    # 2. Extract Sentence-Level Timestamps with Whisper
    model = whisper.load_model("tiny") # Lightweight model for quick CPU execution
    result = model.transcribe(audio_path)

    sentences = []
    for segment in result["segments"]:
        sentences.append({
            "text": segment["text"].strip(),
            "start": segment["start"],
            "end": segment["end"]
        })

    return audio_path, sentences