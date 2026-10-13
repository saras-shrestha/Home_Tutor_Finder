from django.urls import path

from admin_panel import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tutors-list/', views.tutors_list, name='tutors_list'),
    path('students-list/', views.students_list, name='students_list'),
    path('tutors-approval/', views.tutors_approval, name='tutors_approval'),
    path('tutor/<int:id>/review', views.tutor_review, name='tutor_review'),
    path('tutor/<int:id>/review-update', views.tutor_review, name='review_update'),
    path('regions/', views.regions, name='regions'),
    path('login/', views.admin_login, name='admin_login'),   
    path('logout/', views.admin_logout, name='admin_logout'),
]


