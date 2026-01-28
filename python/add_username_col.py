import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../backend/appointments.db')

def migrate_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(appointments)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'username' not in columns:
            print("Adding 'username' column to appointments table...")
            cursor.execute("ALTER TABLE appointments ADD COLUMN username TEXT")
            print("Column added successfully.")
        else:
            print("'username' column already exists.")
            
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    migrate_db()
