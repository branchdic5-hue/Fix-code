import json
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "cdr_system.db")
USERS_PATH = os.path.join(DATA_DIR, "users.json")


def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def connect_db() -> sqlite3.Connection:
    ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    ensure_data_dir()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT UNIQUE NOT NULL,
            police_station TEXT NOT NULL,
            case_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cdr_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            operator TEXT NOT NULL,
            a_party TEXT,
            b_party TEXT,
            call_type TEXT,
            direction TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_sec INTEGER,
            cell_id TEXT,
            lac_id TEXT,
            imei TEXT,
            imsi TEXT,
            lat REAL,
            lng REAL,
            location TEXT,
            raw_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(case_id)
        )
        """
    )
    conn.commit()
    conn.close()


def load_users() -> dict:
    ensure_data_dir()
    if not os.path.exists(USERS_PATH):
        seed = {
            "users": [
                {
                    "username": "admin",
                    "password": "admin",
                    "role": "admin"
                }
            ]
        }
        with open(USERS_PATH, "w", encoding="utf-8") as handle:
            json.dump(seed, handle, indent=2)
    with open(USERS_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_users(payload: dict) -> None:
    ensure_data_dir()
    with open(USERS_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def utc_now() -> str:
    return datetime.utcnow().isoformat()
