from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField


class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    icon = models.CharField(
        max_length=50,
        help_text="Must match a key in the frontend's ICON_MAP (e.g. FaBuilding, FaHammer).",
    )
    short_description = models.CharField(max_length=300)
    hero_image = CloudinaryField("image", blank=True, null=True)
    description = models.TextField()
    scope = models.JSONField(
        default=list,
        blank=True,
        help_text="Ordered list of strings, e.g. ['Consultation', 'Site Survey'].",
    )

    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]  # oldest first — matches original 4 services' display order

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title