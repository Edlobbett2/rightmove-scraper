import requests
import json

def test_fetch_properties():
    try:
        # Fetch data from our test server
        response = requests.get('http://localhost:8000/api/properties')
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            print("Successfully fetched properties:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: Server returned status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the test server is running.")
        return False
    except json.JSONDecodeError:
        print("Error: Received invalid JSON response")
        print("Response:", response.text)
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

if __name__ == '__main__':
    test_fetch_properties() 