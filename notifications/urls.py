
from django.urls import path
from . import views

urlpatterns = [
    path(
        'read/<int:pk>/',
        views.mark_as_read,
        name='mark_as_read'
    ),

    path(
        'read-all/',
        views.mark_all_as_read,
        name='mark_all_as_read'
    ),
]
