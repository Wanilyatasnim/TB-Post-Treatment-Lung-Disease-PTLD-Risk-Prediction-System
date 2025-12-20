#!/usr/bin/env python
"""Quick script to create a superuser if one doesn't exist."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from accounts.models import User

# Check if superuser exists
superusers = User.objects.filter(is_superuser=True)

if superusers.exists():
    print("Existing superusers found:")
    for user in superusers:
        print(f"  - Username: {user.username}")
        print(f"    Email: {user.email or '(no email)'}")
else:
    print("No superuser found. Creating one...")
    # Create superuser
    username = "admin"
    email = "admin@example.com"
    password = "admin123"
    
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"Superuser created:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  Email: {email}")

