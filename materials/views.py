from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import Material
from .serializers import MaterialSerializer, MaterialWriteSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class MaterialListCreateView(APIView):
    """
    GET  /api/materials/          -> list, with ?group=, ?search=
    POST /api/materials/          -> create (admin only)

    No pagination here — your public Materials page renders the full
    directory on one filterable grid (like the real PDF), not a paged list.
    The dataset is small (dozens, not thousands), so this is intentional,
    not an oversight.
    """
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        queryset = Material.objects.filter(is_deleted=False)

        group = request.query_params.get("group")
        if group and group != "All":
            queryset = queryset.filter(group=group)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(brand__icontains=search) | \
                       queryset.filter(category__icontains=search)

        serializer = MaterialSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MaterialWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        material = serializer.save()
        return Response(
            MaterialSerializer(material).data,
            status=status.HTTP_201_CREATED,
        )


class MaterialDetailView(APIView):
    """
    GET    /api/materials/<id>/   -> retrieve
    PUT    /api/materials/<id>/   -> full update
    PATCH  /api/materials/<id>/   -> partial update
    DELETE /api/materials/<id>/   -> soft delete
    """
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        return get_object_or_404(Material, pk=pk, is_deleted=False)

    def get(self, request, pk):
        material = self.get_object(pk)
        return Response(MaterialSerializer(material).data)

    def put(self, request, pk):
        material = self.get_object(pk)
        serializer = MaterialWriteSerializer(material, data=request.data)
        serializer.is_valid(raise_exception=True)
        material = serializer.save()
        return Response(MaterialSerializer(material).data)

    def patch(self, request, pk):
        material = self.get_object(pk)
        serializer = MaterialWriteSerializer(material, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        material = serializer.save()
        return Response(MaterialSerializer(material).data)

    def delete(self, request, pk):
        material = self.get_object(pk)
        material.is_deleted = True
        material.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)