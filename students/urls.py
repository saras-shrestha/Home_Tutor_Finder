from django.urls import path

from students import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path('get-districts/<int:region_id>/', views.get_districts, name='get_districts'),
    path('get-cities/<int:district_id>/', views.get_cities, name='get_cities'),
]


