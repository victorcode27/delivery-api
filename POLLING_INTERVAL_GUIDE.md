# Polling Interval Comparison Guide

## Quick Reference Table

| Interval | Response Time | Safety | Resource Usage | Network Impact | Recommendation |
|----------|---------------|--------|----------------|----------------|----------------|
| **5-10s** | Excellent | ⚠️ Low | High | High | ❌ Not recommended |
| **10-20s** | Very Good | ⚠️ Medium | Medium | Medium | ⚠️ Use with caution |
| **30-60s** | Good | ✅ High | Low | Low | ✅ **RECOMMENDED** |
| **60-90s** | Moderate | ✅ Very High | Very Low | Very Low | ⚠️ For bulk processing |
| **120s+** | Slow | ✅ Very High | Minimal | Minimal | ❌ Too slow |

---

## Detailed Analysis

### 🚀 5-10 Seconds (Aggressive)

**Pros:**
- Near real-time processing
- Files processed within 10-15 seconds

**Cons:**
- ❌ High risk of catching files mid-write
- ❌ 360-720 network checks per hour
- ❌ Higher CPU usage (~0.5%)
- ❌ Unnecessary for most use cases

**When to use:**
- Mission-critical, time-sensitive operations
- Local folders only (not network)
- Small number of files (<100)

**Example scenario:** Stock trading alerts, emergency notifications

---

### ⚡ 10-20 Seconds (Moderate-Aggressive)

**Pros:**
- Quick processing (20-30 seconds)
- Better than 5-10s for safety

**Cons:**
- ⚠️ Still較 frequent network checks (180-360/hour)
- ⚠️ May catch incomplete files on slow networks
- ⚠️ Moderate resource usage

**When to use:**
- Fast local network
- Smaller folders (<500 files)
- Response time is important but not critical

**Example scenario:** Order processing systems with hourly deadlines

---

### ✅ 30-60 Seconds (RECOMMENDED)

**Pros:**
- ✅ **Optimal balance** of all factors
- ✅ Safe file detection (files have time to complete)
- ✅ Low resource usage (~0.1% CPU)
- ✅ Only 60-120 network checks/hour
- ✅ Works well with 1000s of files
- ✅ Network-friendly

**Cons:**
- Files processed within 1-2 minutes (acceptable for most cases)

**When to use:**
- **Default choice for most scenarios**
- Network folders (UNC paths)
- Folders with many files (100-10,000+)
- Continuous background operation

**Example scenario:** Your invoice processing system (current use case)

**Why this is best for your system:**
1. Invoices don't require instant processing
2. Network folder may have slow write speeds
3. Large number of existing files (2600+)
4. Runs continuously in background
5. Minimal impact on system resources

---

### 🐢 60-90 Seconds (Conservative)

**Pros:**
- Extremely safe
- Minimal resource usage
- Very network-friendly

**Cons:**
- ⚠️ Slower response (1.5-3 minutes)
- May feel sluggish during active periods

**When to use:**
- Very slow networks
- Extremely large folders (10,000+ files)
- Low-priority background processing
- Resource-constrained systems

**Example scenario:** Overnight batch processing, archival systems

---

### 🦥 120+ Seconds (Too Slow)

**Pros:**
- Absolute minimum resource usage

**Cons:**
- ❌ Too slow for practical use (4+ minutes)
- ❌ Poor user experience
- ❌ Not responsive enough

**When to use:**
- Almost never
- Maybe for daily/weekly batch jobs

---

## Real-World File Write Times

Understanding how long files take to write helps choose the right interval:

### Local SSD/HDD:
- Small PDF (100KB): **< 0.1 seconds**
- Medium PDF (1MB): **< 0.5 seconds**
- Large PDF (10MB): **1-2 seconds**

### Network Drive (SMB/CIFS):
- Small PDF (100KB): **0.5-2 seconds**
- Medium PDF (1MB): **2-5 seconds**
- Large PDF (10MB): **5-15 seconds**

### Slow Network (Congested/WiFi):
- Small PDF (100KB): **2-5 seconds**
- Medium PDF (1MB): **5-15 seconds**
- Large PDF (10MB): **15-60 seconds**

**Conclusion:** 
- With **30-second polling** + **6-second stability check**, you can safely detect files up to 10MB even on slow networks
- Files are checked multiple times before processing (extra safety)

---

## Configuration Examples

### For Your Current System (Network Folder)
```python
POLL_INTERVAL = 30  # ✅ RECOMMENDED
FILE_STABILITY_CHECKS = 3
FILE_STABILITY_DELAY = 2
```

### For Fast Local Folder
```python
POLL_INTERVAL = 15
FILE_STABILITY_CHECKS = 2
FILE_STABILITY_DELAY = 1
```

### For Very Slow Network
```python
POLL_INTERVAL = 60
FILE_STABILITY_CHECKS = 4
FILE_STABILITY_DELAY = 3
```

### For Urgent Processing (Use with Caution)
```python
POLL_INTERVAL = 10
FILE_STABILITY_CHECKS = 4  # More checks to compensate
FILE_STABILITY_DELAY = 2
```

---

## Decision Tree

```
How many files in folder?
│
├─ < 500 files
│  │
│  ├─ Network drive? → 30 seconds ✅
│  └─ Local drive? → 15-30 seconds
│
├─ 500-5,000 files
│  │
│  ├─ Network drive? → 30-45 seconds ✅
│  └─ Local drive? → 20-30 seconds
│
└─ > 5,000 files
   │
   ├─ Network drive? → 45-60 seconds ✅
   └─ Local drive? → 30-45 seconds
```

---

## Your Specific Case: \\BRD-DESKTOP-ELV\storage

**Facts:**
- ✅ Network UNC path
- ✅ 2,600+ PDFs already present
- ✅ Continuous operation expected
- ✅ Not time-critical (invoices processed within minutes is fine)

**Recommendation:** **30 seconds** ⭐

**Alternative if you want faster response:** 20-30 seconds  
**Alternative if network is slow:** 45-60 seconds

---

## Performance Impact Visualization

### Network Checks per Hour:
```
5s   → ████████████████████ 720 checks
10s  → ██████████ 360 checks
30s  → ███ 120 checks ✅
60s  → █ 60 checks
```

### Processing Time per File:
```
Detection → Stability → Processing
   (30s)      (6s)        (~2s)
   
Total: ~38 seconds from file creation to database entry ✅
```

---

## Testing Recommendations

1. **Start with 30 seconds** (current default)
2. **Monitor for 1 hour** - check log file
3. **Check response times** - are files processed quickly enough?
4. **Check resource usage** - is CPU/network impact acceptable?
5. **Adjust if needed** - increase/decrease based on observations

---

## Summary

**For your invoice processing system:**

🏆 **Best Choice: 30-60 seconds**

This provides:
- ✅ Safe file detection (no incomplete files)
- ✅ Reasonable response time (files processed within 1-2 minutes)
- ✅ Low resource usage (can run 24/7)
- ✅ Network-friendly (minimal overhead)
- ✅ Scales well with 1000s of files

**The current configuration (30s) is optimal for your use case.**

