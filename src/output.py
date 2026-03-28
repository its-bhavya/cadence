"""Output writers for JSON, text, and skeleton video."""

import json
import os

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark


def write_json(data: dict, output_prefix: str) -> str:
    """Write all pipeline data to a JSON file.

    Args:
        data: Dict containing all pipeline outputs.
        output_prefix: File path prefix for output.

    Returns:
        Path to the written JSON file.
    """
    path = f"{output_prefix}.json"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    # Strip non-serializable frame arrays before writing
    serializable = _make_serializable(data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)

    return path


def write_text_outputs(instructions: list, form_feedback: list, output_prefix: str) -> tuple[str, str]:
    """Write instruction and form feedback text files.

    Args:
        instructions: List of step dicts from generate_instructions().
        form_feedback: List of feedback dicts from generate_form_feedback().
        output_prefix: File path prefix for output.

    Returns:
        Tuple of (instructions_path, feedback_path).
    """
    os.makedirs(os.path.dirname(output_prefix) or ".", exist_ok=True)

    # Instructions
    instr_path = f"{output_prefix}_instructions.txt"
    with open(instr_path, "w", encoding="utf-8") as f:
        for step in instructions:
            f.write(f"Step {step['step_number']}: {step['phase']}\n")
            f.write(f"  {step['instruction']}\n")
            f.write(f"  Form cue: {step['form_cue']}\n")
            f.write(f"  Breathing: {step['breathing']}\n")
            f.write("\n")

    # Form feedback
    feedback_path = f"{output_prefix}_form_feedback.txt"
    with open(feedback_path, "w", encoding="utf-8") as f:
        for item in form_feedback:
            pose_tag = "[pose-detectable]" if item["detectable_from_pose"] else "[not pose-detectable]"
            f.write(f"* {item['issue']} {pose_tag}\n")
            f.write(f"  -> {item['correction']}\n")
            f.write("\n")

    return instr_path, feedback_path


def write_skeleton_video(frames: list, output_prefix: str) -> str:
    """Draw pose skeletons on frames and write as MP4 video.

    Args:
        frames: List of frame dicts with 'frame' and 'landmarks' keys.
        output_prefix: File path prefix for output.

    Returns:
        Path to the written MP4 file.
    """
    os.makedirs(os.path.dirname(output_prefix) or ".", exist_ok=True)
    path = f"{output_prefix}_skeleton.mp4"

    if not frames:
        return path

    drawing_utils = mp.tasks.vision.drawing_utils
    connections = mp.tasks.vision.PoseLandmarksConnections.POSE_LANDMARKS

    landmark_spec = drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3)
    connection_spec = drawing_utils.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=1)

    h, w = frames[0]["frame"].shape[:2]

    # Estimate original FPS from timestamps
    timestamps = [f["timestamp_sec"] for f in frames]
    if len(timestamps) > 1:
        avg_interval = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)
        fps = 1.0 / avg_interval if avg_interval > 0 else 30.0
    else:
        fps = 30.0

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (w, h))

    for frame_data in frames:
        canvas = frame_data["frame"].copy()
        landmarks = frame_data.get("landmarks")

        if landmarks is not None:
            landmark_list = [
                NormalizedLandmark(
                    x=lm["x"],
                    y=lm["y"],
                    z=lm["z"],
                    visibility=lm.get("visibility"),
                )
                for lm in landmarks
            ]
            drawing_utils.draw_landmarks(
                canvas,
                landmark_list,
                connections,
                landmark_drawing_spec=landmark_spec,
                connection_drawing_spec=connection_spec,
            )

        writer.write(canvas)

    writer.release()
    return path


def _make_serializable(obj):
    """Recursively convert non-serializable types for JSON output."""
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_serializable(item) for item in obj]
    if isinstance(obj, np.ndarray):
        return None  # Skip frame arrays
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    return obj
