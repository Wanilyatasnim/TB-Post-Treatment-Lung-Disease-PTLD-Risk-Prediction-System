"""
Role-Based Access Control (RBAC) for PTLD Risk Prediction System

Implements permission checks based on user roles:
- Admin: Full access to all resources
- Clinician: Can view and create patients, predictions, regimens, visits
- Researcher: Read-only access to data for analysis
"""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Only admin users can access."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'admin'
        )


class IsClinician(permissions.BasePermission):
    """Clinicians can access."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role in ['admin', 'clinician']
        )


class IsResearcher(permissions.BasePermission):
    """Researchers have read-only access."""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not hasattr(request.user, 'role'):
            return False
        
        # Admin and clinician can do everything
        if request.user.role in ['admin', 'clinician']:
            return True
        
        # Researchers can only read (GET, HEAD, OPTIONS)
        if request.user.role == 'researcher':
            return request.method in permissions.SAFE_METHODS
        
        return False


class PatientPermission(permissions.BasePermission):
    """
    Permission class for Patient operations:
    - Admin: Full access
    - Clinician: Can create, read, update patients
    - Researcher: Read-only
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not hasattr(request.user, 'role'):
            return False
        
        role = request.user.role
        
        # Admin: full access
        if role == 'admin':
            return True
        
        # Clinician: can create, read, update
        if role == 'clinician':
            return True
        
        # Researcher: read-only
        if role == 'researcher':
            return request.method in permissions.SAFE_METHODS
        
        return False


class PredictionPermission(permissions.BasePermission):
    """
    Permission class for Risk Prediction operations:
    - Admin: Full access
    - Clinician: Can create and view predictions
    - Researcher: Read-only
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            # Allow unauthenticated for predict endpoint (for development)
            if view.action == 'predict' and request.method == 'POST':
                return True
            return False
        
        if not hasattr(request.user, 'role'):
            return False
        
        role = request.user.role
        
        # Admin: full access
        if role == 'admin':
            return True
        
        # Clinician: can create and view
        if role == 'clinician':
            return True
        
        # Researcher: read-only
        if role == 'researcher':
            return request.method in permissions.SAFE_METHODS
        
        return False


