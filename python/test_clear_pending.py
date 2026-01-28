import requests
import json
import sys

# Configuration
BASE_URL = 'http://localhost:5000'
ADMIN_USERNAME = 'bhumesh'
ADMIN_PASSWORD = 'bhumesh@123'

# 1. Login as Admin
print("Logging in as admin...")
session = requests.Session()
login_payload = {
    'username': ADMIN_USERNAME, 
    'password': ADMIN_PASSWORD
}
response = session.post(f'{BASE_URL}/api/login', json=login_payload)

if response.status_code != 200:
    print(f"Login failed: {response.text}")
    sys.exit(1)
else:
    print("Login successful.")

# 2. Check counts before (optional, but good for debug)
stats_response = session.get(f'{BASE_URL}/api/stats')
stats = stats_response.json()
print(f"Initial Pending: {stats['pending']}")

# 3. Create some dummy pending appointments to test with
# We'll use a separate session or logout to simulate a user, 
# or just use the backend code directly if easier. 
# But let's stick to API testing.

print("Creating 3 pending appointments...")
book_session = requests.Session() # New session for booking
# Register a temp user
temp_user = "temp_tester_999"
book_session.post(f'{BASE_URL}/api/register', json={'username': temp_user, 'password': 'password'})
book_session.post(f'{BASE_URL}/api/login', json={'username': temp_user, 'password': 'password'})

for i in range(3):
    data = {
        'name': f'Pending Test {i}',
        'phone': '555-0000',
        'service': 'Haircut',
        'date': '2027-01-01',
        'time': f'10:0{i}' # 10:00, 10:01, 10:02
    }
    res = book_session.post(f'{BASE_URL}/api/book', json=data)
    if res.status_code == 201:
        print(f"  Booked {data['time']}")
    elif res.status_code == 409:
        print(f"  Slot {data['time']} already booked (skipping)")
    else:
        print(f"  Failed: {res.text}")

# 4. Check stats again
stats_response = session.get(f'{BASE_URL}/api/stats')
stats = stats_response.json()
print(f"Pending before clear: {stats['pending']}")

if stats['pending'] == 0:
    print("No pending appointments to clear! Test aborted.")
    sys.exit(0)

# 5. Call Clear Pending API
print("Calling Clear Pending API...")
clear_response = session.post(f'{BASE_URL}/api/appointments/clear-pending')

if clear_response.status_code == 200:
    print(f"Success: {clear_response.json()['message']}")
else:
    print(f"Failed to clear: {clear_response.text}")
    sys.exit(1)

# 6. Verify stats
stats_response = session.get(f'{BASE_URL}/api/stats')
stats = stats_response.json()
print(f"Pending after clear: {stats['pending']}")
print(f"Rejected after clear: {stats['rejected']}")

if stats['pending'] == 0:
    print("VERIFICATION PASSED: Pending count is 0.")
else:
    print("VERIFICATION FAILED: Pending count is not 0.")
