from django.contrib import admin

from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "clinic", "is_active", "is_staff")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "clinic")



