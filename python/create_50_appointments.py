import requests
import datetime
import random

BASE_URL = "http://localhost:5000/api"
SESSION = requests.Session()

def create_50_appointments():
    print("--- Generating 50 Appointments ---")
    
    # Register/Login a dummy user for booking
    username = "bulk_booker"
    password = "password123"
    SESSION.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    SESSION.post(f"{BASE_URL}/login", json={"username": username, "password": password})

    start_date = datetime.date(2027, 1, 1) # Future date
    services = ["Classic Cut", "Royal Shave", "Beard Sculpting", "Full Service"]
    
    count = 0
    day_offset = 0
    
    while count < 50:
        current_date = start_date + datetime.timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Book slots from 9:00 to 17:00 (8 slots per day)
        for hour in range(9, 18):
            if count >= 50:
                break
                
            time_str = f"{hour:02d}:00"
            service = random.choice(services)
            name = f"Test Client {count + 1}"
            
            payload = {
                "name": name,
                "phone": f"555-00{count:02d}",
                "service": service,
                "date": date_str,
                "time": time_str
            }
            
            res = SESSION.post(f"{BASE_URL}/book", json=payload)
            
            if res.status_code == 201:
                print(f"[{count+1}/50] Booked: {name} on {date_str} at {time_str}")
                count += 1
            else:
                print(f"Skipped {date_str} {time_str}: {res.text}")
                
        day_offset += 1

    print("\n--- Done! 50 Appointments Created ---")

if __name__ == "__main__":
    create_50_appointments()
