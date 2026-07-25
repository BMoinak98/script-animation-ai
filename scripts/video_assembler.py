import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from image_gen import generate_scene_image

def build_final_video(segments: list, audio_path: str, output_video_path: str):
    print("Generating images and assembling video...")
    clips = []

    for i, seg in enumerate(segments):
        img_path = f"frame_{i}.png"
        duration = max(0.5, seg["end"] - seg["start"])

        print(f"Generating image {i+1}/{len(segments)}...")
        generate_scene_image(seg["text"], img_path)

        # Load image and set how long it stays on screen based on audio
        clip = ImageClip(img_path).set_duration(duration)
        clips.append(clip)

    concat_clip = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_path)
    final_clip = concat_clip.set_audio(audio)

    # Write optimized MP4
    final_clip.write_videofile(
        output_video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=2 # Optimized for GH Actions 2-core runner
    )

    # Cleanup temporary frames
    for i in range(len(segments)):
        if os.path.exists(f"frame_{i}.png"):
            os.remove(f"frame_{i}.png")