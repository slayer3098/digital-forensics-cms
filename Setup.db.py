import sqlite3

def create_database():
    # Connect to SQLite database file (creates if it doesn't exist)
    conn = sqlite3.connect('dfcms.db')

    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')

    # Create cases table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE NOT NULL,
        case_name TEXT NOT NULL,
        investigator TEXT,
        evidence TEXT,
        description TEXT,
        status TEXT,
        location TEXT,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()
    print("SQLite database and tables created successfully!")

if __name__ == "__main__":
    create_database()
