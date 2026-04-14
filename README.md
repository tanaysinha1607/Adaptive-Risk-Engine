# Adaptive Risk Engine

## Backend (FastAPI)

### 1) Setup env

- Copy `.env.example` → `.env`
- Set `DATABASE_URL` to your Postgres connection string

### 2) Install dependencies

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3) Run API

```bash
uvicorn backend.main:app --reload
```

API will be at `http://127.0.0.1:8000` and docs at `http://127.0.0.1:8000/docs`.
