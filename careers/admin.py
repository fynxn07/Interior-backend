from django.contrib import admin
from .models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "department", "location", "type", "is_active", "posted_date"]
    list_filter = ["department", "type", "is_active", "is_deleted"]
    search_fields = ["title", "department"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ["name", "job", "status", "submitted_at"]
    list_filter = ["status", "is_deleted"]
    search_fields = ["name", "email"]
    readonly_fields = ["name", "email", "phone", "cover_message", "resume", "submitted_at"]