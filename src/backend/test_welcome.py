import requests

try:
    response = requests.get('http://127.0.0.1:8000/', allow_redirects=False)
    print(f"Status: {response.status_code}")
    print(f"Location: {response.headers.get('Location')}")
    print(f"Content length: {len(response.text)}")
    if response.status_code == 200:
        print("Page content (first 100 chars):")
        print(response.text[:100])
except Exception as e:
    print(f"Error: {e}")
