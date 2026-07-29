import json
from google import genai
from google.genai import types
from gemini_helper import get_gemini_token

def generate_global_storyboard(script_text: str, segments: list) -> dict:
    api_key = get_gemini_token()
    if not api_key:
        print("[Director] GEMINI_API_KEY missing!")
        return fallback_storyboard(segments)

    client = genai.Client(api_key=api_key)
    transcript_summary = "\n".join([f"Frame {i}: \"{seg['text']}\"" for i, seg in enumerate(segments)])

    system_instruction = (
        "You are an expert cinematic storyboard director.\n\n"
        "STRICT DIRECTOR RULES:\n"
        "1. LITERAL VISUAL PROPS: Every frame MUST feature concrete physical props that match the spoken line literally:\n"
        "   - 'bedtime / sleep schedule' -> A large visible wall clock showing nighttime hours.\n"
        "   - 'anchor' -> A heavy metallic ship anchor sitting prominently in the room as a visual metaphor.\n"
        "   - 'two weeks' -> A wall calendar with 14 days clearly marked or circled in red.\n"
        "   - 'screens' -> A glowing smartphone screen with a red prohibition slash over it.\n"
        "   - 'alarm / wake time' -> A digital alarm clock glowing 06:00 AM on a nightstand.\n"
        "2. STATIC POSES ONLY (NO MOTION BLUR): Do NOT use motion verbs (e.g. 'shaking', 'waving', 'chopping', 'flexing', 'stretching'). "
        "   Use purely stationary poses (e.g. 'standing calmly', 'seated', 'pointing at the clock', 'holding the calendar').\n"
        "3. PROPORTION & FRAMING: Vary framing between Close-Up on key props, Medium shots with character holding props, and Wide room shots. "
        "   Do NOT place the character dead-center doing nothing in every shot.\n"
        "4. STYLE: Crisp cinematic 3D digital render, sharp focus, clean modern interior, professional lighting, zero blur.\n\n"
        "OUTPUT FORMAT (STRICT JSON ONLY):\n"
        "{\n"
        "  \"frames\": [\n"
        "    {\n"
        "      \"index\": 0,\n"
        "      \"camera_angle\": \"Medium Shot\",\n"
        "      \"characters_in_scene\": \"A young man with short dark hair in a grey sweatshirt, standing calmly beside a large wall clock.\",\n"
        "      \"environment\": \"A clean modern bedroom with a large glowing wall clock showing 10:00 PM.\",\n"
        "      \"props_in_scene\": \"A large modern wall clock with crisp numbers.\",\n"
        "      \"visual_description\": \"The young man stands statically beside a large wall clock mounted on a clean bedroom wall.\",\n"
        "      \"text_to_display\": \"Raise your hand if you've tried to fix your sleep schedule by just going to bed earlier.\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    user_content = f"FULL SCRIPT:\n{script_text}\n\nTRANSCRIPT FRAMES:\n{transcript_summary}"

    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"[Director] Error creating storyboard: {e}")
        return fallback_storyboard(segments)

def fallback_storyboard(segments):
    return {
        "frames": [
            {
                "index": i,
                "camera_angle": "Wide Shot",
                "characters_in_scene": "A young man in a grey sweatshirt.",
                "environment": "Clean modern room with a wall clock.",
                "props_in_scene": "Alarm clock on a nightstand.",
                "visual_description": seg['text'],
                "text_to_display": seg['text']
            } for i, seg in enumerate(segments)
        ]
    }