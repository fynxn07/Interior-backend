import random
from datetime import datetime
from django.db import models
from cloudinary.models import CloudinaryField


def generate_reference():
    """OKD-2026-XXXX, guarantee
    d unique via DB check — regenerates on collision."""
    year = datetime.now().year
    while True:
        candidate = f"OKD-{year}-{random.randint(1000, 9999)}"
        if not Quotation.objects.filter(reference=candidate).exists():
            return candidate


class Quotation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("in-progress", "In Progress"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    ]

    reference = models.CharField(max_length=20, unique=True, editable=False, db_index=True)

    # --- Submitted by the customer — never editable by admin ---
    service = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    budget = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    preferred_date = models.DateField(blank=True, null=True)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    # --- Managed by admin only ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    assigned_to = models.CharField(max_length=150, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(blank=True)

    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_reference()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} — {self.name}"


class QuotationImage(models.Model):
    quotation = models.ForeignKey(Quotation, related_name="images", on_delete=models.CASCADE)
    image = CloudinaryField("image")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]