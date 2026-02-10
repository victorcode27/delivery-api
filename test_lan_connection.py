"""
Quick LAN connectivity test for Delivery Route System
Run this on OTHER PCs (not the host) to verify they can reach the API server
"""

import requests
import sys

def test_lan_connection(host_ip):
    """Test if we can reach the API server from this PC"""
    
    print("=" * 60)
    print("LAN Connectivity Test - Delivery Route System")
    print("=" * 60)
    print()
    
    base_url = f"http://{host_ip}:8000"
    
    # Test 1: Health endpoint
    print(f"[1/3] Testing API health endpoint...")
    print(f"      URL: {base_url}/health")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"      ✅ SUCCESS - Server is reachable")
            print(f"      Status: {data.get('status')}")
            print(f"      Dev Mode: {data.get('dev_mode')}")
        else:
            print(f"      ❌ FAILED - HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"      ❌ FAILED - Connection refused")
        print(f"      Possible causes:")
        print(f"         - Server not running on host PC")
        print(f"         - Firewall blocking port 8000")
        print(f"         - Wrong IP address")
        return False
    except requests.exceptions.Timeout:
        print(f"      ❌ FAILED - Connection timeout")
        return False
    except Exception as e:
        print(f"      ❌ FAILED - {str(e)}")
        return False
    
    print()
    
    # Test 2: Invoices endpoint
    print(f"[2/3] Testing invoices endpoint...")
    print(f"      URL: {base_url}/invoices")
    try:
        response = requests.get(f"{base_url}/invoices", timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"      ✅ SUCCESS - Found {count} invoices")
        else:
            print(f"      ❌ FAILED - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"      ❌ FAILED - {str(e)}")
        return False
    
    print()
    
    # Test 3: Frontend access
    print(f"[3/3] Testing frontend access...")
    print(f"      URL: {base_url}/")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print(f"      ✅ SUCCESS - Frontend is accessible")
        else:
            print(f"      ❌ FAILED - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"      ❌ FAILED - {str(e)}")
        return False
    
    print()
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print(f"You can now access the system at: {base_url}")
    print()
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_lan_connection.py <HOST_IP>")
        print("Example: python test_lan_connection.py 192.168.0.29")
        print()
        host_ip = input("Enter the host PC's IP address: ").strip()
    else:
        host_ip = sys.argv[1]
    
    if not host_ip:
        print("Error: No IP address provided")
        sys.exit(1)
    
    success = test_lan_connection(host_ip)
    sys.exit(0 if success else 1)
