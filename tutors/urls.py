from django.urls import path

from tutors import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('tutor-dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('tutor-profile/', views.tutor_profile, name='tutor_profile'),
]