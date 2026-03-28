import numpy as np
from scipy.signal import find_peaks

JOINT_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky",
    "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index",
]

LEFT_RIGHT_PAIRS = [
    (11, 12),  # shoulders
    (13, 14),  # elbows
    (15, 16),  # wrists
    (23, 24),  # hips
    (25, 26),  # knees
    (27, 28),  # ankles
]


def extract_joint_trajectory(frames: list, joint_index: int) -> list[float]:
    """Extract the y-coordinate trajectory for a given joint across frames.

    Args:
        frames: List of frame dicts with 'landmarks' key (from detect_poses).
        joint_index: MediaPipe joint index (0-32).

    Returns:
        List of y-coordinate floats, skipping frames with no landmarks.
    """
    trajectory = []
    for frame_data in frames:
        landmarks = frame_data.get("landmarks")
        if landmarks is not None:
            trajectory.append(landmarks[joint_index]["y"])
    return trajectory


def count_reps(trajectory: list) -> dict:
    """Count exercise repetitions from a joint y-coordinate trajectory.

    Smooths the signal with a rolling average, then detects peaks and
    valleys to determine rep count.

    Args:
        trajectory: List of y-coordinate floats from extract_joint_trajectory.

    Returns:
        Dict with 'rep_count' (int), 'peaks' (list of indices),
        and 'valleys' (list of indices).
    """
    if len(trajectory) < 3:
        return {"rep_count": 0, "peaks": [], "valleys": []}

    signal = np.array(trajectory)

    # Use IQR to remove outlier influence before computing prominence
    q1, q3 = np.percentile(signal, [25, 75])
    clipped = np.clip(signal, q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1))

    # Light smoothing: small fixed window to denoise without flattening cycles
    window = max(3, min(7, len(clipped) // 40))
    kernel = np.ones(window) / window
    smoothed = np.convolve(clipped, kernel, mode="same")

    amplitude = np.max(smoothed) - np.min(smoothed)
    if amplitude == 0:
        return {"rep_count": 0, "peaks": [], "valleys": []}

    prominence = amplitude * 0.15
    distance = max(3, len(smoothed) // 60)

    peaks, _ = find_peaks(smoothed, prominence=prominence, distance=distance)
    valleys, _ = find_peaks(-smoothed, prominence=prominence, distance=distance)

    rep_count = max(len(peaks), len(valleys))

    return {
        "rep_count": rep_count,
        "peaks": peaks.tolist(),
        "valleys": valleys.tolist(),
    }


def extract_movement_signature(frames: list) -> dict:
    """Analyze the full landmark sequence to characterize the movement.

    Args:
        frames: List of frame dicts with 'landmarks' key (from detect_poses).

    Returns:
        Dict with primary_joints_moving, movement_axis, range_of_motion,
        symmetry, and body_position.
    """
    valid = [f["landmarks"] for f in frames if f.get("landmarks") is not None]
    if len(valid) < 2:
        return {
            "primary_joints_moving": [],
            "movement_axis": "vertical",
            "range_of_motion": "small",
            "symmetry": "symmetric",
            "body_position": "standing",
        }

    n_joints = len(valid[0])
    n_frames = len(valid)

    # Build arrays: (n_frames, n_joints) for x and y
    x_data = np.array([[lm["x"] for lm in frame] for frame in valid])
    y_data = np.array([[lm["y"] for lm in frame] for frame in valid])

    # --- primary_joints_moving: top joints by combined x+y variance ---
    x_var = np.var(x_data, axis=0)
    y_var = np.var(y_data, axis=0)
    total_var = x_var + y_var

    # Exclude face landmarks (0-10) — they mostly track head bob, not exercise
    body_indices = list(range(11, n_joints))
    body_var = [(i, total_var[i]) for i in body_indices]
    body_var.sort(key=lambda t: t[1], reverse=True)

    top_n = min(5, len(body_var))
    primary_joints_moving = [JOINT_NAMES[i] for i, _ in body_var[:top_n]]

    # --- movement_axis: compare aggregate x vs y variance across body joints ---
    body_x_var = sum(x_var[i] for i in body_indices)
    body_y_var = sum(y_var[i] for i in body_indices)

    if body_y_var == 0 and body_x_var == 0:
        movement_axis = "vertical"
    else:
        ratio = body_x_var / (body_x_var + body_y_var)
        if ratio < 0.3:
            movement_axis = "vertical"
        elif ratio > 0.7:
            movement_axis = "horizontal"
        else:
            movement_axis = "both"

    # --- range_of_motion: based on median joint trajectory amplitude ---
    amplitudes = []
    for i in body_indices:
        amplitudes.append(np.ptp(y_data[:, i]))
        amplitudes.append(np.ptp(x_data[:, i]))
    median_amp = np.median(amplitudes)

    if median_amp < 0.1:
        range_of_motion = "small"
    elif median_amp < 0.25:
        range_of_motion = "medium"
    else:
        range_of_motion = "large"

    # --- symmetry: correlate left vs right joint trajectories ---
    correlations = []
    for left_i, right_i in LEFT_RIGHT_PAIRS:
        if left_i >= n_joints or right_i >= n_joints:
            continue
        for data in (x_data, y_data):
            left_sig = data[:, left_i]
            right_sig = data[:, right_i]
            if np.std(left_sig) > 0 and np.std(right_sig) > 0:
                corr = np.corrcoef(left_sig, right_sig)[0, 1]
                correlations.append(corr)

    if correlations:
        mean_corr = np.mean(correlations)
        symmetry = "symmetric" if mean_corr > 0.7 else "asymmetric"
    else:
        symmetry = "symmetric"

    # --- body_position: based on median hip y-coordinate ---
    # MediaPipe normalized coords: y=0 is top of frame, y=1 is bottom
    hip_y = (y_data[:, 23] + y_data[:, 24]) / 2
    median_hip_y = np.median(hip_y)

    if median_hip_y < 0.5:
        body_position = "standing"
    elif median_hip_y < 0.75:
        body_position = "mixed"
    else:
        body_position = "ground"

    return {
        "primary_joints_moving": primary_joints_moving,
        "movement_axis": movement_axis,
        "range_of_motion": range_of_motion,
        "symmetry": symmetry,
        "body_position": body_position,
    }
