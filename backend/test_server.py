import requests
import sys

def test_server():
    try:
        # Try both localhost and 127.0.0.1
        urls = [
            'http://localhost:8080',
            'http://127.0.0.1:8080'
        ]
        
        for url in urls:
            print(f"\nTrying to connect to {url}...")
            response = requests.get(url)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_server() 