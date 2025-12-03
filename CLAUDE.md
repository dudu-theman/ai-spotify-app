# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered lofi music generation app with React frontend and Flask backend. Users can generate custom instrumental tracks using natural language prompts via the Suno API, with Claude AI generating song titles. Songs are stored in AWS S3 and managed through PostgreSQL.

## Architecture

### Frontend (React + Vite)
- **Location**: `/frontend`
- **Framework**: React 19 with React Router for routing
- **State Management**: React Context API (`AudioPlayerContext.jsx`) for global audio playback
- **Authentication**: Firebase Auth (config in `src/firebase.js`)
- **Key Components**:
  - `App.jsx`: Main routing and search orchestration, handles async song generation polling
  - `MusicPlayer.jsx`: Bottom play bar (fixed position) with progress controls
  - `AudioPlayerContext.jsx`: Centralized audio state (currentSong, isPlaying, playback controls)
  - Pages: `AuthPage`, `HomePage`, `ShowSongs` (private/public song libraries)

### Backend (Flask)
- **Location**: `/backend`
- **Database**: PostgreSQL via SQLAlchemy with three models:
  - `Users`: Basic auth (username/password, no hashing currently)
  - `AISong`: Generated tracks with S3 URLs, linked to users
  - `Task`: Tracks async song generation status (pending/complete/error)
- **Key Endpoints**:
  - `POST /generate?q=<prompt>`: Initiates song generation, returns task_id
  - `POST /callback`: Suno webhook that downloads MP3, uploads to S3, updates DB
  - `GET /task_status/<task_id>`: Frontend polls this for generation status
  - `GET /api/songs/private`: User's songs (requires login)
  - `GET /api/songs/public`: Public song library (user_id=NULL)
- **External Services**:
  - Suno API: Music generation (via `helper_functions/song_maker.py`)
  - Claude AI: Title generation using Haiku model
  - AWS S3: MP3 storage with public URLs
- **Session Management**: Flask sessions with secure cookies (SameSite=None for cross-origin)

### Song Generation Flow
1. User submits prompt → `POST /generate` → calls `make_song(query)`
2. `make_song()` uses Claude to generate title, then calls Suno API with callback URL
3. Returns task_id immediately, frontend starts polling `/task_status/<task_id>`
4. When generation completes, Suno hits `POST /callback`
5. Backend downloads MP3, uploads to S3, creates AISong record, updates Task status
6. Frontend poll detects "complete" status, shows alert

## Development Commands

### Frontend
```bash
cd frontend
npm install              # Install dependencies
npm run dev              # Start dev server (http://localhost:5173)
npm run build            # Production build
npm run lint             # Run ESLint
npm run preview          # Preview production build
```

### Backend
```bash
cd backend
pip install -r requirements.txt  # Install dependencies (use root requirements.txt for full deps)
python app.py            # Run Flask server (default port 5000)
```

**Note**: Main `requirements.txt` is at project root and includes all Python dependencies. Backend has its own subset in `backend/requirements.txt`.

## Environment Variables

### Backend (.env in root)
- `SUNO_API_KEY`: Suno music generation API
- `ANTHROPIC_API_KEY`: Claude AI for title generation
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_BUCKET_NAME`: S3 storage
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_SECRET_KEY`: Session signing

### Frontend (frontend/.env)
- `VITE_BACKEND_URL`: Backend API base URL (default: http://localhost:5000)
- `VITE_API_KEY`, `VITE_AUTH_DOMAIN`, etc.: Firebase config

**Security Note**: The root `.env` file contains production secrets and should be in `.gitignore`.

## Database Management

Flask app auto-creates tables on startup via `db.create_all()` in app context. To reset database, uncomment `db.drop_all()` in `app.py:63`.

## Deployment

- **Frontend**: Vercel (`vercel.json` configured)
- **Backend**: Render (Heroku-compatible, uses `Procfile`)
- **CORS**: Backend whitelists localhost:5173, Render backend URL, and Vercel frontend URL

## Known Issues / TODO

From `app.py:262-265`:
1. Disable song creation while one is already in process (currently frontend disables SearchBar via `disabled` prop)
2. Create alert for when song is generating (basic alert implemented)
3. Add library of public songs (partially implemented via `/api/songs/public`)

## Code Patterns

- **Async Operations**: Frontend uses polling pattern (2s intervals) instead of WebSockets
- **Error Handling**: Backend callbacks are idempotent (check existing song_id before inserting)
- **Audio Context**: Use `useAudioPlayer()` hook anywhere to control playback, don't instantiate new Audio objects
- **API Calls**: Always include `credentials: "include"` for session cookies
- **Styling**: Inline styles used throughout (no CSS modules or Tailwind)
