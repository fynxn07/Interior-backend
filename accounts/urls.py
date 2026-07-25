from django.urls import path

from .views import AdminLoginView,MeView,TokenRefreshView

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("me/", MeView.as_view(), name="me"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
]