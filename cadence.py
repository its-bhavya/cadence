"""Cadence — auto-generate workout instructions from silent video."""

import argparse

from src.extractor import extract_frames
from src.pose import detect_poses
from src.counter import extract_joint_trajectory, count_reps, extract_movement_signature
from src.classifier import classify_exercise


def main():
    """Run the Cadence pipeline."""
    parser = argparse.ArgumentParser(description="Cadence: workout video analysis pipeline")
    parser.add_argument("--input", required=True, help="Path to input video file")
    parser.add_argument("--output", default="results", help="Output file prefix (default: results)")
    parser.add_argument("--joints", type=int, default=24, help="Joint index for rep counting (default: 24, right hip)")
    parser.add_argument("--verbose", action="store_true", help="Print each pipeline stage with timing")
    args = parser.parse_args()

    # Phase 1: Extract, detect, count
    print(f"[1/6] Extracting frames from {args.input}...")
    frames = extract_frames(args.input)

    print(f"[2/6] Running pose detection...")
    frames = detect_poses(frames)

    print(f"[3/6] Extracting joint trajectory (joint {args.joints})...")
    trajectory = extract_joint_trajectory(frames, args.joints)

    print(f"[4/6] Counting reps...")
    rep_data = count_reps(trajectory)

    # Phase 2: Classify
    print(f"[5/6] Analyzing movement signature...")
    signature = extract_movement_signature(frames)

    print(f"[6/6] Classifying exercise via Gemini...")
    classification = classify_exercise(signature, rep_data["rep_count"])

    # Summary
    valid_poses = sum(1 for f in frames if f["landmarks"] is not None)
    muscles = ", ".join(classification["muscles_worked"])
    print()
    print(f"Frames extracted:   {len(frames)}")
    print(f"Frames with pose:   {valid_poses}")
    print()
    print(f"{classification['exercise_name'].title()} ({classification['confidence']} confidence) - {rep_data['rep_count']} reps - {muscles}")


if __name__ == "__main__":
    main()
