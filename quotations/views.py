from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.throttling import AnonRateThrottle
from django.shortcuts import get_object_or_404

from .models import Quotation, QuotationImage
from .serializers import (
    QuotationCreateSerializer,
    QuotationListSerializer,
    QuotationDetailSerializer,
    QuotationUpdateSerializer,
)


class QuotationSubmitThrottle(AnonRateThrottle):
    scope = "quotation_submit"


class QuotationListCreateView(APIView):
    """
    GET  /api/quotations/   -> admin-only list, with ?status=
    POST /api/quotations/   -> public submit (throttled), accepts multiple
                               files under the "images" field name — matches
                               the frontend wizard submitting everything in
                               one go at Step 4.
    """
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_throttles(self):
        if self.request.method == "POST":
            return [QuotationSubmitThrottle()]
        return []

    def get(self, request):
        queryset = Quotation.objects.filter(is_deleted=False)

        status_filter = request.query_params.get("status")
        if status_filter and status_filter != "All":
            queryset = queryset.filter(status=status_filter)

        serializer = QuotationListSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = QuotationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quotation = serializer.save()

        # Handle up to 6 images submitted alongside the request —
        # matches the frontend wizard's "up to 6" limit in StepPhotos.
        images = request.FILES.getlist("images")[:6]
        for image_file in images:
            QuotationImage.objects.create(quotation=quotation, image=image_file)

        return Response(
            QuotationDetailSerializer(quotation).data,
            status=status.HTTP_201_CREATED,
        )


class QuotationDetailView(APIView):
    """
    GET    /api/quotations/<id>/   -> admin retrieve
    PATCH  /api/quotations/<id>/   -> admin update (status/assigned_to/price/remarks only)
    DELETE /api/quotations/<id>/   -> admin soft delete

    No PUT here — same reasoning as Contacts. There's no "full replace"
    concept that makes sense for a quotation; only the specific admin
    fields via PATCH.
    """
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(Quotation, pk=pk, is_deleted=False)

    def get(self, request, pk):
        quotation = self.get_object(pk)
        return Response(QuotationDetailSerializer(quotation).data)

    def patch(self, request, pk):
        quotation = self.get_object(pk)
        serializer = QuotationUpdateSerializer(quotation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        quotation = serializer.save()
        return Response(QuotationDetailSerializer(quotation).data)

    def delete(self, request, pk):
        quotation = self.get_object(pk)
        quotation.is_deleted = True
        quotation.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)