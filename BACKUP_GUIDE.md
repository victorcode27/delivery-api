# PostgreSQL Backup & Restore Guide

## Backup Scripts

Two scripts have been created in your project folder:

### 1. `backup_database.bat` - Create Backup
- **What it does:** Creates a complete backup of your `delivery_db` database
- **Output:** Saves timestamped `.sql` files in `backups/` folder
- **Format:** Plain SQL format (human-readable, portable)
- **Usage:** Double-click to run

**Backup file naming:**
```
delivery_db_backup_YYYYMMDD_HHMMSS.sql
Example: delivery_db_backup_20260213_145030.sql
```

### 2. `restore_database.bat` - Restore Backup
- **What it does:** Restores database from a backup file
- **Warning:** ⚠️ REPLACES all current data
- **Safety:** Requires typing "YES" to confirm
- **Usage:** Double-click to run, then select backup file

---

## How to Use

### Creating a Backup

1. **Run the backup script:**
   - Double-click `backup_database.bat`
   - Wait for completion (usually 1-2 seconds)

2. **Verify backup:**
   - Check the `backups/` folder
   - You'll see a new `.sql` file with timestamp

3. **Backup schedule recommendations:**
   - **Daily:** Before starting work
   - **Before major changes:** Before migrations or updates
   - **After important data entry:** End of day/week

### Restoring from Backup

1. **Run the restore script:**
   - Double-click `restore_database.bat`

2. **Select backup file:**
   - View list of available backups
   - Enter filename (e.g., `delivery_db_backup_20260213_145030.sql`)

3. **Confirm restore:**
   - Type `YES` when prompted
   - Wait for completion

4. **Restart your app:**
   - Close the API server
   - Restart it to use the restored data

---

## Backup Location

**Folder:** `C:\Users\Assault\OneDrive\Documents\Delivery Route\backups\`

All backup files are stored here and automatically synced to OneDrive.

---

## What Gets Backed Up

✅ **Included in backup:**
- All database tables and data
- Table structures/schemas
- Indexes and sequences
- Constraints and relationships

❌ **Not included:**
- PostgreSQL server configuration
- User passwords (for security)
- Files outside the database (PDFs, Excel files, etc.)

---

## Backup File Format

The backup is a **plain SQL file** containing:
- `CREATE TABLE` statements
- `INSERT` statements for all data
- Sequence updates
- Constraint definitions

**Advantages:**
- Human-readable (can view in text editor)
- Portable (works across PostgreSQL versions)
- Easy to modify if needed
- Works with version control (Git)

---

## Best Practices

### Regular Backups
```batch
REM Add to Windows Task Scheduler for automatic daily backups
backup_database.bat
```

### Before Updates
Always backup before:
- Migrating databases
- Updating the application
- Making schema changes
- Bulk data operations

### Backup Retention
- Keep last 7 daily backups
- Keep last 4 weekly backups
- Keep monthly backups for 6 months

### Testing Restores
Periodically test that your backups can be restored successfully.

---

## Troubleshooting

### "pg_dump is not recognized"
- Check PostgreSQL installation path
- Update path in script: `C:\Program Files\PostgreSQL\18\bin\`

### "Access denied"
- Ensure PostgreSQL service is running
- Verify password is correct (currently: `1234`)

### "Database does not exist"
- Confirm database name is `delivery_db`
- Check PostgreSQL server is running on port 5432

---

## Advanced: Manual Backup Commands

If you prefer command line:

**Backup:**
```batch
pg_dump -U postgres -h localhost -p 5432 -d delivery_db -F p -f backup.sql
```

**Restore:**
```batch
psql -U postgres -h localhost -p 5432 -d delivery_db -f backup.sql
```

**Compressed backup (smaller file size):**
```batch
pg_dump -U postgres -h localhost -p 5432 -d delivery_db -F c -f backup.dump
```

---

## Quick Reference

| Task | Script | Time | File Size |
|------|--------|------|-----------|
| Create backup | `backup_database.bat` | ~2 sec | ~500 KB |
| Restore backup | `restore_database.bat` | ~5 sec | N/A |
| List backups | Check `backups/` folder | Instant | N/A |

---

**Note:** Your current database contains **2,712 rows** across 9 tables, so backups are small and fast!
