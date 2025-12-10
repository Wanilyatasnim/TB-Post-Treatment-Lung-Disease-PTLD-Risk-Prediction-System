"""
Audit Logging Utility

Provides functions to log user actions for compliance and tracking.
"""

import logging
from django.contrib.auth import get_user_model
from clinical.models import AuditLog

logger = logging.getLogger(__name__)
User = get_user_model()


def log_action(
    user,
    action,
    model_name,
    object_id='',
    description='',
    request=None
):
    """
    Log a user action to the audit log.
    
    Args:
        user: User instance or None
        action: Action type (create, update, delete, view, predict, export, login, logout)
        model_name: Name of the model/entity (e.g., 'Patient', 'RiskPrediction')
        object_id: ID of the object acted upon
        description: Human-readable description
        request: Django request object (optional, for IP and user agent)
    """
    try:
        ip_address = None
        user_agent = ''
        
        if request:
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
        
        AuditLog.objects.create(
            user=user if user and user.is_authenticated else None,
            action=action,
            model_name=model_name,
            object_id=str(object_id),
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception as e:
        # Don't fail the request if audit logging fails
        logger.error(f"Failed to create audit log: {e}")


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

