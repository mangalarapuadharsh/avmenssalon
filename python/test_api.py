import requests
import json

BASE_URL = "http://localhost:5000/api"
SESSION = requests.Session()

def test_api():
    print("--- 1. Registering 'testuser' ---")
    res = SESSION.post(f"{BASE_URL}/register", json={
        "username": "testuser", "password": "password123"
    })
    print(f"Status: {res.status_code}, Response: {res.text}")
    
    print("\n--- 2. Logging in ---")
    res = SESSION.post(f"{BASE_URL}/login", json={
        "username": "testuser", "password": "password123"
    })
    print(f"Status: {res.status_code}, Response: {res.text}")
    print(f"Cookies: {SESSION.cookies.get_dict()}")
    
    if res.status_code == 200:
        print("\n--- 3. Checking Current User ---")
        res = SESSION.get(f"{BASE_URL}/current_user")
        print(f"User: {res.json()}")

        print("\n--- 4. Booking Appointment ---")
        book_data = {
            "name": "Test User",
            "phone": "555-0199",
            "service": "Royal Shave",
            "date": "2026-05-20",
            "time": "14:00"
        }
        res = SESSION.post(f"{BASE_URL}/book", json=book_data)
        print(f"Status: {res.status_code}, Response: {res.text}")
        
        print("\n--- 5. Fetching My Bookings ---")
        res = SESSION.get(f"{BASE_URL}/my-bookings")
        print(f"Status: {res.status_code}, History: {res.text}")
        
        print("\n--- 6. Logout ---")
        res = SESSION.post(f"{BASE_URL}/logout")
        print(f"Status: {res.status_code}")
        
    else:
        print("Login failed, skipping authenticated steps.")

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"Test Failed: {e}")
