import time
import urllib.parse
import requests
from deep_translator import GoogleTranslator

def generate_scene_image(original_text: str, output_path: str):
    try:
        # Auto-detect language and translate to English for the Image model
        english_prompt = GoogleTranslator(source='auto', target='en').translate(original_text)
    except Exception as e:
        print(f"Translation failed: {e}")
        english_prompt = original_text

    formatted_prompt = f"minimalist simple black and white stick figure drawing, vector art, cartoon style, depicting: {english_prompt}"
    encoded_prompt = urllib.parse.quote(formatted_prompt)

    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
    else:
        print(f"Failed image generation: {response.status_code}")
        # Create a blank fallback image to prevent pipeline crash
        from PIL import Image
        Image.new("RGB", (1024, 1024), "white").save(output_path)

    # Mandatory delay to prevent API bans when generating 200+ images
    time.sleep(1.5)