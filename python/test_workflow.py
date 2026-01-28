import requests
import sys

BASE_URL = "http://localhost:5000/api"
SESSION = requests.Session()

def test_workflow():
    print("--- 1. Register User ---")
    try:
        SESSION.post(f"{BASE_URL}/register", json={"username": "flow_user", "password": "pw"})
    except: pass # Ignore if exists
    
    SESSION.post(f"{BASE_URL}/login", json={"username": "flow_user", "password": "pw"})
    
    print("--- 2. Book Appointment (Expect Pending) ---")
    res = SESSION.post(f"{BASE_URL}/book", json={
        "name": "Flow User", "phone": "111", "service": "Cut", "date": "2026-10-10", "time": "10:00"
    })
    appt_id = res.json().get('id')
    print(f"Booked ID: {appt_id}")
    
    res = SESSION.get(f"{BASE_URL}/my-bookings")
    status = res.json()[0]['status']
    print(f"User View Status: {status}")
    if status != 'pending':
        print("FAIL: Should be pending")
        return

    print("\n--- 3. Admin Approval ---")
    ADMIN_SESSION = requests.Session()
    ADMIN_SESSION.post(f"{BASE_URL}/login", json={"username": "bhumesh", "password": "bhumesh@123"})
    
    res = ADMIN_SESSION.put(f"{BASE_URL}/appointments/{appt_id}/status", json={"status": "confirmed"})
    print(f"Admin Action: {res.text}")
    
    print("\n--- 4. Verify Confirmation ---")
    res = SESSION.get(f"{BASE_URL}/my-bookings")
    new_status = res.json()[0]['status']
    print(f"User View Status: {new_status}")
    
    if new_status == 'confirmed':
        print("SUCCESS: Workflow Complete")
    else:
        print("FAIL: Status didn't change")

if __name__ == "__main__":
    test_workflow()
