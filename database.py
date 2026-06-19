import psycopg2
import os
from urllib.parse import urlparse

# Récupère l'URL de la base Render depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    result = urlparse(DATABASE_URL)

    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port

    return psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port,
        sslmode="require"
    )

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS slots (
            id SERIAL PRIMARY KEY,
            resident TEXT NOT NULL,
            date TEXT NOT NULL,
            hour TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
