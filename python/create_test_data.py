import requests
import datetime
import random
import sys

# Configuration
BASE_URL = 'http://localhost:5000'

def create_appointments(count=15):
    print(f"Generating {count} pending appointments...")
    
    # Register a dummy user for bookings
    user_data = {'username': 'bulk_tester', 'password': 'password123'}
    requests.post(f'{BASE_URL}/api/register', json=user_data)
    
    # Login
    session = requests.Session()
    login_res = session.post(f'{BASE_URL}/api/login', json=user_data)
    if login_res.status_code != 200:
        print("Login failed")
        return

    success_count = 0
    attempts = 0
    
    # Start from tomorrow to avoid "past" issues if any validation exists
    base_date = datetime.date.today() + datetime.timedelta(days=1)
    
    while success_count < count and attempts < 100:
        attempts += 1
        
        # Randomize time to avoid conflicts
        day_offset = random.randint(0, 5)
        current_date = base_date + datetime.timedelta(days=day_offset)
        hour = random.randint(9, 17)
        minute = random.choice(['00', '15', '30', '45'])
        time_str = f"{hour:02d}:{minute}"
        date_str = current_date.strftime("%Y-%m-%d")
        
        data = {
            'name': f'Visitor {success_count + 1}',
            'phone': f'555-01{success_count:02d}',
            'service': random.choice(['Haircut', 'Beard Trim', 'Full Service', 'Facial']),
            'date': date_str,
            'time': time_str
        }
        
        res = session.post(f'{BASE_URL}/api/book', json=data)
        
        if res.status_code == 201:
            print(f"  [OK] Booked: {date_str} {time_str} - {data['name']}")
            success_count += 1
        else:
            # Likely conflict, just retry
            pass

    print(f"\nSuccessfully created {success_count} pending appointments.")

if __name__ == "__main__":
    create_appointments()
