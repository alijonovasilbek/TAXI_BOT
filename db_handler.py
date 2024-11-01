import sqlite3
from config import DATABASE_PATH

class DatabaseHandler:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            # Create a table for storing admin credentials
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
    
    def register_admin(self, username: str, password: str):
        """Register a new admin."""
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO admin (username, password) VALUES (?, ?)",
                    (username, password)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def check_admin_credentials(self, username: str, password: str):
        """Check if the provided credentials match those in the database."""
        result = self.conn.execute(
            "SELECT * FROM admin WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        return result is not None
