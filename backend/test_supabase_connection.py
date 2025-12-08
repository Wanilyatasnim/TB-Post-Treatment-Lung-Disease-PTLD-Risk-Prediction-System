"""
Test script to verify Supabase connection.

This script checks:
1. Environment variables are set correctly
2. Django can load Supabase configuration
3. Supabase client can be initialized
4. Database connection works

Run this before running migrations to ensure everything is configured properly.
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
from app.supabase_client import supabase_client, verify_supabase_connection


def test_environment_variables():
    """Check if required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
        'POSTGRES_DB': settings.DATABASES['default']['NAME'],
        'POSTGRES_USER': settings.DATABASES['default']['USER'],
        'POSTGRES_HOST': settings.DATABASES['default']['HOST'],
        'POSTGRES_PORT': settings.DATABASES['default']['PORT'],
    }
    
    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value:
            print(f"  ✅ {var_name}: {'*' * 10}{var_value[-10:] if len(var_value) > 10 else var_value}")
        else:
            print(f"  ❌ {var_name}: NOT SET")
            all_set = False
    
    # Check password separately (it's sensitive)
    if settings.DATABASES['default']['PASSWORD']:
        print(f"  ✅ POSTGRES_PASSWORD: {'*' * 20}")
    else:
        print(f"  ❌ POSTGRES_PASSWORD: NOT SET")
        all_set = False
    
    return all_set


def test_supabase_client():
    """Check if Supabase client initializes correctly."""
    print("\n🔍 Testing Supabase client initialization...")
    
    if supabase_client is None:
        print("  ❌ Supabase client is not initialized")
        print("     Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set in your .env file")
        return False
    
    print("  ✅ Supabase client initialized successfully")
    
    # Try to verify connection
    if verify_supabase_connection():
        print("  ✅ Supabase API connection verified")
        return True
    else:
        print("  ⚠️  Could not verify Supabase API connection (this may be normal)")
        return True  # Still return True as client is initialized


def test_database_connection():
    """Test PostgreSQL database connection."""
    print("\n🔍 Testing PostgreSQL database connection...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"  ✅ Database connection successful!")
            print(f"     PostgreSQL version: {version.split(',')[0]}")
            return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {str(e)}")
        print("\n  Possible solutions:")
        print("  1. Verify your database password in .env file")
        print("  2. Check that your IP is allowed in Supabase Network Restrictions")
        print("  3. Ensure the database host and port are correct")
        print("  4. Go to: https://app.supabase.com/project/aupzonugezawvtcfkyvj/settings/database")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Supabase Connection Test")
    print("=" * 60)
    
    # Test 1: Environment variables
    env_ok = test_environment_variables()
    
    # Test 2: Supabase client
    client_ok = test_supabase_client()
    
    # Test 3: Database connection
    db_ok = test_database_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if env_ok and client_ok and db_ok:
        print("✅ All tests passed! You're ready to run migrations.")
        print("\nNext steps:")
        print("  1. Run migrations: python manage.py migrate")
        print("  2. Create superuser: python manage.py createsuperuser")
        print("  3. Start server: python manage.py runserver")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        if not env_ok:
            print("\n⚠️  Environment variables issue:")
            print("   Make sure you have a .env file with all required variables")
            print("   See SUPABASE_SETUP.md for detailed instructions")
        if not db_ok:
            print("\n⚠️  Database connection issue:")
            print("   Check your database password and network settings")
            print("   See SUPABASE_SETUP.md for troubleshooting")
        return 1


if __name__ == "__main__":
    sys.exit(main())
