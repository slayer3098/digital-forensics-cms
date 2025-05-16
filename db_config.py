import sqlite3

DATABASE = 'dfcms.db'  # SQLite database file

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
    conn.row_factory = sqlite3.Row  # For dict-like row access
    return conn
