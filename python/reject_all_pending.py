import requests

BASE_URL = "http://localhost:5000/api"
SESSION = requests.Session()

def reject_all_pending():
    print("--- Bulk Rejecting Pending Appointments ---")
    
    # Login as Admin
    username = "bhumesh"
    password = "bhumesh@123"
    SESSION.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    
    # Fetch all appointments (requires admin session)
    # The /appointments endpoint returns a list of all appointments
    try:
        res = SESSION.get(f"http://localhost:5000/appointments")
        if res.status_code != 200:
            print(f"Failed to fetch appointments: {res.status_code}")
            return
            
        all_appts = res.json()
        pending_appts = [a for a in all_appts if a['status'] == 'pending']
        
        print(f"Found {len(pending_appts)} pending appointments out of {len(all_appts)} total.")
        
        if not pending_appts:
            print("No pending appointments to reject.")
            return

        count = 0
        for appt in pending_appts:
            url = f"{BASE_URL}/appointments/{appt['id']}/status"
            res = SESSION.put(url, json={"status": "rejected"})
            
            if res.status_code == 200:
                print(f"[{count+1}/{len(pending_appts)}] Rejected # {appt['id']} ({appt['name']})")
                count += 1
            else:
                print(f"Failed to reject #{appt['id']}: {res.text}")

        print(f"\n--- Done! Rejected {count} appointments. ---")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reject_all_pending()
