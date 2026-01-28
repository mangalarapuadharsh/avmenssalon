import sys
import os

# Add the project root to sys.path so we can import backend
sys.path.append(os.getcwd())

from backend.app import app, db, Appointment

def check_counts():
    with app.app_context():
        total = Appointment.query.count()
        pending = Appointment.query.filter_by(status='pending').count()
        confirmed = Appointment.query.filter_by(status='confirmed').count()
        rejected = Appointment.query.filter_by(status='rejected').count()
        
        print(f"Total: {total}")
        print(f"Pending: {pending}")
        print(f"Confirmed: {confirmed}")
        print(f"Rejected: {rejected}")

if __name__ == "__main__":
    check_counts()
