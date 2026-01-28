import requests
import random

BASE_URL = "http://localhost:5000/api"
SESSION = requests.Session()

def create_pending_booking():
    # 1. Register/Login a demo user
    username = f"demo_user_{random.randint(1000, 9999)}"
    password = "password123"
    
    print(f"Creating user: {username}")
    SESSION.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    SESSION.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    
    # 2. Book
    book_data = {
        "name": "TEST USER (Please Accept Me)",
        "phone": "999-999-9999",
        "service": "Full Service",
        "date": "2026-11-25",
        "time": "16:00"
    }
    
    res = SESSION.post(f"{BASE_URL}/book", json=book_data)
    
    if res.status_code == 201:
        print("\nSUCCESS! Booking Created.")
        print(f"Name: {book_data['name']}")
        print(f"Date: {book_data['date']} at {book_data['time']}")
        print("Go to your Admin Panel to ACCEPT it.")
    else:
        print(f"Failed to book: {res.text}")

if __name__ == "__main__":
    create_pending_booking()
