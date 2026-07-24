from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.throttling import AnonRateThrottle
from django.shortcuts import get_object_or_404

from .models import ContactMessage
from .serializers import (
    ContactMessageCreateSerializer,
    ContactMessageSerializer,
    ContactMessageReplySerializer,
)


class ContactSubmitThrottle(AnonRateThrottle):
    """Basic anti-spam guard — 5 submissions per hour per IP.
    Add this rate to settings.py's REST_FRAMEWORK config (shown below)."""
    scope = "contact_submit"


class ContactMessageListCreateView(APIView):
    """
    GET  /api/contacts/   -> admin-only list, with ?status=
    POST /api/contacts/   -> public submit (throttled, no auth required)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_throttles(self):
        if self.request.method == "POST":
            return [ContactSubmitThrottle()]
        return []

    def get(self, request):
        queryset = ContactMessage.objects.filter(is_deleted=False)

        status_filter = request.query_params.get("status")
        if status_filter and status_filter != "All":
            queryset = queryset.filter(status=status_filter)

        serializer = ContactMessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response(
            ContactMessageSerializer(message).data,
            status=status.HTTP_201_CREATED,
        )


class ContactMessageDetailView(APIView):
    """
    GET    /api/contacts/<id>/   -> retrieve (admin only) — also marks as read
    DELETE /api/contacts/<id>/   -> soft delete (admin only)

    No PUT/PATCH here deliberately — admin should never edit what a
    customer actually submitted. The only "edit" is via the dedicated
    reply endpoint below, which only touches reply/status/replied_at.
    """
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(ContactMessage, pk=pk, is_deleted=False)

    def get(self, request, pk):
        message = self.get_object(pk)
        if message.status == "unread":
            message.status = "read"
            message.save(update_fields=["status"])
        return Response(ContactMessageSerializer(message).data)

    def delete(self, request, pk):
        message = self.get_object(pk)
        message.is_deleted = True
        message.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContactMessageReplyView(APIView):
    """
    POST /api/contacts/<id>/reply/   -> admin only
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        message = get_object_or_404(ContactMessage, pk=pk, is_deleted=False)
        serializer = ContactMessageReplySerializer(instance=message, data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response(ContactMessageSerializer(message).data)