from django.urls import path

from students import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student_profile/', views.student_profile, name='student_profile'),
]