from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["title", "icon", "is_deleted", "created_at"]
    list_filter = ["is_deleted"]
    search_fields = ["title", "short_description"]
    prepopulated_fields = {"slug": ("title",)}