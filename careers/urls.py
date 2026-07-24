from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    JobApplicationListCreateView,
    JobApplicationDetailView,
    JobApplicationStatusView,
)

urlpatterns = [
    path("jobs/", JobListCreateView.as_view(), name="job-list-create"),
    path("jobs/<slug:slug>/", JobDetailView.as_view(), name="job-detail"),
    path("applications/", JobApplicationListCreateView.as_view(), name="application-list-create"),
    path("applications/<int:pk>/", JobApplicationDetailView.as_view(), name="application-detail"),
    path("applications/<int:pk>/status/", JobApplicationStatusView.as_view(), name="application-status"),
]