from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from tutors.models import TutorAvailability, TutorTeaching, TutorRequest, TutorReview, TutorProfile
from students.models import StudentProfile
from .forms import RegisterForm
from django.views.decorators.http import require_GET
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.template.loader import render_to_string
from django.db.models import Avg, Count, FloatField, OuterRef, Prefetch, Q, Exists, Value
from django.db.models.functions import Coalesce
import math
from datetime import time
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from core.models import GradeSubject, Location, Grade

# Create your views here.
def homePage(request, section=None):
    tutors = TutorTeaching.objects.none()

    # Check if user is a logged-in student
    student_profile = None
    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        student_profile = request.user.student_profile

    if request.GET.get('search'):
        # Get search criteria
        grade_id = request.GET.get('grade')
        subject_id = request.GET.get('subject')
        budget = request.GET.get('budget')
        fee_type = request.GET.get('fee_type')
        rating = request.GET.get('rating')

        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')

        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')

        # Optional: Fallback to logged-in student's saved location if coordinates aren't in GET
        if not latitude and not longitude and student_profile and getattr(student_profile, 'location', None):
            if student_profile.location.latitude and student_profile.location.longitude:
                latitude = str(student_profile.location.latitude)
                longitude = str(student_profile.location.longitude)

        has_criteria = any([
            grade_id,
            subject_id,
            budget,
            fee_type,
            rating,
            latitude,
            longitude,
            start_time,
            end_time,
        ])

        if has_criteria:
             # 1. Subquery: check if at least 1 active daily time slot is NOT booked
            unbooked_active_slots = TutorAvailability.objects.filter(
                tutor_teaching=OuterRef('pk'),
                is_active=True
            ).exclude(
                booking_requests__status__in=['accepted', 'in_progress']
            )

            # 2. Subquery for Prefetch: fetch all unbooked active slots for display
            booked_requests = TutorRequest.objects.filter(
                availability=OuterRef('pk'),
                status__in=['accepted', 'in_progress']
            )
            free_availabilities_qs = (
                TutorAvailability.objects.filter(is_active=True)
                .annotate(is_booked=Exists(booked_requests))
                .filter(is_booked=False)
                .order_by('start_time')
            )

            # 3. Compulsory Base Query
            tutors = (
                TutorTeaching.objects.annotate(
                    has_free_slot=Exists(unbooked_active_slots),
                    avg_rating=Coalesce(
                        Avg('reviews__rating'),
                        Value(0.0),
                        output_field=FloatField()
                    ),
                    total_reviews=Count('reviews', distinct=True),
                )
                .filter(
                    # Compulsory Profile Info
                    tutor__verification_status=TutorProfile.VerificationStatus.VERIFIED,
                    tutor__profile_completed=True,
                    tutor__full_name__isnull=False,
                    tutor__location__isnull=False,
                    tutor__location__latitude__isnull=False,
                    tutor__location__longitude__isnull=False,
                    # Compulsory Grade-Subject & Teaching Active
                    is_active=True,
                    grade_subject__isnull=False,
                    # Compulsory Fee & Fee Type
                    fee__isnull=False,
                    fee__gt=0,
                    fee_type__in=['hour', 'day', 'month'],
                    # Compulsory Free Daily Time Slot
                    has_free_slot=True,
                )
                .exclude(tutor__full_name='')
                .select_related(
                    'tutor',
                    'tutor__location',
                    'grade_subject',
                    'grade_subject__grade',
                    'grade_subject__subject',
                )
                .prefetch_related(
                    Prefetch(
                        'availabilities',
                        queryset=free_availabilities_qs,
                        to_attr='free_slots'
                    )
                )
            )

            # 1. Grade & Subject filters
            if grade_id:
                tutors = tutors.filter(grade_subject__grade_id=grade_id)

            if subject_id:
                tutors = tutors.filter(grade_subject__subject_id=subject_id)

            # 2. Budget & Fee Type filter
            if fee_type in ['hour', 'day', 'month']:
                tutors = tutors.filter(fee_type=fee_type)

            if budget:
                try:
                    budget_val = Decimal(budget)
                    tutors = tutors.filter(fee__lte=budget_val)
                except (InvalidOperation, ValueError):
                    tutors = TutorTeaching.objects.none()

            # 3. Daily Time Slot filter 
            if start_time or end_time:
                try:
                    parsed_start = time.fromisoformat(start_time) if start_time else None
                    parsed_end = time.fromisoformat(end_time) if end_time else None

                    if parsed_start and parsed_end and parsed_end <= parsed_start:
                        return JsonResponse(
                            {'error': 'End time must be later than start time.'},
                            status=400
                        )

                    if parsed_start:
                        tutors = tutors.filter(availabilities__start_time__lte=parsed_start)
                    if parsed_end:
                        tutors = tutors.filter(availabilities__end_time__gte=parsed_end)

                except ValueError:
                    return JsonResponse(
                        {'error': 'Please provide valid availability times.'},
                        status=400
                    )

            # 4. Rating filter
            if rating:
                try:
                    tutors = tutors.filter(avg_rating__gte=float(rating))
                except (ValueError, TypeError):
                    tutors = TutorTeaching.objects.none()

            tutors = tutors.distinct()

            # 5. Location filter - 5 km radius (sorted by nearest distance)
            if latitude or longitude:
                try:
                    if not latitude or not longitude:
                        raise ValueError

                    lat = float(latitude)
                    lng = float(longitude)

                    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                        raise ValueError

                except (TypeError, ValueError):
                    return JsonResponse(
                        {'error': 'Please select a valid location on the map.'},
                        status=400
                    )

                radius = 5.0  # km
                lat_range = radius / 110.574
                lng_range = radius / (111.320 * math.cos(math.radians(lat)))

                nearby_candidates = tutors.filter(
                    tutor__location__latitude__isnull=False,
                    tutor__location__longitude__isnull=False,
                    tutor__location__latitude__range=(lat - lat_range, lat + lat_range),
                    tutor__location__longitude__range=(lng - lng_range, lng + lng_range),
                )

                nearby_results = []
                lat1 = math.radians(lat)
                lng1 = math.radians(lng)

                for teaching in nearby_candidates:
                    tutor_lat = float(teaching.tutor.location.latitude)
                    tutor_lng = float(teaching.tutor.location.longitude)

                    lat2 = math.radians(tutor_lat)
                    lng2 = math.radians(tutor_lng)

                    dlat = lat2 - lat1
                    dlng = lng2 - lng1

                    a = (
                        math.sin(dlat / 2) ** 2
                        + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
                    )
                    distance = 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

                    if distance <= radius:
                        teaching.distance_km = round(distance, 2)
                        nearby_results.append(teaching)

                # Sort nearest tutors first
                nearby_results.sort(key=lambda item: item.distance_km)
                tutors = nearby_results

    grade_subjects = GradeSubject.objects.select_related('grade', 'subject').order_by(
        'grade__id', 'subject__name'
    )

    # Safe check for logged-in student vs. guest visitor on index page
    if student_profile and getattr(student_profile, 'grade_id', None):
        my_subjects = grade_subjects.filter(grade_id=student_profile.grade_id)
    else:
        my_subjects = GradeSubject.objects.none()

    context = {
        'grades': Grade.objects.all().order_by('id'),
        'grade_subjects': grade_subjects,
        'my_subjects': my_subjects,
        'tutors': tutors,
        'searched': bool(request.GET.get('search')),
        'selected_grade': request.GET.get('grade', ''),
        'selected_subject': request.GET.get('subject', ''),
        'selected_budget': request.GET.get('budget', ''),
        'selected_fee_type': request.GET.get('fee_type', ''),
        'selected_rating': request.GET.get('rating', ''),
        'selected_start_time': request.GET.get('start_time', ''),
        'selected_end_time': request.GET.get('end_time', ''),
        'section': section
    }
  
    # AJAX request: return only tutor results

    # AJAX request: return only tutor results
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tutor_data = []

        for tutor in tutors:
            # Build list of open daily time slots (uses prefetched `free_slots` if available)
            slots_qs = getattr(
                tutor,
                'free_slots',
                tutor.availabilities.filter(is_active=True)
            )
            free_slots = [
                {
                    'id': slot.id,
                    'start_time': slot.start_time.strftime('%I:%M %p'),
                    'end_time': slot.end_time.strftime('%I:%M %p'),
                }
                for slot in slots_qs
            ]

            tutor_data.append ({
                'id': tutor.id,
                'name': tutor.tutor.full_name,
                'profile_picture': (
                    tutor.tutor.profile_picture.url
                    if tutor.tutor.profile_picture
                    else ''
                ),
                'status': (
                    True if tutor.tutor.verification_status in [1,4]
                    else False
                    ),
                'experience': str(tutor.tutor.experience or 0),
                'grade': str(tutor.grade_subject.grade),
                'subject': str(tutor.grade_subject.subject),
                'fee': str(tutor.fee),
                'fee_type': tutor.get_fee_type_display(),
                'location': (
                    tutor.tutor.location.address
                    if tutor.tutor.location
                    else ''
                ),
                'distance_km': getattr(tutor, 'distance_km', None),
                'free_slots': free_slots,
                'total_reviews': tutor.total_reviews,
                'rating': (
                    round(tutor.avg_rating, 1)
                    if tutor.avg_rating
                    else 'No ratings'
                ),
            })

        return JsonResponse({
            'tutors': tutor_data
        })

    return render(request, 'index.html', context)


def register(request):
    if request.method == 'POST':
        agree=request.POST.get('terms_agree')
        if agree=="1":
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()          
                if user.role == 'student':
                    StudentProfile.objects.create(
                        user=user
                    )
                    login(request, user)
                    return redirect('student_dashboard')
            
                elif user.role == 'tutor':
                    TutorProfile.objects.create(
                        user=user
                    )
                    login(request, user)
                    return redirect('tutor_dashboard')
        else:
            return render(request, 'accounts/register.html',{
                'terms_condition_error':'Please agree the terms and conditions first.'
            })        

    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            if user.role == 'student':

                return redirect('student_dashboard')

            elif user.role == 'tutor':
                return redirect('tutor_dashboard')

            elif user.role == 'admin':
                return redirect('admin_dashboard')

        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid username or password.'
            })

    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    return redirect('home-page')

def password_forgot(request):
    return render(request, 'accounts/forgot_password.html')
# @login_required
# def student_dashboard(request):
#     return render(request, 'accounts/student_dashboard.html')
@login_required
def tutor_dashboard(request):
    return render(request, 'accounts/tutor_dashboard.html')