import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor
    )

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
