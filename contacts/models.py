from django.db import models


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ("unread", "Unread"),
        ("read", "Read"),
        ("replied", "Replied"),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    service = models.CharField(max_length=150, blank=True)
    message = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unread", db_index=True)
    reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.status}"