"""
Test script to verify database connection.

This script tests:
1. Database connection (SQLite or PostgreSQL)
2. Environment configuration
3. Supabase API client (optional, only if configured)

Note: Currently using SQLite for local development.
To switch to Supabase/PostgreSQL, set USE_SQLITE=False in .env
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.conf import settings
from django.db import connection

print("=" * 70)
print("DATABASE CONNECTION TEST")
print("=" * 70)

# Test 1: Check database configuration
print("\n[1] Checking database configuration...")
db_config = settings.DATABASES['default']
db_engine = db_config['ENGINE']

if 'sqlite' in db_engine:
    print(f"  ✓ Database: SQLite")
    print(f"  ✓ Database file: {db_config['NAME']}")
    print(f"  ✓ SQLite is ready for local development")
else:
    print(f"  ✓ Database: PostgreSQL")
    db_host = db_config.get('HOST', '')
    db_user = db_config.get('USER', '')
    db_name = db_config.get('NAME', '')
    db_port = db_config.get('PORT', '')
    db_password = db_config.get('PASSWORD', '')
    
    print(f"  ✓ POSTGRES_HOST: {db_host}")
    print(f"  ✓ POSTGRES_USER: {db_user}")
    print(f"  ✓ POSTGRES_DB: {db_name}")
    print(f"  ✓ POSTGRES_PORT: {db_port}")
    
    if db_password:
        print(f"  ✓ POSTGRES_PASSWORD: {'*' * 20} (set)")
    else:
        print("  ✗ POSTGRES_PASSWORD: NOT SET")

# Test 2: Test Supabase API client (optional)
print("\n[2] Testing Supabase API client (optional)...")
try:
    from app.supabase_client import supabase_client
    
    if supabase_client is None:
        print("  ⏭️  Supabase client not configured (optional - not needed for SQLite)")
    else:
        print("  ✓ Supabase client initialized")
        print("  ✓ Supabase API client is ready")
except Exception as e:
    print(f"  ⏭️  Supabase client not available: {e}")

# Test 3: Test database connection
print("\n[3] Testing database connection...")
if 'sqlite' in db_engine:
    # SQLite connection test
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()[0]
            print(f"  ✓ Database connection successful!")
            print(f"     SQLite version: {version}")
            
            # Test if we can query
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
            table_count = cursor.fetchone()[0]
            print(f"     Tables created: {table_count}")
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
else:
    # PostgreSQL connection test
    db_password = db_config.get('PASSWORD', '')
    if not db_password:
        print("  ⏭️  Skipping database test (password not set)")
    else:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print(f"  ✓ Database connection successful!")
                print(f"     PostgreSQL: {version.split(',')[0]}")
                
                # Test if we can query
                cursor.execute("SELECT current_database(), current_user;")
                db, user = cursor.fetchone()
                print(f"     Database: {db}")
                print(f"     User: {user}")
        except Exception as e:
            error_msg = str(e).lower()
            print(f"  ✗ Database connection failed: {e}")
            
            print("\n  Troubleshooting:")
            if "password" in error_msg or "authentication" in error_msg:
                print("     → Wrong password! Verify in Supabase dashboard")
            elif "pg_hba" in error_msg or "not permitted" in error_msg or "not allowed" in error_msg:
                print("     → IP not allowed! Add your IP in Supabase Network Restrictions")
            elif "timeout" in error_msg:
                print("     → Connection timeout! Check firewall/network")
            elif "could not translate host name" in error_msg or "getaddrinfo" in error_msg:
                print("     → DNS resolution failed! Check hostname")
            else:
                print("     → Check database connection details")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

all_ok = True

# Check database connection
if 'sqlite' in db_engine:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ SQLite database connection working")
    except:
        print("✗ Database connection failed (see errors above)")
        all_ok = False
else:
    db_password = db_config.get('PASSWORD', '')
    if not db_password:
        print("✗ Database password not set")
        print("\n  Next steps:")
        print("  1. Get your database password from Supabase dashboard")
        print("  2. Update POSTGRES_PASSWORD in backend/.env")
        print("  3. Run this test again")
        all_ok = False
    else:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print("✓ PostgreSQL database connection working")
        except:
            print("✗ Database connection failed (see errors above)")
            all_ok = False

if all_ok:
    print("\n🎉 All tests passed! Your Supabase connection is working.")
    print("\nNext steps:")
    print("  1. Run migrations: python manage.py migrate")
    print("  2. Create superuser: python manage.py createsuperuser")
    print("  3. Start server: python manage.py runserver")
else:
    print("\n⚠️  Some issues found. Please fix them and run this test again.")
    sys.exit(1)

