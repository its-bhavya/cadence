import numpy as np
from scipy.signal import find_peaks


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
