import re
import numpy as np
import soundfile as sf
import torch
from transformers import VitsModel, AutoTokenizer

def chunk_text(text: str, max_length: int = 200):
    """Splits text into smaller sentences to prevent OOM errors."""
    # Split by standard sentence delimiters
    sentences = re.split(r'(?<=[.!?।]) +', text.replace('\n', ' '))
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def generate_english_tts(text: str, gender: str) -> np.ndarray:
    try:
        from kokoro_onnx import Kokoro
        kokoro = Kokoro("kokoro-v0_19.onnx", "voices.bin")
        voice_style = "af_sarah" if gender == "female" else "am_adam"
        samples, _ = kokoro.create(text, voice=voice_style, speed=1.0, lang="en-us")
        return samples
    except Exception as e:
        print(f"Kokoro failed: {e}. Fallback to MMS.")
        return generate_mms_tts(text, "facebook/mms-tts-eng")

def generate_mms_tts(text: str, model_name: str) -> np.ndarray:
    model = VitsModel.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        output = model(**inputs).waveform
    return output.numpy().squeeze()

def create_master_audio(text: str, language: str, gender: str, output_path: str):
    print(f"Chunking text and generating TTS ({language})...")
    chunks = chunk_text(text)
    audio_pieces = []
    sample_rate = 24000 if language == "english" else 16000 # MMS defaults to 16k, Kokoro to 24k

    for idx, chunk in enumerate(chunks):
        print(f"Processing TTS chunk {idx+1}/{len(chunks)}...")
        if language == "english":
            piece = generate_english_tts(chunk, gender)
            sample_rate = 24000
        elif language == "hindi":
            piece = generate_mms_tts(chunk, "facebook/mms-tts-hin")
        elif language == "bengali":
            piece = generate_mms_tts(chunk, "facebook/mms-tts-ben")
        else:
            raise ValueError("Unsupported language.")

        audio_pieces.append(piece)

    # Concatenate all numpy arrays into one continuous audio track
    master_audio = np.concatenate(audio_pieces)
    sf.write(output_path, master_audio, sample_rate)
    print(f"Master audio saved to {output_path}")