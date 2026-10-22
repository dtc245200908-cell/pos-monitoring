
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "apartment.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS apartments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                floor INTEGER NOT NULL,
                area REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Còn trống'
                    CHECK(status IN ('Còn trống', 'Đang sử dụng'))
            )
        """)
        conn.commit()


if __name__ == "__main__":
    init_db()
    print("Da khoi tao database thanh cong!")
