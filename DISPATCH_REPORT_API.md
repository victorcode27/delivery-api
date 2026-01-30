# Dispatch Report API Documentation

## Base URL
```
http://localhost:8000
```

---

## Endpoints

### 1. Get Dispatched Invoices (NEW)

**Endpoint:** `GET /reports/dispatched`

**Description:** Get dispatched invoices as invoice-level rows with denormalized dispatch metadata.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date_from` | string (YYYY-MM-DD) | No | null | Filter by dispatch date >= |
| `date_to` | string (YYYY-MM-DD) | No | null | Filter by dispatch date <= |
| `search` | string | No | null | Global text search across invoice #, order #, manifest #, customer, driver, truck reg, checker |
| `limit` | integer | No | 50 | Results per page |
| `offset` | integer | No | 0 | Skip N results (for pagination) |
| `sort_by` | string | No | date_dispatched | Field to sort by (`date_dispatched`, `manifest_number`, `invoice_number`, `customer_name`, `driver`) |
| `sort_order` | string | No | DESC | Sort order (`ASC` or `DESC`) |

**Response:**
```json
{
  "invoices": [
    {
      "manifest_number": "A35426",
      "date_dispatched": "2026-01-26",
      "driver": "John Doe",
      "assistant": "Jane Smith",
      "checker": "Bob Wilson",
      "reg_number": "ABC-123",
      "invoice_number": "BINV8492",
      "order_number": "12345",
      "customer_name": "ACME Corp",
      "customer_number": "C001",
      "invoice_date": "2026-01-25",
      "area": "NORTH",
      "sku": 10,
      "value": 1250.50,
      "weight": 45.2
    }
  ],
  "total": 123,
  "page": 0,
  "limit": 50
}
```

**Example Requests:**

```bash
# Get all dispatched invoices
curl "http://localhost:8000/reports/dispatched"

# Filter by date range
curl "http://localhost:8000/reports/dispatched?date_from=2026-01-01&date_to=2026-01-31"

# Search for specific invoice
curl "http://localhost:8000/reports/dispatched?search=BINV8492"

# Search for customer
curl "http://localhost:8000/reports/dispatched?search=ACME"

# Pagination
curl "http://localhost:8000/reports/dispatched?limit=10&offset=0"  # Page 1
curl "http://localhost:8000/reports/dispatched?limit=10&offset=10" # Page 2

# Combined filters
curl "http://localhost:8000/reports/dispatched?date_from=2026-01-26&search=BINV&limit=20"
```

---

### 2. Get Outstanding Orders (NEW)

**Endpoint:** `GET /reports/outstanding`

**Description:** Get invoices that have NO dispatch record (never added to any manifest).

**Query Parameters:** None

**Response:**
```json
{
  "orders": [
    {
      "invoice_number": "BINV8500",
      "order_number": "12350",
      "customer_name": "XYZ Ltd",
      "invoice_date": "2026-01-28",
      "customer_number": "C002",
      "total_value": "850.00",
      "area": "SOUTH"
    }
  ],
  "count": 42
}
```

**Example Requests:**

```bash
# Get all outstanding orders
curl "http://localhost:8000/reports/outstanding"
```

**Notes:**
- This checks if invoice has ANY record in `report_items` table
- Does NOT rely on `is_allocated` flag
- Excludes cancelled invoices
- Returns invoices sorted by invoice_date DESC

---

### 3. Get Reports (DEPRECATED)

**Endpoint:** `GET /reports`

**Status:** ⚠️ **DEPRECATED** - Use `/reports/dispatched` instead

**Description:** Get dispatch reports (report-level aggregation).

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date_from` | string (YYYY-MM-DD) | No | null | Filter by date >= |
| `date_to` | string (YYYY-MM-DD) | No | null | Filter by date <= |

**Response:**
```json
{
  "reports": [
    {
      "id": 1,
      "manifest_number": "A35426",
      "date": "2026-01-26",
      "date_dispatched": "2026-01-26",
      "driver": "John Doe",
      "assistant": "Jane Smith",
      "checker": "Bob Wilson",
      "reg_number": "ABC-123",
      "pallets_brown": 10,
      "pallets_blue": 5,
      "crates": 3,
      "mileage": 120,
      "total_value": 5000.00,
      "total_sku": 50,
      "total_weight": 250.5,
      "created_at": "2026-01-26 14:30:00",
      "invoices": [...]
    }
  ],
  "count": 18
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

---

## Database Immutability

**IMPORTANT:** Historical dispatch data is protected by database triggers.

Any attempt to UPDATE or DELETE records in `reports` or `report_items` tables will be **blocked** with an error:

```
sqlite3.IntegrityError: Historical dispatch reports cannot be modified
```

This ensures dispatch records remain accurate for auditing and historical reporting.

---

## Performance

All queries are optimized with indexes:
- `idx_reports_date_dispatched` - Date filtering
- `idx_reports_manifest_number` - Manifest lookups
- `idx_report_items_invoice_number` - Invoice searches
- `idx_report_items_report_id` - JOIN optimization

**Expected Response Times:**
- Filtered queries: < 100ms
- Full-text search: < 200ms
- Pagination: Constant time (O(1))

---

## Pagination Guide

Use `limit` and `offset` for pagination:

```javascript
// Page 1 (first 50 results)
fetch('/reports/dispatched?limit=50&offset=0')

// Page 2 (next 50 results)
fetch('/reports/dispatched?limit=50&offset=50')

// Page 3 (next 50 results)
fetch('/reports/dispatched?limit=50&offset=100')

// Calculate total pages
const totalPages = Math.ceil(response.total / limit)
```

The `total` field in the response reflects the **total count AFTER filters** are applied, ensuring accurate pagination.
