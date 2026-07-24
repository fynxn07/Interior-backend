from rest_framework import serializers
from .models import Project, ProjectGalleryImage


class ProjectGalleryImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectGalleryImage
        fields = ["id", "url", "type", "order"]

    def get_url(self, obj):
        return obj.image.url if obj.image else None


class ProjectListSerializer(serializers.ModelSerializer):
    coverImage = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "client", "location", "category",
            "duration", "status", "featured", "coverImage",
        ]

    def get_coverImage(self, obj):
        return obj.cover_image.url if obj.cover_image else None


class ProjectDetailSerializer(serializers.ModelSerializer):
    coverImage = serializers.SerializerMethodField()
    gallery = ProjectGalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "title", "client", "location", "category",
            "duration", "status", "featured", "coverImage", "gallery",
            "created_at", "updated_at",
        ]

    def get_coverImage(self, obj):
        return obj.cover_image.url if obj.cover_image else None


class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "title", "client", "location", "category",
            "duration", "status", "featured", "cover_image",
        ]