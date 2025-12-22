#!/usr/bin/env python
"""
Fix user login issues - reset password and verify user status
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from accounts.models import User

def fix_user(username, new_password=None):
    """Fix a user's login by resetting password and verifying status."""
    try:
        user = User.objects.get(username=username)
        print(f"\nFound user: {username}")
        print(f"  ID: {user.id}")
        print(f"  Role: {user.role}")
        print(f"  Active: {user.is_active}")
        print(f"  Staff: {user.is_staff}")
        print(f"  Superuser: {user.is_superuser}")
        print(f"  Has Password: {bool(user.password)}")
        
        # Ensure user can login
        if not user.is_active:
            user.is_active = True
            print("  ✓ Activated user")
        
        # Ensure user can access admin (if needed)
        if not user.is_staff and user.role in ['admin', 'researcher']:
            user.is_staff = True
            print("  ✓ Enabled staff access")
        
        # Reset password if provided
        if new_password:
            user.set_password(new_password)
            print(f"  ✓ Password reset")
        
        user.save()
        
        print(f"\n✅ User '{username}' is ready to login!")
        if new_password:
            print(f"   Username: {username}")
            print(f"   Password: {new_password}")
        else:
            print(f"   (Password unchanged - use existing password)")
        
        return True
        
    except User.DoesNotExist:
        print(f"\n❌ User '{username}' not found!")
        print("\nAvailable users:")
        for u in User.objects.all():
            print(f"  - {u.username} ({u.role})")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_user_login.py <username> [new_password]")
        print("\nExample:")
        print("  python fix_user_login.py data password123")
        print("  python fix_user_login.py data  # (just verify, don't reset password)")
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2] if len(sys.argv) > 2 else None
    
    fix_user(username, new_password)

