# LAN Access Configuration Guide

## Step 1: Find Your PC's LAN IP Address

**Windows Command:**
```cmd
ipconfig
```

Look for **IPv4 Address** under your active network adapter (Wi-Fi or Ethernet).
Example: `192.168.1.15`

---

## Step 2: Backend Configuration Changes

### BEFORE (Localhost Only):
```python
if __name__ == "__main__":
    logger.info("Starting Invoice API server on http://localhost:8000")
    print("Starting Invoice API server on http://localhost:8000")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

### AFTER (LAN Accessible):
```python
# --- LAN Configuration ---
LAN_MODE = True  # Set to False for localhost-only
PRODUCTION_MODE = False  # Safety check

if __name__ == "__main__":
    # Safety check: prevent accidental public exposure
    if PRODUCTION_MODE and LAN_MODE:
        print("ERROR: Cannot run in LAN mode when PRODUCTION_MODE is enabled!")
        print("Set PRODUCTION_MODE = False or LAN_MODE = False")
        exit(1)
    
    host = "0.0.0.0" if LAN_MODE else "127.0.0.1"
    port = 8000
    
    if LAN_MODE:
        print("=" * 60)
        print("WARNING: Server running in LAN MODE")
        print("Other devices on your network CAN access this server")
        print(f"Access from other PCs: http://<YOUR_IP>:{port}")
        print("To find your IP, run: ipconfig")
        print("=" * 60)
    
    logger.info(f"Starting Invoice API server on http://{host}:{port}")
    print(f"Starting Invoice API server on http://{host}:{port}")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host=host, port=port)
```

---

## Step 3: Frontend Configuration Changes

### File: `script.js` (Line 15)

**BEFORE:**
```javascript
const API_URL = "http://127.0.0.1:8000";
```

**AFTER (Replace with YOUR actual IP):**
```javascript
// For LAN access, use your PC's IP address
// Find it with: ipconfig (look for IPv4 Address)
const API_URL = "http://192.168.1.15:8000";  // REPLACE WITH YOUR IP
```

**Alternative (Dynamic):**
```javascript
// Auto-detect: works if accessing via IP
const API_URL = window.location.hostname === "localhost" 
    ? "http://127.0.0.1:8000" 
    : `http://${window.location.hostname}:8000`;
```

---

## Step 4: Windows Firewall Configuration

### Option A: Allow Python Through Firewall (Recommended)

1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules** → **New Rule**
3. Select **Program** → Next
4. Browse to: `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python3XX\python.exe`
5. Select **Allow the connection**
6. Check: **Domain**, **Private**, **Public** (or just Private for LAN)
7. Name: "Python FastAPI Server"

### Option B: Allow Port 8000

1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules** → **New Rule**
3. Select **Port** → Next
4. Select **TCP** → Specific local ports: `8000`
5. Select **Allow the connection**
6. Check: **Private** (LAN networks)
7. Name: "Delivery Manifest API - Port 8000"

### Quick Test (PowerShell - Run as Admin):
```powershell
New-NetFirewallRule -DisplayName "Delivery Manifest API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

---

## Step 5: Testing LAN Access

### On Your PC (Host):
1. Start server: `python api_server.py`
2. Open browser: `http://localhost:8000`

### On Another PC (Same Network):
1. Find host PC's IP: `192.168.1.15` (example)
2. Open browser: `http://192.168.1.15:8000`
3. You should see the Delivery Manifest System

---

## LAN Access Checklist

```
□ Found my PC's LAN IP using ipconfig
□ Updated api_server.py with LAN_MODE = True
□ Updated script.js with correct IP address
□ Configured Windows Firewall (Python or Port 8000)
□ Restarted the API server
□ Tested access from host PC (localhost:8000)
□ Tested access from another PC (192.168.1.X:8000)
□ Verified multiple users can access simultaneously
□ Confirmed database writes work from remote PCs
```

---

## Troubleshooting

**Problem:** Other PCs can't connect
- Check firewall settings
- Verify both PCs are on same network
- Ping the host PC: `ping 192.168.1.15`
- Check if server is running: `netstat -an | findstr :8000`

**Problem:** "Connection Refused"
- Ensure server is bound to `0.0.0.0`, not `127.0.0.1`
- Restart the server after config changes

**Problem:** Slow performance
- Normal for SQLite with multiple concurrent users
- Consider limiting simultaneous writes
- Current setup handles 5-10 users comfortably

---

## Security Notes (LAN Environment)

✅ **Safe for LAN:**
- No authentication needed (trusted network)
- SQLite handles concurrent reads well
- File-based database is simple and reliable

⚠️ **Do NOT:**
- Expose to the internet (no port forwarding)
- Run with PRODUCTION_MODE = True in LAN mode
- Share your IP outside your local network

---

## Quick Reference

| Setting | Localhost Only | LAN Access |
|---------|---------------|------------|
| Backend Host | `127.0.0.1` | `0.0.0.0` |
| Frontend API_URL | `http://127.0.0.1:8000` | `http://192.168.1.X:8000` |
| Firewall | Not needed | Port 8000 allowed |
| Access URL | `localhost:8000` | `<YOUR_IP>:8000` |
