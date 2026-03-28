"""Cadence — auto-generate workout instructions from silent video."""

import argparse

from src.extractor import extract_frames
from src.pose import detect_poses
from src.counter import extract_joint_trajectory, count_reps, extract_movement_signature
from src.classifier import classify_exercise
from src.generator import generate_instructions, generate_form_feedback
from src.output import write_json, write_text_outputs, write_skeleton_video


def main():
    """Run the Cadence pipeline."""
    parser = argparse.ArgumentParser(description="Cadence: workout video analysis pipeline")
    parser.add_argument("--input", required=True, help="Path to input video file")
    parser.add_argument("--output", default="results", help="Output file prefix (default: results)")
    parser.add_argument("--joints", type=int, default=24, help="Joint index for rep counting (default: 24, right hip)")
    parser.add_argument("--verbose", action="store_true", help="Print each pipeline stage with timing")
    args = parser.parse_args()

    # Phase 1: Extract, detect, count
    print(f"[1/9] Extracting frames from {args.input}...")
    frames = extract_frames(args.input)

    print(f"[2/9] Running pose detection...")
    frames = detect_poses(frames)

    print(f"[3/9] Extracting joint trajectory (joint {args.joints})...")
    trajectory = extract_joint_trajectory(frames, args.joints)

    print(f"[4/9] Counting reps...")
    rep_data = count_reps(trajectory)

    # Phase 2: Classify
    print(f"[5/9] Analyzing movement signature...")
    signature = extract_movement_signature(frames)

    print(f"[6/9] Classifying exercise via Gemini...")
    classification = classify_exercise(signature, rep_data["rep_count"])

    # Phase 3: Generate + write outputs
    print(f"[7/9] Generating instructions via Gemini...")
    instructions = generate_instructions(
        classification["exercise_name"], signature, rep_data["rep_count"]
    )

    print(f"[8/9] Generating form feedback via Gemini...")
    form_feedback = generate_form_feedback(
        classification["exercise_name"], signature
    )

    print(f"[9/9] Writing output files...")
    skeleton_path = write_skeleton_video(frames, args.output)
    print(f"  -> {skeleton_path}")

    valid_poses = sum(1 for f in frames if f["landmarks"] is not None)
    pipeline_data = {
        "input_video": args.input,
        "frames_extracted": len(frames),
        "frames_with_pose": valid_poses,
        "joint_index": args.joints,
        "rep_data": rep_data,
        "signature": signature,
        "classification": classification,
        "instructions": instructions,
        "form_feedback": form_feedback,
    }

    json_path = write_json(pipeline_data, args.output)
    print(f"  -> {json_path}")

    instr_path, feedback_path = write_text_outputs(instructions, form_feedback, args.output)
    print(f"  -> {instr_path}")
    print(f"  -> {feedback_path}")

    # Summary
    muscles = ", ".join(classification["muscles_worked"])
    print()
    print(f"{classification['exercise_name'].title()} ({classification['confidence']} confidence) - {rep_data['rep_count']} reps - {muscles}")


if __name__ == "__main__":
    main()
