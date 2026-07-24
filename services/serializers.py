from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    heroImage = serializers.SerializerMethodField()
    shortDescription = serializers.CharField(source="short_description")

    class Meta:
        model = Service
        fields = [
            "id", "slug", "title", "icon", "shortDescription",
            "heroImage", "description", "scope",
        ]

    def get_heroImage(self, obj):
        return obj.hero_image.url if obj.hero_image else None


class ServiceWriteSerializer(serializers.ModelSerializer):
    """Handles both JSON (scope as a real array) and multipart (scope as a
    newline-separated string, matching how your admin's textarea submits it)."""
    short_description = serializers.CharField()
    scope = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Service
        fields = ["title", "icon", "short_description", "hero_image", "description", "scope"]

    def validate_scope(self, value):
        if isinstance(value, list):
            return value
        # multipart/form-data can't send real arrays — accept "one per line" text
        return [line.strip() for line in str(value).split("\n") if line.strip()]