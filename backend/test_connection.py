import requests
try:
    response = requests.post('http://localhost:5000/api/verify-code', json={'code': '0000'})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
