from django.urls import path
from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    ProjectGalleryImageView,
    ProjectGalleryImageDetailView,
)

urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="project-list-create"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("<int:pk>/gallery/", ProjectGalleryImageView.as_view(), name="project-gallery-add"),
    path("<int:pk>/gallery/<int:image_id>/", ProjectGalleryImageDetailView.as_view(), name="project-gallery-delete"),
]