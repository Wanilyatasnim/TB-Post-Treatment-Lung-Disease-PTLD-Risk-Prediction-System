from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("clinician", "Clinician"),
        ("researcher", "Researcher"),
        ("admin", "Admin"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="clinician")
    clinic = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"



