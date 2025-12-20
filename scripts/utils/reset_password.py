#!/usr/bin/env python
"""Reset password for test user."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from accounts.models import User

# Get or create test user
username = "test"
password = "testpass"

try:
    user = User.objects.get(username=username)
    print(f"User found: {username}")
    print(f"  Is active: {user.is_active}")
    print(f"  Is staff: {user.is_staff}")
    print(f"  Is superuser: {user.is_superuser}")
    
    # Check current password
    if user.check_password(password):
        print(f"  Password '{password}' is already correct!")
    else:
        print(f"  Password check failed. Resetting password...")
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"  Password reset successfully!")
    
    # Ensure user is active
    if not user.is_active:
        user.is_active = True
        user.save()
        print(f"  User activated!")
        
except User.DoesNotExist:
    print(f"User '{username}' not found. Creating new user...")
    user = User.objects.create_superuser(
        username=username,
        email="wanilyatasnim@test.my",
        password=password
    )
    print(f"User created successfully!")

print("\n" + "="*50)
print("LOGIN CREDENTIALS:")
print("="*50)
print(f"Username: {username}")
print(f"Password: {password}")
print("="*50)

