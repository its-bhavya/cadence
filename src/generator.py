"""Instruction and form feedback generation using Gemini API."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def generate_instructions(exercise_name: str, signature: dict, rep_count: int) -> list[dict]:
    """Generate step-by-step exercise instructions using Gemini.

    Args:
        exercise_name: Name of the classified exercise.
        signature: Movement signature dict from extract_movement_signature().
        rep_count: Number of detected repetitions.

    Returns:
        List of step dicts with step_number, phase, instruction,
        form_cue, and breathing.

    Raises:
        ValueError: If GEMINI_API_KEY environment variable is not set.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-flash-latest")

    prompt = f"""You are a certified personal trainer writing exercise instructions.

Exercise: {exercise_name}
Reps performed: {rep_count}
Movement details:
- Primary joints moving: {', '.join(signature.get('primary_joints_moving', []))}
- Movement axis: {signature.get('movement_axis', 'unknown')}
- Range of motion: {signature.get('range_of_motion', 'unknown')}
- Symmetry: {signature.get('symmetry', 'unknown')}
- Body position: {signature.get('body_position', 'unknown')}

Write numbered step-by-step instructions for performing this exercise. Break the movement into these phases:
1. Starting Position
2. Descent/Initiation
3. Peak/Midpoint
4. Return
5. Recovery

For each step, include:
- A clear instruction in plain English
- A specific form cue (what the person should feel or focus on)
- A breathing instruction (inhale/exhale/hold)

Respond with ONLY valid JSON, no markdown or extra text. Use this exact format:
[
  {{"step_number": 1, "phase": "Starting Position", "instruction": "...", "form_cue": "...", "breathing": "..."}},
  {{"step_number": 2, "phase": "Descent/Initiation", "instruction": "...", "form_cue": "...", "breathing": "..."}},
  {{"step_number": 3, "phase": "Peak/Midpoint", "instruction": "...", "form_cue": "...", "breathing": "..."}},
  {{"step_number": 4, "phase": "Return", "instruction": "...", "form_cue": "...", "breathing": "..."}},
  {{"step_number": 5, "phase": "Recovery", "instruction": "...", "form_cue": "...", "breathing": "..."}}
]"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    try:
        steps = json.loads(raw)
    except json.JSONDecodeError:
        cleaned = raw
        if "```" in cleaned:
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        try:
            steps = json.loads(cleaned)
        except json.JSONDecodeError:
            steps = []

    return [
        {
            "step_number": s.get("step_number", i + 1),
            "phase": s.get("phase", ""),
            "instruction": s.get("instruction", ""),
            "form_cue": s.get("form_cue", ""),
            "breathing": s.get("breathing", ""),
        }
        for i, s in enumerate(steps)
    ]
