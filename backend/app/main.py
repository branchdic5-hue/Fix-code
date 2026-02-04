import json
import os
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.db import connect_db, init_db, load_users, save_users, utc_now
from app.services.cdr_parser import CDRParsingError, parse_cdr
from app.services.eyecon import load_eyecon_config, search_numbers
from app.services.kml_builder import build_kml
from app.services.reports import call_statistics, day_night_analysis

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CASES_DIR = os.path.join(BASE_DIR, "cases")

app = FastAPI(title="Multi-Operator CDR Analysis")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "app", "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))


@app.on_event("startup")
def startup() -> None:
    init_db()
    os.makedirs(CASES_DIR, exist_ok=True)


@app.post("/api/login")
def login(username: str = Form(...), password: str = Form(...)):
    users = load_users().get("users", [])
    for user in users:
        if user["username"] == username and user["password"] == password:
            return {"username": username, "role": user["role"]}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/users")
def list_users():
    return load_users().get("users", [])


@app.post("/api/users")
def create_user(username: str = Form(...), password: str = Form(...), role: str = Form("analyst")):
    data = load_users()
    users = data.get("users", [])
    if any(user["username"] == username for user in users):
        raise HTTPException(status_code=400, detail="User already exists")
    users.append({"username": username, "password": password, "role": role})
    data["users"] = users
    save_users(data)
    return {"status": "created"}


@app.delete("/api/users/{username}")
def delete_user(username: str):
    data = load_users()
    users = [user for user in data.get("users", []) if user["username"] != username]
    data["users"] = users
    save_users(data)
    return {"status": "deleted"}


@app.post("/api/cases")
def create_case(case_id: str = Form(...), police_station: str = Form(...), case_date: str = Form(...)):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cases(case_id, police_station, case_date, created_at) VALUES(?,?,?,?)",
        (case_id, police_station, case_date, utc_now()),
    )
    conn.commit()
    conn.close()
    case_dir = os.path.join(CASES_DIR, case_id)
    os.makedirs(os.path.join(case_dir, "uploads"), exist_ok=True)
    return {"status": "created", "case_id": case_id}


@app.get("/api/cases")
def list_cases():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT case_id, police_station, case_date, created_at FROM cases ORDER BY created_at DESC")
    cases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cases


@app.post("/api/cases/{case_id}/upload")
def upload_cdr(
    case_id: str,
    operator: str = Form(...),
    file: UploadFile = File(...),
):
    case_dir = os.path.join(CASES_DIR, case_id)
    if not os.path.exists(case_dir):
        raise HTTPException(status_code=404, detail="Case not found")

    uploads_dir = os.path.join(case_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, file.filename)
    with open(file_path, "wb") as handle:
        handle.write(file.file.read())

    try:
        records = parse_cdr(file_path, operator)
    except CDRParsingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    conn = connect_db()
    cursor = conn.cursor()
    for record in records:
        cursor.execute(
            """
            INSERT INTO cdr_records(
                case_id, operator, a_party, b_party, call_type, direction,
                start_time, end_time, duration_sec, cell_id, lac_id, imei, imsi,
                lat, lng, location, raw_json, created_at
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                case_id,
                operator,
                record.get("a_party"),
                record.get("b_party"),
                record.get("call_type"),
                record.get("direction"),
                record.get("start_time"),
                record.get("end_time"),
                record.get("duration_sec"),
                record.get("cell_id"),
                record.get("lac_id"),
                record.get("imei"),
                record.get("imsi"),
                record.get("lat"),
                record.get("lng"),
                record.get("location"),
                record.get("raw_json"),
                utc_now(),
            ),
        )
    conn.commit()
    conn.close()

    return {"status": "uploaded", "rows": len(records)}


@app.get("/api/cases/{case_id}/cdrs")
def list_cdrs(case_id: str, limit: int = 200):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a_party, b_party, call_type, start_time, end_time, duration_sec,
               cell_id, imei, imsi, lat, lng, location
        FROM cdr_records
        WHERE case_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (case_id, limit),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


@app.get("/api/cases/{case_id}/reports/call-stats")
def report_call_stats(case_id: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cdr_records WHERE case_id = ?", (case_id,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return call_statistics(records)


@app.get("/api/cases/{case_id}/reports/day-night")
def report_day_night(case_id: str, day_start: str = "06:00", night_start: str = "18:00"):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cdr_records WHERE case_id = ?", (case_id,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return day_night_analysis(records, day_start=day_start, night_start=night_start)


@app.get("/api/cases/{case_id}/reports/tower-kml")
def report_tower_kml(case_id: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cdr_records WHERE case_id = ?", (case_id,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    kml_content = build_kml(records)
    kml_path = os.path.join(CASES_DIR, case_id, "tower_report.kml")
    with open(kml_path, "w", encoding="utf-8") as handle:
        handle.write(kml_content)
    return FileResponse(kml_path, media_type="application/vnd.google-earth.kml+xml")


@app.post("/api/cases/{case_id}/eyecon")
def eyecon_search(case_id: str, numbers: str = Form(...)):
    number_list = [number.strip() for number in numbers.split(",") if number.strip()]
    config = load_eyecon_config()
    results = search_numbers(number_list, config["api_url"], config["api_key"])
    output_path = os.path.join(CASES_DIR, case_id, "eyecon_results.json")
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    return {"status": "ok", "results": results}


@app.get("/reports/{case_id}", response_class=HTMLResponse)
async def report_dashboard(request: Request, case_id: str):
    return templates.TemplateResponse("dashboard.html", {"request": request, "case_id": case_id})


@app.get("/reports/{case_id}/call-stats", response_class=HTMLResponse)
async def report_call_stats_view(request: Request, case_id: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cdr_records WHERE case_id = ?", (case_id,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    stats = call_statistics(records)
    return templates.TemplateResponse(
        "report_call_stats.html", {"request": request, "case_id": case_id, "stats": stats}
    )


@app.get("/reports/{case_id}/day-night", response_class=HTMLResponse)
async def report_day_night_view(request: Request, case_id: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cdr_records WHERE case_id = ?", (case_id,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    analysis = day_night_analysis(records)
    return templates.TemplateResponse(
        "report_day_night.html",
        {"request": request, "case_id": case_id, "analysis": analysis},
    )


@app.get("/reports/{case_id}/tower", response_class=HTMLResponse)
async def report_tower_view(request: Request, case_id: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cdr_records WHERE case_id = ?", (case_id,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return templates.TemplateResponse(
        "report_tower.html", {"request": request, "case_id": case_id, "records": records}
    )
