import sqlite3

conn = sqlite3.connect("garden.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS planning")

conn.commit()
conn.close()

print("Table planning supprimée.")
