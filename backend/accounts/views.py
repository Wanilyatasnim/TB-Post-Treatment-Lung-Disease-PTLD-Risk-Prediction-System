"""
Authentication views for login and logout.
"""

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from clinical.audit import log_action


class CustomLoginView(LoginView):
    """Custom login view with audit logging."""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to patient list after login."""
        return reverse_lazy('patients:patient-list')
    
    def form_valid(self, form):
        """Log successful login."""
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action='login',
            model_name='User',
            object_id=str(self.request.user.id),
            description=f'User {self.request.user.username} logged in',
            request=self.request
        )
        return response


class CustomLogoutView(RedirectView):
    """Custom logout view with audit logging."""
    url = reverse_lazy('accounts:login')
    
    def get(self, request, *args, **kwargs):
        """Log logout action before logging out."""
        if request.user.is_authenticated:
            log_action(
                user=request.user,
                action='logout',
                model_name='User',
                object_id=str(request.user.id),
                description=f'User {request.user.username} logged out',
                request=request
            )
        logout(request)
        return redirect(self.url)


