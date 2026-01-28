import requests
import datetime

BASE_URL = "http://localhost:5000/api"
SESSION = requests.Session()

def create_today_appointments():
    print("--- Creating Appointments for TODAY ---")
    
    # Register/Login
    username = "today_client"
    password = "password123"
    SESSION.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    SESSION.post(f"{BASE_URL}/login", json={"username": username, "password": password})

    # Get today's date
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"Date: {today}")
    
    services = ["Classic Cut", "Royal Shave", "Beard Sculpting"]
    times = ["10:00", "11:00", "12:00", "13:00", "14:00"]
    
    for i, time_str in enumerate(times):
        payload = {
            "name": f"Today Customer {i+1}",
            "phone": f"555-TODAY-{i}",
            "service": services[i % len(services)],
            "date": today,
            "time": time_str
        }
        
        res = SESSION.post(f"{BASE_URL}/book", json=payload)
        
        if res.status_code == 201:
            print(f"Booked: {payload['name']} at {time_str}")
        else:
            print(f"Failed {time_str}: {res.text}")

    print("\nCheck your Admin Panel! You have 5 new Pending requests for TODAY.")
    print("Accept them to see 'Today's Work' count increase.")

if __name__ == "__main__":
    create_today_appointments()
