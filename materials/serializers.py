from rest_framework import serializers
from .models import Material


class MaterialSerializer(serializers.ModelSerializer):
    """Read serializer — camelCase logo URL matches frontend's materialsData.js shape."""
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = ["id", "brand", "logo", "category", "country", "group"]

    def get_logo(self, obj):
        return obj.logo.url if obj.logo else None


class MaterialWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["brand", "logo", "category", "country", "group"]

    def validate_group(self, value):
        valid_groups = dict(Material.GROUP_CHOICES).keys()
        if value not in valid_groups:
            raise serializers.ValidationError(
                f"Group must be one of: {', '.join(valid_groups)}"
            )
        return value