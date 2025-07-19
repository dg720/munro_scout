import json
import sqlite3

data = json.load(open("munro_descriptions.json"))
conn = sqlite3.connect("db.sqlite")
c = conn.cursor()

c.execute("""
  CREATE TABLE IF NOT EXISTS munros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, summary TEXT, distance REAL,
    time REAL, grade INTEGER, bog INTEGER, start TEXT
  )
""")

for m in data:
    c.execute(
        "INSERT INTO munros (name, summary, distance, time, grade, bog, start) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            m["name"],
            m["summary"],
            m["distance"],
            m["time"],
            m["grade"],
            m["bog"],
            m["start"],
        ),
    )

conn.commit()
