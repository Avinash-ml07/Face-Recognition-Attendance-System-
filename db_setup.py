import sqlite3

def init_db(db_path='faces.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS face_images (
            img_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER,
            angle     TEXT CHECK(angle IN ('left','center','right')),
            image     BLOB,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
