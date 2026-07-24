from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "status", "created_at"]
    list_filter = ["status", "is_deleted"]
    search_fields = ["name", "email", "message"]
    readonly_fields = ["created_at"]