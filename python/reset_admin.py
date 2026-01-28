import sqlite3
import hashlib
import os

DB_PATH = r'd:\anti\backend\appointments.db'

def reset_admin():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Ensure table exists just in case
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'customer'
            )
        ''')

        password = hashlib.sha256("admin123".encode()).hexdigest()
        
        # Check if admin exists
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        user = cursor.fetchone()
        
        if user:
            print("Admin user found. Updating password...")
            cursor.execute("UPDATE users SET password=?, role='admin' WHERE username='admin'", (password,))
        else:
            print("Admin user not found. Creating...")
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'admin')", ("admin", password))
            
        conn.commit()
        conn.close()
        print("SUCCESS: Admin credentials reset to admin / admin123")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    reset_admin()
