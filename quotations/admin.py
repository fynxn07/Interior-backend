from django.contrib import admin
from .models import Quotation, QuotationImage


class QuotationImageInline(admin.TabularInline):
    model = QuotationImage
    extra = 0
    readonly_fields = ["image"]


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ["reference", "name", "service", "status", "created_at"]
    list_filter = ["status", "is_deleted"]
    search_fields = ["reference", "name", "email"]
    readonly_fields = ["reference", "created_at", "updated_at"]
    inlines = [QuotationImageInline]