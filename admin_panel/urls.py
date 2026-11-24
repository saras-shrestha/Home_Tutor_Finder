from django.urls import path
from admin_panel import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # tutors
    path('tutors-list/', views.tutors_list, name='tutors_list'),
    path('tutors-approval/', views.tutors_approval, name='tutors_approval'),
    path('tutor/<int:id>/review', views.tutor_review, name='tutor_review'),
    path('tutor/<int:id>/review-update', views.tutor_review, name='review_update'),
    path('tutor/<int:id>/info', views.tutor_info, name='tutor_info'),

    # students    
    path('students-list/', views.students_list, name='students_list'),
    path('student/<int:student_id>/info', views.student_info, name='student_info'),

    # student-tutor
    path('student-tutor-requests/', views.student_tutor_requests, name='student_tutor_requests'),

    # grades
    path('grades-list/', views.grades_list, name='grades_list'),
    path('grade/<int:id>/edit', views.grade_edit, name='grade_edit'),
    path('grade/<int:id>/delete', views.grade_delete, name='grade_delete'),

    # subjects
    path('subjects-list/', views.subjects_list, name='subjects_list'),
    path('subjects/<int:id>/edit', views.subject_edit, name='subject_edit'),
    path('subjects/<int:id>/delete', views.subject_delete, name='subject_delete'),

    path('grade-subject/', views.grade_subject, name='grade_subject'),
    path('get-grade-subjects/<int:grade_id>/', views.get_grade_subjects, name='get_grade_subjects'),

    path('login/', views.admin_login, name='admin_login'),   
    path('logout/', views.admin_logout, name='admin_logout'),

    # my_profile
    path('my-admin-profile/', views.my_admin_profile, name='my_admin_profile'), 
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

