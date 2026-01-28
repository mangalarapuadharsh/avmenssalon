import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../backend/appointments.db')

def update_admin():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        username = "bhumesh"
        password = hashlib.sha256("bhumesh@123".encode()).hexdigest()
        
        # Check if 'bhumesh' already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"User '{username}' already exists. Updating password...")
            cursor.execute("UPDATE users SET password = ?, role = 'admin' WHERE username = ?", (password, username))
        else:
            # Check for old admin/root to replace, or insert new
            cursor.execute("SELECT * FROM users WHERE role = 'admin'")
            old_admin = cursor.fetchone()
            
            if old_admin:
                print(f"Renaming old admin '{old_admin[1]}' to '{username}'...")
                cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, old_admin[0]))
            else:
                print(f"Creating new admin '{username}'...")
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'admin')", (username, password))
        
        conn.commit()
        conn.close()
        print("Success! Admin credentials updated to bhumesh / bhumesh@123")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update_admin()
