# LAN Access Quick Reference

## Current Configuration
- **Your PC's IP:** 192.168.0.29
- **Server Port:** 8000
- **Access URL:** http://192.168.0.29:8000

## Quick Start (3 Steps)

### 1. Configure Firewall
Run PowerShell as Administrator:
```powershell
New-NetFirewallRule -DisplayName "Delivery Manifest API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### 2. Start Server
```cmd
python api_server.py
```
You should see: "WARNING: Server running in LAN MODE"

### 3. Access from Other PCs
Open browser on any PC on the same network:
```
http://192.168.0.29:8000
```

## Toggle Between Localhost and LAN

### Switch to Localhost Only
**api_server.py** (line 834):
```python
LAN_MODE = False
```

**script.js** (line 14):
```javascript
const API_URL = "http://127.0.0.1:8000";
```

### Switch to LAN Access
**api_server.py** (line 834):
```python
LAN_MODE = True
```

**script.js** (line 14):
```javascript
const API_URL = "http://192.168.0.29:8000";
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect from other PC | Check firewall, run: `python get_lan_ip.py` |
| "Connection refused" | Ensure LAN_MODE = True, restart server |
| Wrong IP after network change | Run: `python get_lan_ip.py`, update script.js |
| Server won't start | Check if PRODUCTION_MODE = False |

## Testing Checklist
```
□ Firewall rule added
□ Server started with LAN MODE warning
□ Accessed from host PC (localhost:8000)
□ Accessed from other PC (192.168.0.29:8000)
□ Multiple users can connect simultaneously
```

## Files Modified
- `api_server.py` - LAN_MODE configuration
- `script.js` - API_URL updated
- `get_lan_ip.py` - Helper script (run anytime)
- `LAN_ACCESS_GUIDE.md` - Full documentation
