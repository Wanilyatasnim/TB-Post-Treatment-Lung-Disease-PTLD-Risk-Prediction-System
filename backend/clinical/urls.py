from django.urls import path

from clinical import views

urlpatterns = [
    path("health/", views.health, name="api-health"),
]


