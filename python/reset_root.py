import sqlite3
import hashlib
import os

DB_PATH = r'd:\anti\backend\appointments.db'

def reset_admin_root():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        password = hashlib.sha256("root".encode()).hexdigest()
        
        # Check if admin exists
        cursor.execute("SELECT * FROM users WHERE username='root'")
        user = cursor.fetchone()
        
        if user:
            print("Root user found. Resetting password...")
            cursor.execute("UPDATE users SET password=?, role='admin' WHERE username='root'", (password,))
        else:
            print("Creating root admin user...")
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'admin')", ("root", password))
            
        conn.commit()
        conn.close()
        print("SUCCESS: Credentials set to root / root")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    reset_admin_root()
