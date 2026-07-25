from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count

from projects.models import Project
from services.models import Service
from materials.models import Material
from quotations.models import Quotation
from contacts.models import ContactMessage
from careers.models import Job, JobApplication


class DashboardStatsView(APIView):
    """
    GET /api/dashboard/stats/  -> admin only.

    Single source of truth for every number the Dashboard page shows.
    Queries each app's models directly (not through the paginated list
    endpoints), so counts are always the true total — not "however many
    fit on page 1."
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        projects = Project.objects.filter(is_deleted=False)
        services = Service.objects.filter(is_deleted=False)
        materials = Material.objects.filter(is_deleted=False)
        quotations = Quotation.objects.filter(is_deleted=False)
        messages = ContactMessage.objects.filter(is_deleted=False)
        jobs = Job.objects.filter(is_deleted=False)
        applications = JobApplication.objects.filter(is_deleted=False)

        # ---- Top-line counts ----
        counts = {
            "projects": projects.count(),
            "services": services.count(),
            "materials": materials.count(),
            "quotations_total": quotations.count(),
            "quotations_pending": quotations.filter(status="pending").count(),
            "messages_total": messages.count(),
            "messages_unread": messages.filter(status="unread").count(),
            "applications_total": applications.count(),
            "jobs_open": jobs.filter(is_active=True).count(),
        }

        # ---- Quotation status breakdown (only statuses that actually have data) ----
        quotation_status_breakdown = [
            {"status": row["status"], "count": row["count"]}
            for row in quotations.values("status").annotate(count=Count("id")).order_by("status")
        ]

        # ---- Projects by category ----
        projects_by_category = [
            {"category": row["category"] or "Uncategorized", "count": row["count"]}
            for row in projects.values("category").annotate(count=Count("id")).order_by("-count")
        ]

        # ---- Content overview ----
        content_overview = {
            "open_job_roles": jobs.filter(is_active=True).count(),
            "featured_projects": projects.filter(featured=True).count(),
            "material_categories": materials.values("group").distinct().count(),
        }

        # ---- Recent activity — merge + sort the 3 lead sources, most recent first ----
        activity = []

        for q in quotations.order_by("-created_at")[:10]:
            activity.append({
                "id": f"q-{q.id}",
                "text": f"New quotation from {q.name or 'a customer'} — {q.service or 'General enquiry'}",
                "date": q.created_at.isoformat(),
                "color": "#8B7CFF",
                "to": "/admin/quotations",
            })

        for m in messages.order_by("-created_at")[:10]:
            activity.append({
                "id": f"m-{m.id}",
                "text": f"New message from {m.name}",
                "date": m.created_at.isoformat(),
                "color": "#22D3EE",
                "to": "/admin/messages",
            })

        for a in applications.select_related("job").order_by("-submitted_at")[:10]:
            activity.append({
                "id": f"a-{a.id}",
                "text": f"Application from {a.name} for {a.job.title}",
                "date": a.submitted_at.isoformat(),
                "color": "#F472B6",
                "to": "/admin/careers",
            })

        activity.sort(key=lambda item: item["date"], reverse=True)
        activity = activity[:7]

        return Response({
            "counts": counts,
            "quotation_status_breakdown": quotation_status_breakdown,
            "projects_by_category": projects_by_category,
            "content_overview": content_overview,
            "activity": activity,
        })