from django.urls import path
from students import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-profile/', views.student_profile, name='student_profile'),

    # tutor management
    path('find-tutors/', views.find_tutors, name='find_tutors'),

    path('get-districts/<int:region_id>/', views.get_districts, name='get_districts'),
    path('get-cities/<int:district_id>/', views.get_cities, name='get_cities'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)