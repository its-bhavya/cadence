"""Cadence FastAPI server."""

import os
import tempfile
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from src.extractor import extract_frames
from src.pose import detect_poses
from src.counter import extract_joint_trajectory, count_reps, extract_movement_signature
from src.classifier import classify_exercise
from src.generator import generate_instructions, generate_form_feedback
from src.output import write_skeleton_video

TEMP_DIR = os.path.join(tempfile.gettempdir(), "cadence_outputs")
os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI(title="Cadence", description="Workout video analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """Analyze an uploaded workout video through the full pipeline."""
    job_id = uuid.uuid4().hex[:12]
    video_path = os.path.join(TEMP_DIR, f"{job_id}_{file.filename}")

    try:
        with open(video_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save upload: {e}")

    try:
        # Phase 1
        frames = extract_frames(video_path)
        frames = detect_poses(frames)
        trajectory = extract_joint_trajectory(frames, 24)
        rep_data = count_reps(trajectory)

        # Phase 2
        signature = extract_movement_signature(frames)
        classification = classify_exercise(signature, rep_data["rep_count"])

        # Phase 3
        instructions = generate_instructions(
            classification["exercise_name"], signature, rep_data["rep_count"]
        )
        form_feedback = generate_form_feedback(
            classification["exercise_name"], signature
        )

        output_prefix = os.path.join(TEMP_DIR, job_id)
        skeleton_path = write_skeleton_video(frames, output_prefix)
        skeleton_filename = os.path.basename(skeleton_path)

        return {
            "exercise_name": classification["exercise_name"],
            "confidence": classification["confidence"],
            "muscles_worked": classification["muscles_worked"],
            "rep_count": rep_data["rep_count"],
            "instructions": instructions,
            "form_feedback": form_feedback,
            "skeleton_video_url": f"/video/{skeleton_filename}",
        }
    except ValueError as e:
        return JSONResponse(
            status_code=422,
            content={"message": str(e), "detail": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Pipeline error: {e}", "detail": f"Pipeline error: {e}"},
        )
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


@app.get("/video/{filename}")
def serve_video(filename: str):
    """Serve a skeleton video file from the temp directory."""
    path = os.path.join(TEMP_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path, media_type="video/mp4")
