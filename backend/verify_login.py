#!/usr/bin/env python
"""Verify login credentials."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate

username = "test"
password = "testpass"

try:
    user = User.objects.get(username=username)
    print("="*50)
    print("USER ACCOUNT STATUS:")
    print("="*50)
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Is Active: {user.is_active}")
    print(f"Is Staff: {user.is_staff}")
    print(f"Is Superuser: {user.is_superuser}")
    
    # Check password
    password_check = user.check_password(password)
    print(f"\nPassword Check ('{password}'): {password_check}")
    
    # Try authentication
    auth_user = authenticate(username=username, password=password)
    if auth_user:
        print(f"Authentication: SUCCESS")
    else:
        print(f"Authentication: FAILED")
    
    print("\n" + "="*50)
    print("LOGIN CREDENTIALS:")
    print("="*50)
    print(f"URL: http://localhost:8000/accounts/login/")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("="*50)
    
except User.DoesNotExist:
    print(f"ERROR: User '{username}' not found!")

