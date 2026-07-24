from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id","email","username","is_staff","is_superuser","is_blocked",)
    list_filter = ("is_staff","is_superuser","is_blocked",)
    search_fields = ("email","username",)
    ordering = ("id",)