# Cadence

Accessibility-first workout video analysis — paste a YouTube URL or upload a video and get structured instructions, audio narration, and form feedback in seconds.

## Requirements

- Python 3.10+
- Node 18+
- A [Gemini API key](https://aistudio.google.com/apikey)

## Backend Setup

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
uvicorn api:app --reload
```

The API runs on `http://localhost:8000` by default.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` by default.

**Both the backend and frontend must be running simultaneously.**

## What the Outputs Mean

Cadence analyzes a workout video and returns five things:

1. **Step-by-step instructions** — each exercise broken into phases with form cues, written for deaf and hard-of-hearing users
2. **Audio narration** — a spoken script read aloud via the browser's Web Speech API, designed for blind and visually impaired users
3. **Simplified version** — plain English rewording of each step for non-native speakers and neurodivergent users
4. **Muscle map + form feedback** — which muscles are worked, common mistakes, and how to fix them
5. **Workout summary** — exercise count, difficulty, and workout type at a glance

## How It Works

1. User pastes a YouTube URL or uploads a video file (MP4, WebM, MOV)
2. The backend sends the video directly to Gemini's native video understanding (no frame extraction, no pose estimation)
3. Gemini watches the full video and detects every exercise in order
4. It returns structured JSON with timestamps, instructions, form cues, and narration for each exercise
5. The backend parses and validates the JSON response
6. The frontend renders all five output types simultaneously
7. Audio narration plays via the browser's built-in Web Speech API (no paid TTS)
