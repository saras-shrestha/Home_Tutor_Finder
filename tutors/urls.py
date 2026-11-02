from django.urls import path
from tutors import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('tutor-dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('tutor-profile/', views.tutor_profile, name='tutor_profile'),
    path('availability/', views.tutor_availability, name='tutor_availability'),
    path('availability/<int:pk>/edit/', views.edit_availability, name='edit_availability'),
    path('availability/<int:pk>/delete/', views.delete_availability, name='delete_availability'),

    # manage teaching fees
    path('fees-management/', views.teaching_fees, name='teaching_fees'),
    path('grade-subjects/<int:grade_id>/', views.get_subjects, name='get_subjects'),
    path('fee_structure/<int:pk>/edit/', views.edit_fee_structure, name='edit_fee_structure'),
    path('fee_structure/<int:pk>/delete/', views.delete_fee_structure, name='delete_fee_structure'),

    # Location
    path('manage-location/', views.manage_location, name='manage_location'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)