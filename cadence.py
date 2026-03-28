"""Cadence — auto-generate workout instructions from silent video."""

import argparse

from src.extractor import extract_frames
from src.pose import detect_poses
from src.counter import extract_joint_trajectory, count_reps


def main():
    """Run the Cadence pipeline."""
    parser = argparse.ArgumentParser(description="Cadence: workout video analysis pipeline")
    parser.add_argument("--input", required=True, help="Path to input video file")
    parser.add_argument("--output", default="results", help="Output file prefix (default: results)")
    parser.add_argument("--joints", type=int, default=24, help="Joint index for rep counting (default: 24, right hip)")
    parser.add_argument("--verbose", action="store_true", help="Print each pipeline stage with timing")
    args = parser.parse_args()

    print(f"[1/4] Extracting frames from {args.input}...")
    frames = extract_frames(args.input)

    print(f"[2/4] Running pose detection...")
    frames = detect_poses(frames)

    print(f"[3/4] Extracting joint trajectory (joint {args.joints})...")
    trajectory = extract_joint_trajectory(frames, args.joints)

    print(f"[4/4] Counting reps...")
    rep_data = count_reps(trajectory)

    valid_poses = sum(1 for f in frames if f["landmarks"] is not None)
    print()
    print(f"Frames extracted:   {len(frames)}")
    print(f"Frames with pose:   {valid_poses}")
    print(f"Rep count:          {rep_data['rep_count']}")


if __name__ == "__main__":
    main()
