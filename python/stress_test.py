import requests
import concurrent.futures
import time
import random
import string

BASE_URL = "http://localhost:5000/api"
NUM_USERS = 100  # Number of concurrent users to simulate
MAX_WORKERS = 20 # Number of parallel threads

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def simulate_user(user_id):
    session = requests.Session()
    username = f"stress_user_{user_id}_{random_string(4)}"
    password = "password123"
    
    print(f"[{username}] Starting simulation...")
    
    # 1. Register
    try:
        res = session.post(f"{BASE_URL}/register", json={
            "username": username, "password": password
        })
        if res.status_code != 201:
            print(f"[{username}] Registration failed: {res.text}")
            return False
    except Exception as e:
        print(f"[{username}] Registration exception: {e}")
        return False
        
    # 2. Login
    try:
        res = session.post(f"{BASE_URL}/login", json={
            "username": username, "password": password
        })
        if res.status_code != 200:
            print(f"[{username}] Login failed: {res.text}")
            return False
    except Exception as e:
        print(f"[{username}] Login exception: {e}")
        return False

    # 3. Book Appointment
    try:
        book_data = {
            "name": f"User {username}",
            "phone": "555-0100",
            "service": "Stress Cut",
            "date": "2026-06-01",
            "time": f"{random.randint(9, 17)}:00"
        }
        res = session.post(f"{BASE_URL}/book", json=book_data)
        if res.status_code != 201:
            print(f"[{username}] Booking failed: {res.text}")
            return False
    except Exception as e:
        print(f"[{username}] Booking exception: {e}")
        return False

    # 4. Get My Bookings
    try:
        res = session.get(f"{BASE_URL}/my-bookings")
        if res.status_code != 200:
            print(f"[{username}] Fetch bookings failed: {res.text}")
            return False
    except Exception as e:
        print(f"[{username}] Fetch bookings exception: {e}")
        return False
        
    print(f"[{username}] Success!")
    return True

def run_stress_test():
    start_time = time.time()
    successful_users = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Launch user simulations
        future_to_user = {executor.submit(simulate_user, i): i for i in range(NUM_USERS)}
        
        for future in concurrent.futures.as_completed(future_to_user):
            if future.result():
                successful_users += 1
                
    duration = time.time() - start_time
    print(f"\n--- Stress Test Completed ---")
    print(f"Total Users Simulated: {NUM_USERS}")
    print(f"Successful Users: {successful_users}")
    print(f"Failed Users: {NUM_USERS - successful_users}")
    print(f"Total Duration: {duration:.2f} seconds")

if __name__ == "__main__":
    run_stress_test()
