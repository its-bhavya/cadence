"""Exercise classification using Gemini API."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def classify_exercise(signature: dict, rep_count: int) -> dict:
    """Classify the exercise using Gemini based on movement signature.

    Args:
        signature: Movement signature dict from extract_movement_signature().
        rep_count: Number of detected repetitions.

    Returns:
        Dict with exercise_name, confidence, muscles_worked, and raw_response.

    Raises:
        ValueError: If GEMINI_API_KEY environment variable is not set.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-flash-latest")

    prompt = f"""You are an exercise classification expert. Based on the movement data below, identify the exercise being performed.

Movement signature:
- Primary joints moving: {', '.join(signature.get('primary_joints_moving', []))}
- Movement axis: {signature.get('movement_axis', 'unknown')}
- Range of motion: {signature.get('range_of_motion', 'unknown')}
- Symmetry: {signature.get('symmetry', 'unknown')}
- Body position: {signature.get('body_position', 'unknown')}
- Rep count: {rep_count}

Respond with ONLY valid JSON in this exact format, no markdown or extra text:
{{"exercise_name": "name of the exercise", "confidence": "high/medium/low", "muscles_worked": ["muscle1", "muscle2", "muscle3"]}}"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Try extracting JSON from markdown code block
        cleaned = raw
        if "```" in cleaned:
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            parsed = {
                "exercise_name": "unknown",
                "confidence": "low",
                "muscles_worked": [],
            }

    return {
        "exercise_name": parsed.get("exercise_name", "unknown"),
        "confidence": parsed.get("confidence", "low"),
        "muscles_worked": parsed.get("muscles_worked", []),
        "raw_response": raw,
    }
