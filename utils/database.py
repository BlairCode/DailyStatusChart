import sqlite3
import os
import datetime
from .constants import BASE_DIR 

DB_PATH = os.path.join(BASE_DIR, "data/status.db")

def get_today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def init_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_status (
                date TEXT PRIMARY KEY,
                score REAL,
                title TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attributes (
                date TEXT,
                attr_name TEXT,
                attr_score REAL,
                total_score REAL,
                PRIMARY KEY (date, attr_name)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS factors (
                date TEXT,
                attr_name TEXT,
                factor_name TEXT,
                factor_score REAL,
                factor_weight REAL,
                PRIMARY KEY (date, attr_name, factor_name)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                date TEXT,
                attr_name TEXT,
                event TEXT,
                PRIMARY KEY (date, attr_name)
            )
        """)
        conn.commit()