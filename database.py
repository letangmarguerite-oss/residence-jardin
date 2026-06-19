import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    db_url = os.getenv("DATABASE_URL")

    # Render → PostgreSQL
    if db_url is not None and db_url != "":
        return psycopg2.connect(db_url, cursor_factory=RealDictCursor)

    # Local → SQLite
    return sqlite3.connect("local.db")

def init_db():
    db_url = os.getenv("DATABASE_URL")
    is_render = db_url is not None and db_url != ""

    conn = get_connection()
    cur = conn.cursor()

    if is_render:
        # PostgreSQL
        cur.execute("""
            CREATE TABLE IF NOT EXISTS slots (
                id SERIAL PRIMARY KEY,
                resident TEXT NOT NULL,
                date TEXT NOT NULL,
                hour TEXT NOT NULL
            );
        """)
    else:
        # SQLite
        cur.execute("""
            CREATE TABLE IF NOT EXISTS slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resident TEXT NOT NULL,
                date TEXT NOT NULL,
                hour TEXT NOT NULL
            );
        """)

    conn.commit()
    cur.close()
    conn.close()
