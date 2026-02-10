import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("Response:", data)
            if data["status"] == "ok" and "timestamp" in data and "dev_mode" in data:
                print("PASS: /health check OK")
                return True
            else:
                print("FAIL: /health check Missing keys")
                return False
        else:
            print(f"FAIL: /health check Status {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: /health check Connection error")
        return False

def test_date_validation():
    print("\nTesting Date Validation...")
    try:
        response = requests.get(f"{BASE_URL}/reports/dispatched", params={"date_from": "INVALID-DATE"})
        if response.status_code == 400:
            print(f"PASS: Validation caught invalid date 400")
        else:
            print(f"FAIL: Validation Status {response.status_code}")
    except Exception as e:
        print(f"FAIL: Validation test error: {e}")

if __name__ == "__main__":
    health_passed = test_health()
    if health_passed:
        test_date_validation()
    else:
        print("\nSkipping validation test because health check failed.")
