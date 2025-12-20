#!/usr/bin/env python
"""Check admin credentials and create admin user if needed."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from accounts.models import User

print("="*60)
print("ADMIN PANEL ACCESS")
print("="*60)

# Check all superusers
superusers = User.objects.filter(is_superuser=True)

if superusers.exists():
    print("\nSuperuser accounts (can access admin panel):")
    print("-" * 60)
    for user in superusers:
        print(f"Username: {user.username}")
        print(f"Email: {user.email or '(no email)'}")
        print(f"Is Active: {user.is_active}")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")
        print()
else:
    print("No superuser found!")

print("="*60)
print("ADMIN PANEL LOGIN:")
print("="*60)
print("URL: http://localhost:8000/admin/")
if superusers.exists():
    admin_user = superusers.first()
    print(f"Username: {admin_user.username}")
    print(f"Password: testpass")
    print("\nNote: Same credentials work for both:")
    print("  - Regular login: http://localhost:8000/accounts/login/")
    print("  - Admin panel: http://localhost:8000/admin/")
else:
    print("No admin user available!")
print("="*60)

