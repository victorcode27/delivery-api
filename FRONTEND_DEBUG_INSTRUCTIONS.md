# Frontend Date Filter Diagnostic Instructions

## CRITICAL: Follow These Steps Exactly

### Step 1: Open the Dispatch Report Page

1. Open your browser
2. Navigate to: `http://localhost:8000/dispatch_report.html`
3. Open Developer Tools (F12 or Right-click → Inspect)
4. Go to the **Console** tab
5. Clear the console (click the 🚫 icon or press Ctrl+L)

### Step 2: Test WITHOUT Date Filter

1. Let the page load completely
2. **Copy ALL console output** that appears
3. Look for the section that starts with `=== LOAD DATA DEBUG ===`
4. Save this output as **"test1_no_filter.txt"**

**Expected output structure:**
```
=== LOAD DATA DEBUG ===
1. Current State: { dateFrom: null, dateTo: null, ... }
2. API Request URL: http://localhost:8000/reports/dispatched?filter_type=dispatch&limit=50&offset=0...
3. Query Parameters: { filter_type: "dispatch", limit: "50", ... }
4. API Response: { invoices_count: XX, total: XX, ... }
5. Updated State: { currentData_length: XX, totalCount: XX }
6. Showing TABLE state (XX invoices)
=== END DEBUG ===
```

### Step 3: Test WITH Date Filter

1. Clear the console again
2. Set **Date From**: `2026-01-29`
3. Set **Date To**: `2026-01-29`
4. Click **"Apply Filters"** button
5. Wait for the page to update
6. **Copy ALL console output** that appears
7. Save this output as **"test2_with_filter.txt"**

### Step 4: Compare the Outputs

Look for these specific differences:

#### Check 1: State Values
```
Test 1: dateFrom: null, dateTo: null
Test 2: dateFrom: ???, dateTo: ???
```

#### Check 2: API Request URL
```
Test 1: ...?filter_type=dispatch&limit=50&offset=0&sort_by=date_dispatched&sort_order=DESC
Test 2: ...?date_from=???&date_to=???&filter_type=dispatch&limit=50&offset=0&sort_by=date_dispatched&sort_order=DESC
```

#### Check 3: Query Parameters Object
```
Test 1: { filter_type: "dispatch", limit: "50", offset: "0", sort_by: "date_dispatched", sort_order: "DESC" }
Test 2: { date_from: "???", date_to: "???", filter_type: "dispatch", ... }
```

#### Check 4: API Response
```
Test 1: { invoices_count: XX, total: XX }
Test 2: { invoices_count: ???, total: ??? }
```

#### Check 5: Final State
```
Test 1: Showing TABLE state (XX invoices)
Test 2: Showing ??? state (??? invoices)
```

### Step 5: Report Back

**Send me BOTH complete console outputs** (test1_no_filter.txt and test2_with_filter.txt)

I need to see:
- ✅ Exact date format being sent (YYYY-MM-DD vs ISO timestamp)
- ✅ Whether date parameters are actually included in the URL
- ✅ What the API returns (invoices_count and total)
- ✅ Whether the frontend receives the data but doesn't display it

---

## Quick Troubleshooting

### If you see NO console output:
- Make sure you're on the **Console** tab, not Elements or Network
- Refresh the page (F5) and try again
- Check that JavaScript is enabled

### If you see errors in red:
- Copy the ENTIRE error message
- Include it in your report

### If the page shows "No invoices available":
- This is expected when filtering fails
- The console logs will tell us WHY

---

## What I'm Looking For

The console logs will reveal:

1. **Date format issue**: Is `dateFrom` being sent as `"2026-01-29"` or something else?
2. **Parameter passing**: Are the date parameters actually in the URL?
3. **API response**: Does the API return 42 invoices or 0?
4. **Frontend bug**: Does the frontend receive 42 invoices but show 0?

**This will pinpoint the EXACT line where the bug occurs.**
