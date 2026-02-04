# Multi-Operator CDR Analysis System

This repository contains a ready-to-run CDR Analysis system with a Python FastAPI backend and a React frontend. The system supports operator-specific parsing, case-centric storage, reporting, and Eyecon enrichment.

## Features
- Operator-specific CDR normalization for Zong, Jazz/Warid/Mobilink, Telenor, and Ufone.
- Case management with persistent SQLite storage.
- Call statistics and day/night analysis.
- Tower KML generation for Google Earth.
- Eyecon API integration with JSON output.
- HTML report templates for printing and PDF export.

## Backend Setup (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Environment variables for Eyecon:
```bash
export EYECON_API_URL="https://api.example.com/eyecon"
export EYECON_API_KEY="your-key"
```

The backend auto-creates the SQLite database and a default `admin/admin` user in `backend/data/users.json`.

## Frontend Setup (React)
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser and use the navigation links to manage cases, upload CDRs, view reports, and run Eyecon enrichment.

## Reports
HTML reports are available at:
- `http://localhost:8000/reports/{case_id}`

KML export:
- `http://localhost:8000/api/cases/{case_id}/reports/tower-kml`

## Notes
- No password hashing libraries are used; credentials are stored in plaintext as requested.
- Uploads are saved under `backend/cases/{case_id}/uploads`.
