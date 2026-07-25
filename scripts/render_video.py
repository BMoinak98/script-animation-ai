import os
import subprocess

def create_video_from_frames(sentences, image_paths, audio_path, output_mp4):
    concat_file = "concat_list.txt"

    with open(concat_file, "w") as f:
        for img_path, sentence in zip(image_paths, sentences):
            duration = sentence["end"] - sentence["start"]
            f.write(f"file '{os.path.abspath(img_path)}'\n")
            f.write(f"duration {duration}\n")
        # Repeat last image frame per FFmpeg concat demuxer requirements
        f.write(f"file '{os.path.abspath(image_paths[-1])}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
        "-i", audio_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest",
        output_mp4
    ]

    subprocess.run(cmd, check=True)
    if os.path.exists(concat_file):
        os.remove(concat_file)