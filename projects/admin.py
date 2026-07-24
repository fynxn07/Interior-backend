from django.contrib import admin
from .models import Project, ProjectGalleryImage


class ProjectGalleryImageInline(admin.TabularInline):
    model = ProjectGalleryImage
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "status", "featured", "is_deleted", "created_at"]
    list_filter = ["category", "featured", "is_deleted"]
    search_fields = ["title", "client", "location"]
    inlines = [ProjectGalleryImageInline]