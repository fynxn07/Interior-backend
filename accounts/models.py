from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    # Drop username entirely — email is the login identifier
    username = None
    email = models.EmailField(unique=True)

    is_blocked = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # no other required fields when creating a superuser

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ["-created_at"]