import os
from tts_engine import create_master_audio
from transcriber import extract_timestamps
from video_assembler import build_final_video
from gdrive_utils import upload_to_drive

def run_pipeline():
    # 1. Fetch parameters from GitHub Actions Environment
    script_text = os.getenv("SCRIPT_TEXT", "This is a fallback test script.")
    language = os.getenv("LANGUAGE", "english").lower()
    gender = os.getenv("VOICE_GENDER", "female").lower()
    sa_json = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON")

    audio_file = "master_audio.wav"
    video_file = "final_animation.mp4"

    # 2. Pipeline Execution
    try:
        create_master_audio(script_text, language, gender, audio_file)

        segments = extract_timestamps(audio_file)

        build_final_video(segments, audio_file, video_file)
# Inside main.py
        if sa_json:
            url = upload_to_drive(video_file, "video/mp4", sa_json)
            print(f"SUCCESS! Video uploaded successfully. View here: {url}")

            # Write the URL to the GitHub Actions environment variables
            with open(os.environ['GITHUB_ENV'], 'a') as f:
                f.write(f"VIDEO_URL={url}\n")
        else:
            print("Finished! No Google Drive credentials found, skipped upload.")

    except Exception as e:
        print(f"Pipeline failed: {e}")
        exit(1)

if __name__ == "__main__":
    run_pipeline()