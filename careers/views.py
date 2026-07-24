from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import Job, JobApplication
from .serializers import (
    JobSerializer,
    JobWriteSerializer,
    JobApplicationCreateSerializer,
    JobApplicationSerializer,
    JobApplicationStatusSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


# ---------------- Job Postings — full CRUD ----------------

class JobListCreateView(APIView):
    """
    GET  /api/careers/jobs/   -> public list (only active, non-deleted)
    POST /api/careers/jobs/   -> admin create
    """
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        queryset = Job.objects.filter(is_deleted=False)
        if not (request.user and request.user.is_authenticated and request.user.is_staff):
            queryset = queryset.filter(is_active=True)  # public only sees open roles
        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JobWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save()
        return Response(JobSerializer(job).data, status=status.HTTP_201_CREATED)


class JobDetailView(APIView):
    """
    GET    /api/careers/jobs/<slug>/   -> retrieve
    PUT    /api/careers/jobs/<slug>/   -> full update (admin only)
    PATCH  /api/careers/jobs/<slug>/   -> partial update (admin only)
    DELETE /api/careers/jobs/<slug>/   -> soft delete (admin only)
    """
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, slug):
        return get_object_or_404(Job, slug=slug, is_deleted=False)

    def get(self, request, slug):
        job = self.get_object(slug)
        return Response(JobSerializer(job).data)

    def put(self, request, slug):
        job = self.get_object(slug)
        serializer = JobWriteSerializer(job, data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save()
        return Response(JobSerializer(job).data)

    def patch(self, request, slug):
        job = self.get_object(slug)
        serializer = JobWriteSerializer(job, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        job = serializer.save()
        return Response(JobSerializer(job).data)

    def delete(self, request, slug):
        job = self.get_object(slug)
        job.is_deleted = True
        job.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------- Applications — create + admin view/status/delete only ----------------

class JobApplicationListCreateView(APIView):
    """
    GET  /api/careers/applications/   -> admin-only list, with ?status=
    POST /api/careers/applications/   -> public submit, multipart (resume file)
    """
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get(self, request):
        queryset = JobApplication.objects.filter(is_deleted=False)
        status_filter = request.query_params.get("status")
        if status_filter and status_filter != "All":
            queryset = queryset.filter(status=status_filter)
        serializer = JobApplicationSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JobApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        return Response(
            JobApplicationSerializer(application).data,
            status=status.HTTP_201_CREATED,
        )


class JobApplicationDetailView(APIView):
    """
    GET    /api/careers/applications/<id>/          -> admin retrieve
    PATCH  /api/careers/applications/<id>/status/    -> admin status only (separate action below)
    DELETE /api/careers/applications/<id>/           -> admin soft delete

    No PUT/PATCH on the main resource — matches exactly what you asked:
    admin can never edit what a candidate submitted.
    """
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(JobApplication, pk=pk, is_deleted=False)

    def get(self, request, pk):
        application = self.get_object(pk)
        return Response(JobApplicationSerializer(application).data)

    def delete(self, request, pk):
        application = self.get_object(pk)
        application.is_deleted = True
        application.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class JobApplicationStatusView(APIView):
    """
    PATCH /api/careers/applications/<id>/status/   -> admin only, status field only
    """
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        application = get_object_or_404(JobApplication, pk=pk, is_deleted=False)
        serializer = JobApplicationStatusSerializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        return Response(JobApplicationSerializer(application).data)