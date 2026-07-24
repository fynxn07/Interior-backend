from django.urls import path

from .views import AdminLoginView,MeView,Tok

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("me/", MeView.as_view(), name="me"),
    
]