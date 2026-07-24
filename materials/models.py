from django.db import models
from cloudinary.models import CloudinaryField


class Material(models.Model):
    GROUP_CHOICES = [
        ("Material Directory", "Material Directory"),
        ("Materials & Colour", "Materials & Colour"),
    ]

    brand = models.CharField(max_length=150)
    logo = CloudinaryField("image", blank=True, null=True)
    category = models.CharField(max_length=150)
    country = models.CharField(max_length=100, blank=True)
    group = models.CharField(max_length=50, choices=GROUP_CHOICES, default="Material Directory")

    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["group", "brand"]

    def __str__(self):
        return f"{self.brand} ({self.group})"