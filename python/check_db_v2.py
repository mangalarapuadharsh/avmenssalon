import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.app import app, db, Appointment

def check_db():
    with app.app_context():
        count = Appointment.query.count()
        print(f"Total Appointments: {count}")
        appts = Appointment.query.all()
        for a in appts:
            print(f"- {a.date} {a.time} (User: {a.username})")

if __name__ == "__main__":
    check_db()
