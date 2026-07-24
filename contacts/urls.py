from django.urls import path
from .views import (
    ContactMessageListCreateView,
    ContactMessageDetailView,
    ContactMessageReplyView,
)

urlpatterns = [
    path("", ContactMessageListCreateView.as_view(), name="contact-list-create"),
    path("<int:pk>/", ContactMessageDetailView.as_view(), name="contact-detail"),
    path("<int:pk>/reply/", ContactMessageReplyView.as_view(), name="contact-reply"),
]