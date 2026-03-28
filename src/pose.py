import os

import mediapipe as mp
import numpy as np


_MODEL_PATH = os.path.join(os.path.dirname(__file__), os.pardir, "models", "pose_landmarker_lite.task")


def detect_poses(frames: list) -> list:
    """Run MediaPipe Pose detection on each frame.

    For each frame dict, adds a 'landmarks' key containing a list of 33 dicts
    with {x, y, z, visibility}, or None if no pose is detected.

    Args:
        frames: List of dicts with 'timestamp_sec' and 'frame' keys,
                as returned by extract_frames().

    Returns:
        The same list with 'landmarks' added to each dict.
    """
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.normpath(_MODEL_PATH)),
        num_poses=1,
        min_pose_detection_confidence=0.5,
    )

    with PoseLandmarker.create_from_options(options) as landmarker:
        for frame_data in frames:
            rgb_frame = np.ascontiguousarray(frame_data["frame"][:, :, ::-1])
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results = landmarker.detect(mp_image)

            if results.pose_landmarks and len(results.pose_landmarks) > 0:
                frame_data["landmarks"] = [
                    {
                        "x": lm.x,
                        "y": lm.y,
                        "z": lm.z,
                        "visibility": lm.visibility,
                    }
                    for lm in results.pose_landmarks[0]
                ]
            else:
                frame_data["landmarks"] = None

    return frames
