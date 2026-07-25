import os
import json
import asyncio
from tts_transcribe import generate_audio_and_timestamps
from fetch_images import fetch_all_images
from render_video import create_video_from_frames
from drive_uploader import upload_folder_contents

def main():
    script_text = os.environ.get("SCRIPT_TEXT")
    drive_folder_id = os.environ.get("DRIVE_FOLDER_ID")

    work_dir = "output_job"
    os.makedirs(work_dir, exist_ok=True)

    # 1. Audio & Forced Alignment
    print("Generating audio and alignment...")
    audio_path, sentences = generate_audio_and_timestamps(script_text, work_dir)

    # Save transcript file as JSON
    with open(os.path.join(work_dir, "transcript.json"), "w") as f:
        json.dump(sentences, f, indent=2)

    # 2. Fetch Images Asynchronously
    print("Fetching images in parallel...")
    image_paths = asyncio.run(fetch_all_images(sentences, work_dir))

    # 3. Render MP4
    print("Rendering video with FFmpeg...")
    output_mp4 = os.path.join(work_dir, "final_video.mp4")
    create_video_from_frames(sentences, image_paths, audio_path, output_mp4)

    # 4. Upload Assets to Google Drive
    print("Uploading output assets to Google Drive...")
    upload_folder_contents(work_dir, drive_folder_id)
    print("Job Completed Successfully!")

if __name__ == "__main__":
    main()