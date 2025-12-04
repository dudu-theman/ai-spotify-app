# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered lofi music generation app with React frontend and Flask backend. Users generate custom instrumental tracks using natural language prompts via the Suno API, with Claude AI generating song titles. Songs are stored in AWS S3 and managed through PostgreSQL.

## Architecture

### Frontend (React + Vite)
- **Location**: `/frontend`
- **Stack**: React 19, React Router, Vite build tool
- **State Management**: React Context API via `AudioPlayerContext.jsx` for global audio playback state
- **Key Components**:
  - `App.jsx`: Main routing, search orchestration, async song generation polling (2s intervals)
  - `MusicPlayer.jsx`: Fixed-position bottom play bar with progress controls
  - `AudioPlayerContext.jsx`: Centralized audio state (currentSong, isPlaying, playback controls via `audioRef`)
  - Pages: `AuthPage` (login/signup), `HomePage`, `ShowSongs` (private/public song libraries)

### Backend (Flask)
- **Location**: `/backend`
- **Entry Point**: `app.py` (runs on port 5000 by default, configurable via `PORT` env var)
- **Database Models** (SQLAlchemy):
  - `Users`: Basic auth (id, username, password) - **Note: passwords stored unhashed currently**
  - `AISong`: Generated tracks (id, title, audio_url, song_id, user_id nullable for public songs)
  - `Task`: Async job tracking (task_id primary key, user_id, status: pending/complete/error)
- **Key Endpoints**:
  - `POST /generate?q=<prompt>`: Initiates song generation, returns task_id (requires login)
  - `POST /callback`: Suno webhook that downloads MP3 from Suno, uploads to S3, updates DB
  - `GET /task_status/<task_id>`: Frontend polls this (2s intervals) for generation status
  - `GET /api/songs/private`: User's songs (requires login via session)
  - `GET /api/songs/public`: Public song library (user_id=NULL songs)
  - `POST /login`, `POST /signup`, `POST /logout`: Session-based auth
- **External Services**:
  - Suno API: Music generation via `helper_functions/song_maker.py`
  - Claude AI: Title generation using `claude-3-haiku-20240307` model
  - AWS S3: MP3 storage with public-read URLs
- **Session Management**: Flask sessions with `SameSite=None`, `Secure=True` for cross-origin support

### Song Generation Flow
1. User submits prompt → `POST /generate?q=<prompt>`
2. Backend calls `make_song(query)` in `helper_functions/song_maker.py`:
   - Calls `make_title_name()` using Claude API to generate song title
   - POSTs to Suno API with prompt, title, and callback URL (hardcoded to Render backend)
3. Returns task_id immediately, frontend starts polling `/task_status/<task_id>` every 2s
4. When Suno generation completes, Suno hits `POST /callback` with song data
5. Backend downloads MP3 from Suno URL, uploads to S3 with UUID filename, creates AISong record, marks Task complete
6. Frontend poll detects "complete" status, shows alert, stops polling

## Development Commands

### Frontend
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Start dev server (http://localhost:5173)
npm run build        # Production build (output to dist/)
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

### Backend
```bash
cd backend
pip install -r ../requirements.txt    # Install from root requirements.txt
python app.py                         # Run Flask server (port 5000)
```

**Important**: Use root `requirements.txt` for full backend dependencies. `backend/requirements.txt` is a subset.

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push/PR to main:
- **Frontend**: ESLint, build check
- **Backend**: Black (formatting), Flake8 (linting + code quality), Bandit (security scan), syntax check

Run locally:
```bash
# Frontend
cd frontend && npm run lint && npm run build

# Backend (install dev tools first: pip install flake8 black bandit)
cd backend
black --check .
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
bandit -r . -ll --skip B101
python -m py_compile app.py helper_functions/*.py
```

## Environment Variables

### Backend (.env in root)
- `SUNO_API_KEY`: Suno music generation API key
- `ANTHROPIC_API_KEY`: Claude AI API key for title generation
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_BUCKET_NAME`: S3 storage config
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:pass@host/dbname`)
- `FLASK_SECRET_KEY`: Flask session signing key

### Frontend (frontend/.env)
- `VITE_BACKEND_URL`: Backend API base URL (defaults to http://localhost:5000 if not set)
- `VITE_API_KEY`, `VITE_AUTH_DOMAIN`, etc.: Firebase config (not currently used in auth flow)

**Security**: Root `.env` contains production secrets, must be in `.gitignore`.

## Database Management

- Tables auto-created on app startup via `db.create_all()` in `app.py` (line 66-67)
- To reset database: uncomment `db.drop_all()` line mentioned in comments (not currently present in code)
- No migrations setup; schema changes require manual DB updates

## Deployment

- **Frontend**: Vercel (config in `frontend/vercel.json`)
- **Backend**: Render (uses `Procfile: web: python app.py`)
- **CORS**: Backend allows `localhost:5173`, `https://lofi-app-dc75.onrender.com`, `https://ai-spotify-app.vercel.app`
- **Callback URL**: Hardcoded in `song_maker.py:39` to `https://lofi-app-dc75.onrender.com/callback`

## Code Patterns

- **Async Operations**: Frontend uses polling (2s intervals) instead of WebSockets for task status
- **Error Handling**: Backend callbacks check for existing `song_id` before inserting (idempotent)
- **Audio Context**: Always use `useAudioPlayer()` hook for playback control, never instantiate new Audio objects
- **API Calls**: Always include `credentials: "include"` for session cookie support
- **Styling**: Inline styles throughout (no CSS modules, Tailwind, or separate CSS files)
- **Session Auth**: Backend uses Flask sessions with `g.current_user` set in `@app.before_request`

## Known Issues / Development Notes

From code inspection:
1. Passwords stored unhashed in database (Users model, `app.py:56`)
2. Frontend `disabled` prop on SearchBar prevents concurrent song generation
3. Basic alert() used for notifications (no toast/notification UI)
4. `song_maker.py` has debug print statement at line 62 that executes on import
5. Callback URL hardcoded to production Render URL in `song_maker.py`, not configurable via env var
6. Firebase auth configured in frontend but not used (session auth is backend-only)
