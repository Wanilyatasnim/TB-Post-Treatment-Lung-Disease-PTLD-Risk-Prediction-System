"""
Quick script to reset researcher password
Run: python fix_researcher_password.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from accounts.models import User

# Reset password for 'data' user
username = 'data'
new_password = 'researcher123'  # Change this to your desired password

try:
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.is_active = True
    user.is_staff = True  # Required for admin login
    user.save()
    
    print(f"SUCCESS: Password reset successfully for user '{username}'")
    print(f"   Username: {username}")
    print(f"   Password: {new_password}")
    print(f"   Role: {user.role}")
    print(f"   Active: {user.is_active}")
    print(f"   Staff: {user.is_staff}")
    print("\nYou can now login at:")
    print("  - Main site: http://localhost:8000/accounts/login/")
    print("  - Admin: http://localhost:8000/admin/")
    
except User.DoesNotExist:
    print(f"ERROR: User '{username}' not found!")
    print("\nAvailable users:")
    for u in User.objects.all():
        print(f"  - {u.username} ({u.role})")

