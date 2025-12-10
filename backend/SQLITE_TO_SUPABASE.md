# Migrating from SQLite to Supabase

This guide explains how to switch from SQLite (current setup) to Supabase PostgreSQL when you're ready.

## Current Setup (SQLite)

✅ **Currently using**: SQLite database (`db.sqlite3`)
- No configuration needed
- Works out of the box
- Perfect for local development

## When Ready to Migrate to Supabase

### Step 1: Update .env File

1. Open `backend/.env` (or create from `env.example`)

2. Set `USE_SQLITE=False`:
   ```env
   USE_SQLITE=False
   ```

3. Add Supabase credentials:
   ```env
   SUPABASE_URL=https://tlyqeuqpbnyzpwssbfcm.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   
   POSTGRES_DB=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_actual_password
   POSTGRES_HOST=db.tlyqeuqpbnyzpwssbfcm.supabase.co
   POSTGRES_PORT=5432
   ```

### Step 2: Install PostgreSQL Driver

```bash
pip install psycopg2-binary
```

Or add to `requirements.txt`:
```
psycopg2-binary>=2.9.0
```

### Step 3: Run Migrations on Supabase

```bash
python manage.py migrate
```

This will create all tables in your Supabase database.

### Step 4: Migrate Data (Optional)

If you have data in SQLite that you want to migrate:

```bash
# Export from SQLite
python manage.py dumpdata > data_backup.json

# Switch to Supabase (update .env)
# Then load into Supabase
python manage.py loaddata data_backup.json
```

### Step 5: Test Connection

```bash
python test_supabase_connection.py
```

## Switching Back to SQLite

If you need to switch back to SQLite:

1. Set in `.env`:
   ```env
   USE_SQLITE=True
   ```

2. The database will automatically use `db.sqlite3`

## Notes

- SQLite database file: `backend/db.sqlite3` (created automatically)
- SQLite is included in Python, no extra packages needed
- Supabase requires `psycopg2-binary` package
- Both configurations are ready - just toggle `USE_SQLITE` in `.env`

