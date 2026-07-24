from rest_framework import serializers
from .models import Job, JobApplication


class JobSerializer(serializers.ModelSerializer):
    postedDate = serializers.DateTimeField(source="posted_date", read_only=True)

    class Meta:
        model = Job
        fields = [
            "id", "slug", "title", "department", "location", "type",
            "description", "responsibilities", "requirements",
            "is_active", "postedDate",
        ]


class JobWriteSerializer(serializers.ModelSerializer):
    """Accepts responsibilities/requirements as either a real JSON array
    or a newline-separated string — matches JobFormModal.jsx's textarea,
    same pattern as Service's scope field."""
    responsibilities = serializers.CharField(required=False, allow_blank=True)
    requirements = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Job
        fields = [
            "title", "department", "location", "type",
            "description", "responsibilities", "requirements", "is_active",
        ]

    def _to_list(self, value):
        if isinstance(value, list):
            return value
        return [line.strip() for line in str(value).split("\n") if line.strip()]

    def validate_responsibilities(self, value):
        return self._to_list(value)

    def validate_requirements(self, value):
        return self._to_list(value)


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """Public-facing. Excludes status/is_deleted — same lockdown principle
    as ContactMessageCreateSerializer and QuotationCreateSerializer."""

    class Meta:
        model = JobApplication
        fields = ["job", "name", "email", "phone", "cover_message", "resume"]

    def validate_job(self, value):
        if not value.is_active or value.is_deleted:
            raise serializers.ValidationError("This job posting is no longer accepting applications.")
        return value


class JobApplicationSerializer(serializers.ModelSerializer):
    """Admin-facing read serializer — matches ApplicationDetailModal.jsx
    and the Applications tab's row shape exactly."""
    jobTitle = serializers.CharField(source="job.title", read_only=True)
    jobSlug = serializers.CharField(source="job.slug", read_only=True)
    coverMessage = serializers.CharField(source="cover_message", read_only=True)
    submittedAt = serializers.DateTimeField(source="submitted_at", read_only=True)
    resume = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = [
            "id", "jobTitle", "jobSlug", "name", "email", "phone",
            "coverMessage", "resume", "status", "submittedAt",
        ]

    def get_resume(self, obj):
        return obj.resume.url if obj.resume else None


class JobApplicationStatusSerializer(serializers.ModelSerializer):
    """Admin-only, and only status — the single thing AdminCareers.jsx's
    Applications tab actually changes via the status dropdown."""

    class Meta:
        model = JobApplication
        fields = ["status"]