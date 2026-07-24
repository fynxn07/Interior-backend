from django.db import models
from cloudinary.models import CloudinaryField


class Project(models.Model):
    title = models.CharField(max_length=200)
    client = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=100, blank=True, db_index=True)
    duration = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=100, blank=True)
    featured = models.BooleanField(default=False, db_index=True)
    cover_image = CloudinaryField("image", blank=True, null=True)

    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ProjectGalleryImage(models.Model):
    TYPE_CHOICES = [
        ("standard", "Standard"),
        ("before", "Before"),
        ("after", "After"),
        ("render", "Render"),
    ]

    project = models.ForeignKey(Project, related_name="gallery", on_delete=models.CASCADE)
    image = CloudinaryField("image")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="standard")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.project.title} — {self.type}"