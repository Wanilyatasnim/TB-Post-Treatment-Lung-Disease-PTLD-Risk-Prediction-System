#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify researcher can access all population-level statistics.
Run: python test_researcher_access.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from accounts.models import User
from django.test import Client, override_settings
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

def safe_print(msg):
    """Print with UTF-8 encoding for Windows compatibility."""
    sys.stdout.buffer.write(f"{msg}\n".encode('utf-8'))

@override_settings(ALLOWED_HOSTS=['*'])
def test_researcher_access():
    """Test that researcher can access all population-level statistics."""
    safe_print("=" * 60)
    safe_print("Testing Researcher Access to Population-Level Statistics")
    safe_print("=" * 60)
    
    # Get researcher user
    try:
        researcher = User.objects.get(username='data')
        safe_print(f"\n[OK] Found researcher user: {researcher.username} (role: {researcher.role})")
    except User.DoesNotExist:
        safe_print("\n[ERROR] Researcher user 'data' not found!")
        safe_print("Available users:")
        for u in User.objects.all():
            safe_print(f"  - {u.username} ({u.role})")
        return False
    
    # Create API client and authenticate
    client = APIClient()
    token, created = Token.objects.get_or_create(user=researcher)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    safe_print(f"[OK] Authenticated as researcher (token: {'created' if created else 'existing'})")
    
    # Test endpoints
    endpoints = [
        ('/researchers/api/risk-trend/', 'Risk Trend Analysis'),
        ('/researchers/api/risk-distribution/', 'Risk Distribution'),
        ('/researchers/api/group-comparison/?group=age', 'Group Comparison (Age)'),
        ('/researchers/api/group-comparison/?group=sex', 'Group Comparison (Sex)'),
        ('/researchers/api/shap-analysis/', 'SHAP Analysis'),
        ('/researchers/api/outcome-association/', 'Outcome Association'),
    ]
    
    safe_print("\n" + "=" * 60)
    safe_print("Testing API Endpoints")
    safe_print("=" * 60)
    
    all_passed = True
    for endpoint, name in endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                safe_print(f"[OK] {name}: Status {response.status_code}")
                if hasattr(response, 'data'):
                    safe_print(f"  Data keys: {list(response.data.keys())}")
            else:
                safe_print(f"[FAIL] {name}: Status {response.status_code}")
                if hasattr(response, 'data'):
                    safe_print(f"  Error: {response.data}")
                all_passed = False
        except Exception as e:
            safe_print(f"[ERROR] {name}: {e}")
            all_passed = False
    
    # Test dashboard access
    safe_print("\n" + "=" * 60)
    safe_print("Testing Dashboard Access")
    safe_print("=" * 60)
    
    web_client = Client()
    web_client.force_login(researcher)
    
    try:
        response = web_client.get('/researchers/dashboard/')
        if response.status_code == 200:
            safe_print("[OK] Researcher Dashboard: Status 200")
        else:
            safe_print(f"[FAIL] Researcher Dashboard: Status {response.status_code}")
            all_passed = False
    except Exception as e:
        safe_print(f"[ERROR] Researcher Dashboard: {e}")
        all_passed = False
    
    # Test that researcher cannot access clinician dashboard
    safe_print("\n" + "=" * 60)
    safe_print("Testing Access Restrictions")
    safe_print("=" * 60)
    
    try:
        response = web_client.get('/patients/dashboard/overview/')
        if response.status_code == 302:  # Should redirect
            safe_print("[OK] Clinician Dashboard: Properly blocked (redirected)")
        else:
            safe_print(f"[WARN] Clinician Dashboard: Unexpected status ({response.status_code})")
    except Exception as e:
        safe_print(f"[ERROR] Clinician Dashboard test: {e}")
    
    # Summary
    safe_print("\n" + "=" * 60)
    if all_passed:
        safe_print("[SUCCESS] ALL TESTS PASSED - Researcher can access population-level statistics")
    else:
        safe_print("[FAILURE] SOME TESTS FAILED - Check errors above")
    safe_print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_researcher_access()
    sys.exit(0 if success else 1)

