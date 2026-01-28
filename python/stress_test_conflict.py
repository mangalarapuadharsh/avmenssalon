import requests
import concurrent.futures
import time
import random
import string

BASE_URL = "http://localhost:5000/api"
NUM_USERS = 300
MAX_WORKERS = 100  # High parallelism to hit "same time"
TARGET_DATE = "2026-12-31"
TARGET_TIME = "10:00"

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def simulate_conflict_user(user_id):
    session = requests.Session()
    username = f"conflict_user_{user_id}_{random_string(4)}"
    password = "password123"
    
    # 1. Register
    try:
        session.post(f"{BASE_URL}/register", json={
            "username": username, "password": password
        })
    except:
        return "Registration Error"

    # 2. Login
    try:
        res = session.post(f"{BASE_URL}/login", json={
            "username": username, "password": password
        })
        if res.status_code != 200:
            return "Login Failed"
    except:
        return "Login Error"

    # 3. Book SAME Slot
    try:
        book_data = {
            "name": f"Conflict User {user_id}",
            "phone": "555-9999",
            "service": "Conflict Cut",
            "date": TARGET_DATE,
            "time": TARGET_TIME
        }
        res = session.post(f"{BASE_URL}/book", json=book_data)
        if res.status_code == 201:
            return "Booked"
        elif res.status_code == 500:
            return "Server Error (500)"
        else:
            return f"Failed ({res.status_code})"
    except Exception as e:
        return f"Exception: {e}"

def run_conflict_test():
    print(f"--- Starting Conflict Test: {NUM_USERS} users targeting {TARGET_DATE} {TARGET_TIME} ---")
    start_time = time.time()
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_user = {executor.submit(simulate_conflict_user, i): i for i in range(NUM_USERS)}
        
        for future in concurrent.futures.as_completed(future_to_user):
            res = future.result()
            results[res] = results.get(res, 0) + 1
            
    duration = time.time() - start_time
    print(f"\n--- Conflict Test Completed in {duration:.2f}s ---")
    print("Results breakdown:")
    for key, count in results.items():
        print(f"  {key}: {count}")

if __name__ == "__main__":
    run_conflict_test()
