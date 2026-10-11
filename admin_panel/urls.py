from django.urls import path

from admin_panel import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tutors-list/', views.tutors_list, name='tutors_list'),
    path('login/', views.admin_login, name='admin_login'),   
    path('logout/', views.admin_logout, name='admin_logout'),
]


