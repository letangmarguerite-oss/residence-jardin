import os
import psycopg2
import sqlite3
from psycopg2.extras import RealDictCursor

def get_connection():
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        return psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    else:
        return sqlite3.connect("local.db")


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS slots (
            id SERIAL PRIMARY KEY,
            resident TEXT NOT NULL,
            date TEXT NOT NULL,
            hour TEXT NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
