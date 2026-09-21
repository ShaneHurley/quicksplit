# QuickSplit

Adaptive flashcards for high school and college — React UI in the browser, FastAPI + SQLite on your machine. Miss a card and it comes back in about 10–20 minutes (scales with set size); long-term reviews use FSRS.

Architecture details: [docs/ARCHITECTURE_BLUEPRINT.md](docs/ARCHITECTURE_BLUEPRINT.md).

## 60-second local demo

**Requirements:** Node 20+ (22.12+ preferred), Python 3.9+. Frontend is pinned to **Vite 6** for reliable local builds.

```bash
# 1) Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2) Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open the Vite URL (usually http://127.0.0.1:5173). API lives at http://127.0.0.1:8000.

Windows PowerShell backend activate: `.\backend\.venv\Scripts\Activate.ps1`

## Repo layout

| Path | Role |
|------|------|
| `frontend/` | React + Vite + TypeScript SPA |
| `backend/` | FastAPI, SQLAlchemy, FSRS services |
| `docs/` | Blueprint and design notes |
| `scripts/` | Run / package helpers (later phases) |

## Phase status

- [x] Phase 0 — Monorepo hygiene
- [x] Phase 1 — ORM models + schemas
- [x] Phase 2 — FSRS + learning steps + co-occurrence
- [x] Phase 3 — REST API
- [x] Phase 4 — Clay UI shell
- [x] Phase 5 — Decks CRUD
- [x] Phase 6 — Study session
- [ ] Phase 7 — PyInstaller packaging
