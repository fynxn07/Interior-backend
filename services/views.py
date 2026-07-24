from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from .models import Service
from .serializers import ServiceSerializer, ServiceWriteSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class ServicePagination(PageNumberPagination):
    page_size = 12


class ServiceListCreateView(APIView):
    """
    GET  /api/services/   -> list, with ?search=, ?ordering=
    POST /api/services/   -> create (admin only)
    """
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        queryset = Service.objects.filter(is_deleted=False)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search) | \
                       queryset.filter(short_description__icontains=search)

        ordering = request.query_params.get("ordering", "created_at")
        allowed_ordering = {"created_at", "-created_at", "title", "-title"}
        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)

        paginator = ServicePagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ServiceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ServiceWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        return Response(
            ServiceSerializer(service).data,
            status=status.HTTP_201_CREATED,
        )


class ServiceDetailView(APIView):
    """
    GET    /api/services/<slug>/   -> retrieve
    PUT    /api/services/<slug>/   -> full update
    PATCH  /api/services/<slug>/   -> partial update
    DELETE /api/services/<slug>/   -> soft delete
    """
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, slug):
        return get_object_or_404(Service, slug=slug, is_deleted=False)

    def get(self, request, slug):
        service = self.get_object(slug)
        return Response(ServiceSerializer(service).data)

    def put(self, request, slug):
        service = self.get_object(slug)
        serializer = ServiceWriteSerializer(service, data=request.data)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        return Response(ServiceSerializer(service).data)

    def patch(self, request, slug):
        service = self.get_object(slug)
        serializer = ServiceWriteSerializer(service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        return Response(ServiceSerializer(service).data)

    def delete(self, request, slug):
        service = self.get_object(slug)
        service.is_deleted = True
        service.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)