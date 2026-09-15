from django.urls import path

from admin_panel import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-login/', views.admin_login, name='admin_login'),
]


