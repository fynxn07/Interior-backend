from rest_framework import serializers
from .models import Quotation, QuotationImage


class QuotationImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = QuotationImage
        fields = ["id", "url"]

    def get_url(self, obj):
        return obj.image.url if obj.image else None


class QuotationCreateSerializer(serializers.ModelSerializer):
    """Public-facing. Deliberately excludes status/assigned_to/price/remarks —
    same principle as ContactMessageCreateSerializer: a submitter can never
    set admin-only fields, even by tampering with the request body."""

    class Meta:
        model = Quotation
        fields = [
            "service", "description", "budget", "location",
            "preferred_date", "name", "email", "phone",
        ]

    def validate_email(self, value):
        return value.lower().strip()


class QuotationListSerializer(serializers.ModelSerializer):
    """Lighter payload for the admin list view — matches AdminQuotations.jsx,
    which never needs images/remarks up front, just enough for the row + filter."""

    class Meta:
        model = Quotation
        fields = [
            "id", "reference", "name", "service", "budget",
            "location", "status", "created_at",
        ]


class QuotationDetailSerializer(serializers.ModelSerializer):
    """Full payload — matches QuotationDetailModal.jsx exactly."""
    images = QuotationImageSerializer(many=True, read_only=True)

    class Meta:
        model = Quotation
        fields = [
            "id", "reference", "service", "description", "budget", "location",
            "preferred_date", "name", "email", "phone", "status",
            "assigned_to", "price", "remarks", "images", "created_at",
        ]


class QuotationUpdateSerializer(serializers.ModelSerializer):
    """Admin-only. Only the fields QuotationDetailModal.jsx actually saves —
    status, assigned_to, price, remarks. Everything the customer submitted
    stays permanently read-only, matching the Contacts app's principle."""

    class Meta:
        model = Quotation
        fields = ["status", "assigned_to", "price", "remarks"]