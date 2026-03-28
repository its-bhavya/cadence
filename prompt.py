"""Gemini prompt template for workout video analysis."""


def build_prompt():
    """Return the structured prompt for Gemini workout video analysis."""
    return """Analyze this entire workout video from start to finish. Detect every distinct exercise performed, in chronological order. Include rest periods between exercises as their own entry with exercise_name "Rest" and rep_count 0. If the same exercise appears multiple times at different points in the video, treat each occurrence as a separate entry with its own index.

Respond with ONLY valid JSON matching this exact shape. No markdown, no backticks, no preamble, no explanation. Start your response with { and end with }.

{
  "workout_summary": {
    "total_duration": "string, e.g. 12:30",
    "total_exercises": "number, count of distinct exercise entries excluding rest",
    "difficulty": "one of: beginner, intermediate, advanced",
    "workout_type": "string, e.g. full body, upper body, HIIT, lower body"
  },
  "exercises": [
    {
      "index": "number, 1-based sequential order",
      "timestamp_start": "string, e.g. 0:00",
      "timestamp_end": "string, e.g. 0:45",
      "exercise_name": "string, standard exercise name or Rest",
      "confidence": "one of: high, medium, low",
      "rep_count": "number, 0 for rest periods",
      "sets": "number, observed sets in this segment",
      "muscles_worked": ["string array of primary muscles targeted"],
      "difficulty": "one of: beginner, intermediate, advanced",
      "instructions": [
        {
          "step": "number, 1-based",
          "phase": "string, e.g. starting position, lowering, lifting, hold",
          "instruction": "string, clear action description",
          "form_cue": "string, technique tip for correct form",
          "simplified": "string, plain English version for non-native speakers"
        }
      ],
      "form_feedback": [
        {
          "issue": "string, common mistake observed or likely",
          "correction": "string, how to fix it"
        }
      ],
      "narration_script": "string, a natural spoken description of this exercise suitable for audio narration for visually impaired users"
    }
  ]
}

Rules:
- Detect EVERY distinct exercise in the video, in order of appearance
- Include rest periods as separate entries with exercise_name "Rest"
- If the same exercise appears multiple times, each occurrence is a separate entry with its own index
- rep_count should reflect what is visible in the video, not a prescription
- instructions should have 2-5 steps covering the full movement
- form_feedback should list 1-3 common issues per exercise
- narration_script should be 2-4 sentences, conversational, describing the movement for someone who cannot see the video
- For rest periods, narration_script should say what just happened and what comes next
- Return ONLY the JSON object, nothing else"""


def build_strict_prompt():
    """Return the structured prompt with an appended strict JSON-only instruction."""
    return build_prompt() + "\n\nYou must respond with only raw JSON. No markdown. No explanation. Start your response with { and end with }."
