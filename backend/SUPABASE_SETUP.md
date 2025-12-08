# Supabase Setup Guide

This guide will help you connect your Django backend to Supabase.

## Prerequisites

- Supabase project created at https://app.supabase.com
- Project URL and API keys from your Supabase project settings

## Step 1: Get Your Supabase Database Password

1. Go to your Supabase project dashboard: https://app.supabase.com/project/aupzonugezawvtcfkyvj
2. Navigate to **Project Settings** > **Database**
3. Find and copy your **Database Password** (you set this when creating the project)
   - If you forgot it, you can reset it from the same page

## Step 2: Update Your .env File

1. Copy the `env.example` file to create a `.env` file:
   ```bash
   cd backend
   cp env.example .env
   ```

2. Open `.env` and update the `POSTGRES_PASSWORD` with your actual Supabase database password:
   ```bash
   POSTGRES_PASSWORD=your_actual_supabase_db_password
   ```

3. Verify all other Supabase credentials are correct (they should already be set from env.example):
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `POSTGRES_HOST`
   - `POSTGRES_USER`
   - `POSTGRES_DB`
   - `POSTGRES_PORT`

## Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 4: Run Migrations

Create the database tables in your Supabase PostgreSQL database:

```bash
python manage.py migrate
```

## Step 5: Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Step 6: Run the Development Server

```bash
python manage.py runserver
```

Your Django app should now be connected to Supabase! 🎉

## Verifying the Connection

You can verify the connection by:

1. **Django Admin**: Visit http://localhost:8000/admin and log in with your superuser credentials
2. **Supabase Dashboard**: Check your Supabase project's Table Editor to see the Django tables created
3. **API Endpoints**: Test your REST API endpoints

## Using Supabase Features

### Direct Supabase Client Usage

The Django app includes a Supabase client utility in `app/supabase_client.py`. You can use it for:

```python
from app.supabase_client import supabase_client

# Query data directly (alternative to Django ORM)
response = supabase_client.table('your_table').select('*').execute()

# Upload files to Supabase Storage
supabase_client.storage.from_('bucket_name').upload('path', file_data)

# Use real-time subscriptions
supabase_client.table('your_table').on('INSERT', callback).subscribe()
```

### Supabase Auth Integration

If you want to use Supabase Auth instead of Django's built-in auth:

1. Get the service role key from Supabase project settings
2. Add it to your `.env`:
   ```bash
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```
3. Use the auth methods in your views:
   ```python
   from app.supabase_client import supabase_client
   
   # Sign up a user
   response = supabase_client.auth.sign_up({
       "email": "user@example.com",
       "password": "secure_password"
   })
   ```

## Additional Resources

- [Supabase Python Documentation](https://supabase.com/docs/reference/python/introduction)
- [Django + Supabase Guide](https://supabase.com/docs/guides/getting-started/tutorials/with-django)
- Your Supabase Project: https://app.supabase.com/project/aupzonugezawvtcfkyvj

## Troubleshooting

**Connection Error**: If you get a database connection error:
- Verify your database password is correct
- Check that your IP is allowed in Supabase (Network Restrictions in project settings)
- Ensure the PostgreSQL host and port are correct

**Migration Issues**: If migrations fail:
- Make sure the database user has proper permissions
- Check Supabase logs in the project dashboard

**Supabase Client Not Initialized**: If you see warnings about Supabase client:
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set in your `.env` file
- Restart your Django server after updating environment variables
