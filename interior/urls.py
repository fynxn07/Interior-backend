from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/services/",include("services.urls")),
    path("api/projects/", include("projects.urls")),
    path("api/materials/", include("materials.urls")),
    path("api/contacts/", include("contacts.urls")),
    path("api/quotations/", include("quotations.urls")),
    path("api/careers/", include("careers.urls")),
    
]


