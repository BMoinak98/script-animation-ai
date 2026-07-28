import os
import glob
import urllib.parse
import requests
import time

def clean_workspace():
    """Wipes old frame PNGs to ensure a fresh single run every time."""
    print("[Engine] Cleaning workspace...")
    for file in glob.glob("frame_*.png"):
        try:
            os.remove(file)
        except OSError:
            pass

def generate_all_images(storyboard_data: dict, delay_seconds: int = 0.5):
    """
    Renders all storyboard frames sequentially in a simple single thread.
    Pauses for `delay_seconds` (default 30s) between requests.
    """
    clean_workspace()

    frames = storyboard_data.get("frames", [])
    total_frames = len(frames)

    print(f"[Engine] Starting single-threaded rendering for {total_frames} frames.")
    print(f"[Engine] Rate-limit delay: {delay_seconds} seconds between images.\n")

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    total_start_time = time.time()

    for i, frame in enumerate(frames):
        idx = frame.get('index', i)
        out_path = f"frame_{idx}.png"

        angle = frame.get('camera_angle', 'Wide Shot')
        chars = frame.get('characters_in_scene', 'A character standing calmly')
        env = frame.get('environment', 'Clean background')
        props = frame.get('props_in_scene', 'Clear visual props')
        desc = frame.get('visual_description', '')

        # Detailed prompt structure
        raw_prompt = (
            f"Cinematic sharp focus 3D render, 8k resolution. "
            f"{angle}. Key Props: {props}. Character: {chars}. Environment: {env}. "
            f"Scene Details: {desc}. Photorealistic lighting, highly detailed textures, "
            f"stationary freeze-frame pose, sharp details, clean aesthetic, no motion blur, no extra limbs."
        )

        encoded_prompt = urllib.parse.quote(raw_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&seed=105&nologo=true&model=turbo"

        print(f"[{i+1}/{total_frames}] Requesting frame_{idx}.png...")
        frame_start = time.time()

        try:
            response = session.get(url, headers=headers, timeout=120)

            if response.status_code == 200:
                with open(out_path, 'wb') as f:
                    f.write(response.content)
                elapsed = time.time() - frame_start
                print(f"  -> Successfully saved {out_path} in {elapsed:.2f}s")
            else:
                print(f"  -> ERROR: Received HTTP {response.status_code} for frame_{idx}")

        except Exception as e:
            print(f"  -> ERROR generating frame_{idx}: {e}")

        # Sleep for 30 seconds before requesting the next frame (except for the last frame)
        if i < total_frames - 1:
            print(f"  -> Pausing {delay_seconds}s before next request...\n")
            time.sleep(delay_seconds)

    session.close()

    total_elapsed = time.time() - total_start_time
    print(f"\n[Engine] All rendering finished in {total_elapsed / 60:.2f} minutes.")