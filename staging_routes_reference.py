# Manifest Staging Routes (NEW)
# These routes are added to api_server.py right before the static file serving routes

# Import added at top of file:
# from fastapi import Request

#Helper function added after CORS middleware:
def get_username_from_request(request_headers) -> str:
    \"\"\"Extract username from X-Username header. Returns 'anonymous' if not found.\"\"\"
    username = request_headers.get('X-Username', request_headers.get('x-username', ''))
    if not username:
        username = 'anonymous'
    return username

# =============================================
# MANIFEST STAGING ENDPOINTS (NEW FIX)
# =============================================

@app.get("/manifest/current")
def get_current_manifest_staging(request: Request):
    \"\"\"Get invoices in current manifest staging for this user.\"\"\"
    try:
        username = get_username_from_request(request.headers)
        invoices = database.get_current_manifest(username)
        logger.info(f"Fetched {len(invoices)} invoices from staging for user {username}")
        return {"invoices": invoices, "count": len(invoices)}
    except Exception as e:
        logger.error(f"Error fetching current manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/manifest/remove")
def remove_from_manifest_staging(request_data: AllocateRequest, request: Request):
    \"\"\"Remove invoices from current manifest staging.\"\"\"
    try:
        username = get_username_from_request(request.headers)
        removed = database.remove_from_staging(username, request_data.filenames)
        
        if removed > 0:
            logger.info(f"Removed {removed} invoices from staging for user {username}")
            return {"message": f"Removed {removed} invoices from manifest", "removed": removed}
        else:
            return {"message": "No invoices found in manifest to remove", "removed": 0}
    except Exception as e:
        logger.error(f"Error removing from staging: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# MODIFIED EXISTING ROUTES:
# 1. /invoices/allocate - change to use add_to_staging()
# 2. /reports POST - add session_id extraction and pass to save_report()
