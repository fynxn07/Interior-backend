from django.contrib import admin
from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ["brand", "category", "group", "country", "is_deleted"]
    list_filter = ["group", "is_deleted"]
    search_fields = ["brand", "category"]