import sqlite3
from datetime import datetime

def mark_attendance(name, db_path='attendance.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    # Prevent duplicate entry for same day
    c.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name, today))
    if c.fetchone() is None:
        c.execute("INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
                  (name, today, datetime.now().strftime('%H:%M:%S')))
        conn.commit()
    conn.close()
    