# Adaptive Risk Engine

AI-powered, real-time risk management system for a trading platform simulator.

## Live
- **Frontend (Vercel)**: `https://adaptive-risk-engine.vercel.app`
- **Backend (Render)**: `https://adaptive-risk-engine.onrender.com`

## What it does
- **Trade simulator** continuously generates fake trades (volatility spikes + high-risk scenarios).
- **Risk engine** computes a real-time risk score \(0–100\) with an explanation.
- **Anomaly detection** uses Isolation Forest (if available) and falls back to statistical z-score signals.
- **Actions engine** triggers policy actions:
  - risk > 70 → reduce leverage (simulated)
  - risk > 85 → block trades (simulated)
- **Realtime streaming** over WebSockets for live dashboard updates.

## Tech stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, WebSockets
- **Frontend**: React (Vite + TypeScript)
- **AI**: `sklearn` Isolation Forest (optional) + statistical fallback

## API
- **POST** `/trade` ingest a trade
- **GET** `/risk` current risk (includes `risk_score`, `anomaly_score`, `explanation`)
- **GET** `/metrics` system stats
- **GET** `/health` service health
- **WS** `/stream` realtime events (trades, risk, alerts)

## Local development

### Backend

#### 1) Setup environment variables
Create `./.env`:
- **`DATABASE_URL`**: Postgres SQLAlchemy URL
- **`ENABLE_SIMULATOR`**: `true` to run the background simulator, `false` to disable

Notes:
- If you use a Supabase **pooler** URL, prefer `postgresql+psycopg2://...` for stability.
- If you use a Supabase **direct** DB URL, `postgresql+psycopg://...` is fine.

#### 2) Install dependencies

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### 3) Run API

```bash
uvicorn backend.main:app --reload
```

API will be at `http://127.0.0.1:8000` and docs at `http://127.0.0.1:8000/docs`.

### Frontend

#### 1) Set environment variables
In Vercel, set:
- **`VITE_API_URL`**: Render backend URL (example: `https://adaptive-risk-engine.onrender.com`)

For local frontend dev (optional), create `frontend/.env`:
```bash
VITE_API_URL=http://127.0.0.1:8000
```

#### 2) Install + run
```bash
cd frontend
npm install
npm run dev
```

## Deployment notes
- **Render (backend)**: set `DATABASE_URL` and `ENABLE_SIMULATOR` in Render env vars.
- **Vercel (frontend)**: set `VITE_API_URL` and redeploy.
