from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from .models import Project, ProjectGalleryImage
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectWriteSerializer,
    ProjectGalleryImageSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class ProjectPagination(PageNumberPagination):
    page_size = 12


class ProjectListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        queryset = Project.objects.filter(is_deleted=False)

        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__iexact=category)

        featured = request.query_params.get("featured")
        if featured is not None:
            queryset = queryset.filter(featured=featured.lower() == "true")

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search) | \
                       queryset.filter(client__icontains=search) | \
                       queryset.filter(location__icontains=search)

        ordering = request.query_params.get("ordering", "-created_at")
        if ordering in {"created_at", "-created_at", "title", "-title"}:
            queryset = queryset.order_by(ordering)

        paginator = ProjectPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProjectListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProjectWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        return Response(ProjectDetailSerializer(project).data, status=status.HTTP_201_CREATED)


class ProjectDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        return get_object_or_404(Project, pk=pk, is_deleted=False)

    def get(self, request, pk):
        project = self.get_object(pk)
        return Response(ProjectDetailSerializer(project).data)

    def put(self, request, pk):
        project = self.get_object(pk)
        serializer = ProjectWriteSerializer(project, data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        return Response(ProjectDetailSerializer(project).data)

    def patch(self, request, pk):
        project = self.get_object(pk)
        serializer = ProjectWriteSerializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        return Response(ProjectDetailSerializer(project).data)

    def delete(self, request, pk):
        project = self.get_object(pk)
        project.is_deleted = True
        project.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectGalleryImageView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, is_deleted=False)
        serializer = ProjectGalleryImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectGalleryImageDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, pk, image_id):
        project = get_object_or_404(Project, pk=pk, is_deleted=False)
        image = get_object_or_404(ProjectGalleryImage, id=image_id, project=project)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)