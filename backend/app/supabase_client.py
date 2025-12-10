"""
Supabase client initialization and utilities.

This module provides a configured Supabase client for use throughout the Django application.
The client can be used for:
- Authentication (sign up, sign in, social auth)
- Database operations (beyond Django ORM if needed)
- Storage (file uploads)
- Real-time subscriptions
- Edge functions

Usage:
    from app.supabase_client import supabase_client
    
    # Example: Query data directly
    response = supabase_client.table('some_table').select('*').execute()
    
    # Example: Upload file to storage
    supabase_client.storage.from_('bucket_name').upload('path/to/file', file_data)
"""

import os
from supabase import create_client, Client
from django.conf import settings

# Initialize Supabase client
def get_supabase_client() -> Client:
    """
    Create and return a configured Supabase client.
    
    Returns:
        Client: Configured Supabase client instance
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY is not configured
    """
    url = getattr(settings, 'SUPABASE_URL', None)
    key = getattr(settings, 'SUPABASE_KEY', None)
    
    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in Django settings. "
            "Please check your environment variables."
        )
    
    return create_client(url, key)


# Global client instance
# Supabase client is optional - only initialized if credentials are provided
# This allows the app to run with SQLite without Supabase
try:
    supabase_client: Client = get_supabase_client()
except (ValueError, Exception) as e:
    # Allow Django to start even if Supabase is not configured
    # This is useful for running with SQLite or when Supabase is not needed
    supabase_client = None
    # Only warn if Supabase credentials were actually provided
    if getattr(settings, 'SUPABASE_URL', None) or getattr(settings, 'SUPABASE_KEY', None):
        import warnings
        warnings.warn(f"Supabase client not initialized: {e}")


# Helper functions for common operations

def verify_supabase_connection() -> bool:
    """
    Verify that the Supabase client can connect to the service.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    if not supabase_client:
        return False
    
    try:
        # Simple health check - try to access auth
        supabase_client.auth.get_session()
        return True
    except Exception:
        return False


def get_authenticated_user(access_token: str):
    """
    Get user information from an access token.
    
    Args:
        access_token: JWT access token from Supabase Auth
    
    Returns:
        User object if valid, None otherwise
    """
    if not supabase_client:
        return None
    
    try:
        user = supabase_client.auth.get_user(access_token)
        return user
    except Exception:
        return None
