from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
import accounts.views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',account_views.homePage, name="home-page"),
    path("findtutors/", account_views.homePage, {"section": "findtutors"}, name="find-your-tutors"),
    path("how-it-works/", account_views.homePage, {"section": "how-it-works"}, name="how-it-works"),
    path("about/", account_views.homePage, {"section": "about"}, name="about"),
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('tutors/', include('tutors.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )
