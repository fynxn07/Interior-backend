from rest_framework import serializers
from .models import Project, ProjectGalleryImage


class ProjectGalleryImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectGalleryImage
        fields = ["id", "url", "order"]

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
    gallery_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "client",
            "location",
            "category",
            "duration",
            "status",
            "featured",
            "cover_image",
            "gallery_images",
        ]

    def create(self, validated_data):
        gallery_images = validated_data.pop("gallery_images", [])

        project = Project.objects.create(**validated_data)

        for index, image in enumerate(gallery_images):
            ProjectGalleryImage.objects.create(
                project=project,
                image=image,
                order=index,
            )

        return project

    def update(self, instance, validated_data):
        gallery_images = validated_data.pop("gallery_images", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if gallery_images is not None:
            instance.gallery.all().delete()

            for index, image in enumerate(gallery_images):
                ProjectGalleryImage.objects.create(
                    project=instance,
                    image=image,
                    order=index,
                )

        return instance


