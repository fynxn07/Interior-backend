from rest_framework import serializers
from django.utils import timezone
from .models import ContactMessage


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Public-facing — anyone can submit this, so keep it minimal and safe.
    Deliberately excludes status/reply/is_deleted so a submitter can never
    set those themselves, even if they tamper with the request body."""

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "service", "message"]

    def validate_message(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Message is too short.")
        return value


class ContactMessageSerializer(serializers.ModelSerializer):
    """Admin-facing read serializer — camelCase matches the frontend's
    useContactMessages.js shape exactly (createdAt, repliedAt)."""
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    repliedAt = serializers.DateTimeField(source="replied_at", read_only=True)

    class Meta:
        model = ContactMessage
        fields = [
            "id", "name", "email", "phone", "service", "message",
            "status", "reply", "repliedAt", "createdAt",
        ]


class ContactMessageReplySerializer(serializers.Serializer):
    """Dedicated serializer for the reply action — not a ModelSerializer,
    since replying is a specific action with its own side effect
    (auto-setting status + replied_at), not a generic field update."""
    reply = serializers.CharField()

    def save(self, **kwargs):
        message = self.instance
        message.reply = self.validated_data["reply"]
        message.status = "replied"
        message.replied_at = timezone.now()
        message.save(update_fields=["reply", "status", "replied_at"])
        return message