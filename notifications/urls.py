from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_notifications, name='all_notifications'),
    path('fetch/', views.fetch_notifications, name='fetch_notifications'),
    path('read/<int:pk>/', views.mark_as_read, name='mark_as_read'),
    path('read-all/', views.mark_all_as_read, name='mark_all_as_read'),
]
