import sqlite3

conn = sqlite3.connect("ecoswap.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_name TEXT NOT NULL,
    description TEXT NOT NULL
)
""")

# SWAP REQUESTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS swap_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id INTEGER,
    owner_id INTEGER,
    product_id INTEGER,
    status TEXT DEFAULT 'Pending'
)
""")
conn.commit()
conn.close()

print("Database and users table created successfully!")