"""
Helper script to find your PC's LAN IP address.
Run this to quickly get the IP you need for LAN access.
"""

import socket

def get_lan_ip():
    """Get the local LAN IP address of this machine."""
    try:
        # Create a socket and connect to an external address
        # This doesn't actually send data, just determines the route
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unable to detect IP"

if __name__ == "__main__":
    ip = get_lan_ip()
    print("=" * 60)
    print("YOUR PC'S LAN IP ADDRESS")
    print("=" * 60)
    print(f"\nIP Address: {ip}")
    print(f"\nOther PCs should access the system at:")
    print(f"http://{ip}:8000")
    print("\nUpdate script.js with:")
    print(f'const API_URL = "http://{ip}:8000";')
    print("=" * 60)
