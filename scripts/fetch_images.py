import os
import asyncio
import aiohttp
import urllib.parse

async def download_single_image(session, prompt, idx, output_dir):
    # Free serverless image generation endpoint via Pollinations.ai
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true"

    file_path = os.path.join(output_dir, f"frame_{idx:03d}.png")
    async with session.get(url) as response:
        if response.status == 200:
            with open(file_path, "wb") as f:
                f.write(await response.read())
            return file_path
    return None

async def fetch_all_images(sentences, output_dir):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, sentence in enumerate(sentences):
            tasks.append(download_single_image(session, sentence["text"], i, output_dir))
        return await asyncio.gather(*tasks)