# Invoice File Watcher Service

## Overview
Automatically monitors a folder for new PDF invoice files and processes them safely. This service ensures files are completely written before attempting to read them, preventing data corruption or incomplete processing.

---

## 🚀 Quick Start

### Method 1: Using Batch File (Recommended)
Simply double-click: **`START_WATCHER.bat`**

### Method 2: Command Line
```bash
python file_watcher.py
```

---

## ⚙️ Configuration

Edit `file_watcher.py` to customize settings:

```python
WATCH_FOLDER = r"\\BRD-DESKTOP-ELV\storage"  # Folder to monitor
POLL_INTERVAL = 30  # Seconds between scans
FILE_STABILITY_CHECKS = 3  # Number of checks to verify file is complete
FILE_STABILITY_DELAY = 2  # Seconds between stability checks
```

---

## ⏱️ Polling Interval Recommendations

### **30-60 seconds (RECOMMENDED)**
- ✅ **Network-friendly**: Minimal network traffic
- ✅ **Resource efficient**: Low CPU/battery usage  
- ✅ **Fast enough**: Processes files within 1 minute
- ✅ **Safe**: Gives files time to fully write

### **10-20 seconds (Moderate)**
- ⚠️ More responsive but higher resource usage
- ⚠️ May still catch files mid-write on slow networks
- Best for: Local folders or fast network connections

### **5-10 seconds (Aggressive)**
- ❌ High resource usage
- ❌ Increased risk of catching incomplete files
- ❌ Network overhead
- Only use for: Urgent processing requirements

### **60+ seconds (Conservative)**
- ⚠️ Very slow response time
- Best for: Low-priority batch processing

---

## 🔒 File Safety Mechanisms

The watcher uses **multiple layers of protection** to ensure files are ready:

### 1. **Size Stability Check**
- Monitors file size over multiple checks (default: 3 checks)
- Only processes if size remains constant
- Detects files still being written/copied

### 2. **File Lock Detection**
- Attempts to exclusively open the file
- Fails gracefully if file is locked by another process
- Prevents reading corrupted/incomplete data

### 3. **Non-zero Size Validation**
- Rejects empty files (0 bytes)
- Ensures file has actual content

### 4. **Content Accessibility Test**
- Reads first 1KB of file to verify accessibility
- Catches permission issues early

### Total verification time: **6 seconds** (3 checks × 2 seconds)

---

## 📊 How It Works

```
[New File Appears]
      ↓
[Detected in scan] (every 30s)
      ↓
[Size Check 1] → wait 2s
      ↓
[Size Check 2] → wait 2s
      ↓
[Size Check 3]
      ↓
[All checks passed?]
      ↓
[Process Invoice] → Add to database
      ↓
[Mark as known] → Won't reprocess
```

---

## 📁 File Tracking

### On Startup:
- Scans existing PDFs in the folder
- Marks all as "known" (won't reprocess)
- **Only NEW files** added after startup will be processed

### During Operation:
- New files detected each poll cycle
- Undergoes stability checks
- If passing: Processed and marked as known
- If failing: Retried next poll cycle

---

## 📝 Logging

Logs are written to: **`file_watcher.log`**

### Log Levels:
- **INFO**: Normal operation (file detected, processed, etc.)
- **WARNING**: Non-critical issues (duplicates, etc.)
- **ERROR**: Processing failures, network issues
- **DEBUG**: Detailed stability check information

### Example Log Output:
```
2026-01-24 13:30:00 - INFO - Starting File Watcher Service
2026-01-24 13:30:00 - INFO - Watch Folder: \\BRD-DESKTOP-ELV\storage
2026-01-24 13:30:00 - INFO - Poll Interval: 30 seconds
2026-01-24 13:30:05 - INFO - Found 2500 existing PDF files
2026-01-24 13:30:05 - INFO - 🔍 Watching for new files...
2026-01-24 13:31:00 - INFO - 🔔 New file detected: Invoice_12345.pdf
2026-01-24 13:31:08 - INFO - ✓ File is stable and ready (125834 bytes)
2026-01-24 13:31:09 - INFO - ✓ Successfully added: ABC Company - $1,234.56
```

---

## 🛠️ Troubleshooting

### Issue: "Watch folder does not exist"
**Solution**: Verify network path is accessible:
- Open File Explorer
- Navigate to `\\BRD-DESKTOP-ELV\storage`
- If it fails, check network connection or map the drive

### Issue: "File is locked or inaccessible"
**Cause**: Another program is using the file
**Solution**: 
- File will be retried on next poll cycle
- If persists, increase `FILE_STABILITY_DELAY`

### Issue: Files not being detected
**Possible causes**:
1. File existed before watcher started (only NEW files are processed)
2. File extension is not `.pdf`
3. Polling interval is too long

**Solution**: Restart watcher or use "Refresh Invoices" in web UI

### Issue: High CPU usage
**Solution**: Increase `POLL_INTERVAL` (e.g., 60 seconds)

---

## 🔄 Integration with Existing System

The file watcher **complements** the existing manual refresh:

### File Watcher (Automatic)
- Runs continuously in background
- Auto-processes new files every 30-60s
- Ideal for: Continuous operation, unattended processing

### Manual Refresh (On-Demand)
- Click "Refresh Invoices" in web UI
- Processes all files immediately
- Ideal for: Initial setup, troubleshooting, bulk processing

**You can use BOTH simultaneously** - they work together seamlessly.

---

## 🎯 Best Practices

1. **Run as a background service**: Minimize the window, let it run continuously
2. **Monitor the log file**: Check `file_watcher.log` periodically for issues
3. **Start with default settings**: 30-second interval works well for most scenarios
4. **Test with a single file**: Copy one PDF to verify everything works
5. **Don't modify files in the watched folder**: Let the copy complete naturally

---

## 📋 System Requirements

- **Python 3.7+**
- **Network access** to `\\BRD-DESKTOP-ELV\storage`
- **Dependencies**: `pdfplumber` (already installed)
- **Permissions**: Read access to network folder

---

## 🚦 Performance Considerations

### For **30-second polling interval**:
- **Network requests**: 120 per hour
- **CPU usage**: ~0.1% average
- **Memory**: ~15MB
- **Folder with 3000 PDFs**: ~100ms per scan

### Scaling:
- **Up to 5,000 files**: No adjustment needed
- **5,000-10,000 files**: Consider 45-60 second interval
- **10,000+ files**: Use 60-90 second interval or file system events

---

## 🔐 Security Notes

- Service runs with **current user permissions**
- No files are deleted or modified (read-only operation)
- Original PDFs remain in network folder
- Database operations use parameterized queries (SQL injection safe)

---

## ❓ FAQ

**Q: Will it reprocess files already in the database?**  
A: No, it checks the database and skips files already processed.

**Q: What happens if the network disconnects?**  
A: The service logs an error and continues polling. It will resume when the network reconnects.

**Q: Can I run multiple watchers?**  
A: Yes, but not recommended (may cause duplicate processing). Use one watcher per folder.

**Q: Does it work with local folders?**  
A: Yes! Just change `WATCH_FOLDER` to a local path (e.g., `C:\Invoices`)

**Q: How do I stop the service?**  
A: Press `Ctrl+C` in the console window or close the window.

---

## 📞 Support

For issues or questions:
1. Check `file_watcher.log` for error messages
2. Verify network connectivity to the shared folder
3. Test with "Refresh Invoices" button first to ensure invoice_processor works

---

**Last Updated**: 2026-01-24
