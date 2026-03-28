"""Cadence API — single /analyze endpoint for workout video analysis."""

print("Cadence API starting...")

from fastapi import FastAPI

app = FastAPI(title="Cadence")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
