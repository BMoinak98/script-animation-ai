import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from pollinations_engine import generate_all_images

MOTION_MODES = ["zoom_in", "pan_right", "zoom_out", "pan_left"]

def create_animated_frame(img_pil: Image.Image, t: float, duration: float, mode: str, text: str = "") -> np.ndarray:
    """Applies camera motion (pan/zoom) and lower-third subtitles to an image frame."""
    w, h = img_pil.size
    progress = t / duration if duration > 0 else 0.0

    # 1. Camera Pan / Zoom Calculations
    if mode == "zoom_in":
        scale = 1.0 + (0.12 * progress)  # 1.00x -> 1.12x
        crop_w, crop_h = int(w / scale), int(h / scale)
        left = (w - crop_w) // 2
        top = (h - crop_h) // 2

    elif mode == "zoom_out":
        scale = 1.12 - (0.12 * progress)  # 1.12x -> 1.00x
        crop_w, crop_h = int(w / scale), int(h / scale)
        left = (w - crop_w) // 2
        top = (h - crop_h) // 2

    elif mode == "pan_right":
        scale = 1.10
        crop_w, crop_h = int(w / scale), int(h / scale)
        max_shift = w - crop_w
        left = int(max_shift * progress)
        top = (h - crop_h) // 2

    elif mode == "pan_left":
        scale = 1.10
        crop_w, crop_h = int(w / scale), int(h / scale)
        max_shift = w - crop_w
        left = int(max_shift * (1.0 - progress))
        top = (h - crop_h) // 2

    else:
        left, top, crop_w, crop_h = 0, 0, w, h

    cropped = img_pil.crop((left, top, left + crop_w, top + crop_h))
    transformed_img = cropped.resize((w, h), Image.Resampling.LANCZOS)

    # 2. Draw Subtitles
    if text.strip():
        transformed_img = _draw_subtitles(transformed_img, text.strip())

    return np.array(transformed_img)


def _draw_subtitles(img_pil: Image.Image, text: str, font_size: int = 38) -> Image.Image:
    """Draws a clean, semi-transparent subtitle overlay near the bottom center."""
    img = img_pil.copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    padding = 16
    rect_x0 = (w - text_w) // 2 - padding
    rect_y0 = h - text_h - 90 - padding
    rect_x1 = (w + text_w) // 2 + padding
    rect_y1 = h - 90 + padding

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle([rect_x0, rect_y0, rect_x1, rect_y1], radius=12, fill=(0, 0, 0, 180))

    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw_final = ImageDraw.Draw(img)

    text_x = (w - text_w) // 2
    text_y = h - text_h - 90 - (text_h // 4)
    draw_final.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))

    return img.convert("RGB")


def build_final_video(segments: list, storyboard_data: dict, audio_path: str, output_video_path: str):
    """Renders images using Pollinations AI and constructs an animated MP4 video synced to full audio."""

    # Step 1: Render frame images using Pollinations Engine
    generate_all_images(storyboard_data)

    print("[VideoAssembler] Combining animated frames with master audio...")
    clips = []

    for i, seg in enumerate(segments):
        img_path = f"frame_{i}.png"

        # Calculate exact frame duration from segment timestamps
        duration = max(0.5, seg["end"] - seg["start"])
        subtitle_text = seg.get("text", "")

        # Fallback if image generation failed
        if not os.path.exists(img_path):
            from PIL import Image
            Image.new("RGB", (1920, 1080), "#f8f9fa").save(img_path)

        pil_img = Image.open(img_path).convert("RGB")

        # Alternate camera motions across frames
        motion_mode = MOTION_MODES[i % len(MOTION_MODES)]

        # Generator function for dynamic frame creation
        def make_frame(t, current_img=pil_img, dur=duration, mode=motion_mode, txt=subtitle_text):
            return create_animated_frame(current_img, t, dur, mode, txt)

        # Build dynamic clip
        clip = ImageClip(make_frame(0)).set_duration(duration)
        clip = clip.fl(lambda gf, t: make_frame(t))
        clips.append(clip)

    # Step 2: Stitch animated clips together and attach master audio
    concat_clip = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_path)
    final_clip = concat_clip.set_audio(audio)

    # Step 3: Write out final MP4
    final_clip.write_videofile(
        output_video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=2 # Optimized for GH Actions 2-core runner
    )
    print(f"[VideoAssembler] Video created successfully at {output_video_path}")