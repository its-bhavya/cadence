import os

import cv2
import numpy as np


def extract_frames(video_path: str, fps: int = 5) -> list[dict]:
    """Extract frames from a video at a target FPS.

    Opens the video with OpenCV, samples frames at the specified rate
    regardless of the source video's native FPS, and returns frame data.

    Args:
        video_path: Path to the input video file.
        fps: Target frames per second to extract. Defaults to 5.

    Returns:
        List of dicts with keys 'timestamp_sec' (float) and 'frame' (np.ndarray).

    Raises:
        ValueError: If the file doesn't exist or OpenCV can't open it.
    """
    if not os.path.isfile(video_path):
        raise ValueError(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"OpenCV cannot open video: {video_path}")

    source_fps = cap.get(cv2.CAP_PROP_FPS)
    if source_fps <= 0:
        cap.release()
        raise ValueError(f"Invalid source FPS ({source_fps}) for: {video_path}")

    frame_interval = source_fps / fps
    frames = []
    frame_index = 0
    next_sample = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index >= next_sample:
            timestamp_sec = frame_index / source_fps
            frames.append({"timestamp_sec": timestamp_sec, "frame": frame})
            next_sample += frame_interval

        frame_index += 1

    cap.release()
    return frames
