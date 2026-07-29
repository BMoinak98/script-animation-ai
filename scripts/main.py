import os
import sys
import json
from tts_engine import create_master_audio
from transcriber import extract_timestamps
from prompt_generator import generate_global_storyboard
from video_assembler import build_final_video
from gdrive_utils import upload_to_drive

def run_pipeline():
    script_text = os.getenv("SCRIPT_TEXT", "This is a default test script for automated generation.")
    language = os.getenv("LANGUAGE", "english").lower()
    gender = os.getenv("VOICE_GENDER", "female").lower()
    mode = os.getenv("PIPELINE_MODE", "audio").lower()

    audio_file = "master_audio.wav"
    transcript_file = "transcript.json"
    video_file = "final_animation.mp4"

    uploaded_urls = {
        "audio": "",
        "transcript": "",
        "video": ""
    }

    try:
        # Step 1: Create Audio Track
        print(f"[Main] Mode: {mode.upper()} | Language: {language} | Gender: {gender}")
        create_master_audio(script_text, language, gender, audio_file)

        # Step 2: Extract Timestamp Alignment & Save Transcript File
        segments = extract_timestamps(audio_file)

        with open(transcript_file, "w", encoding="utf-8") as f:
            json.dump(segments, f, indent=2, ensure_ascii=False)
        print(f"[Main] Saved transcription file to {transcript_file}")

        # Step 3: Upload Audio and Transcript to Google Drive
        print("[Main] Uploading master audio to Google Drive...")
        uploaded_urls["audio"] = upload_to_drive(audio_file, "audio/wav")

        print("[Main] Uploading transcript JSON to Google Drive...")
        uploaded_urls["transcript"] = upload_to_drive(transcript_file, "application/json")

        # Step 4: Video Generation (if Video Mode selected)
        if mode == "video":
            print("[Main] Generating Global Storyboard & Video...")
            storyboard_data = generate_global_storyboard(script_text, segments)
            build_final_video(segments, storyboard_data, audio_file, video_file)

            print("[Main] Uploading video MP4 to Google Drive...")
            uploaded_urls["video"] = upload_to_drive(video_file, "video/mp4")

        # Step 5: Output Environment Variables for GitHub Actions runner
        if "GITHUB_ENV" in os.environ:
            with open(os.environ['GITHUB_ENV'], 'a') as f:
                f.write(f"AUDIO_URL={uploaded_urls['audio']}\n")
                f.write(f"TRANSCRIPT_URL={uploaded_urls['transcript']}\n")
                f.write(f"VIDEO_URL={uploaded_urls['video']}\n")

        print(f"[Main] Pipeline completed! Uploaded Artifacts: {uploaded_urls}")

    except Exception as e:
        print(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()