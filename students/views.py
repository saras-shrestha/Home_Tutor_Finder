from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from tutors.models import TutorAvailability, TutorTeaching, TutorRequest, TutorReview, TutorProfile
from .models import StudentProfile
from django.urls import reverse
from core.models import GradeSubject, Region, District, City, Location, Grade
from django.http import JsonResponse
from django.utils import timezone
import requests
from django.views.decorators.http import require_GET
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.template.loader import render_to_string
import math
from datetime import time
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from django.db.models import Avg, Count, FloatField, OuterRef, Prefetch, Q, Exists, Value
from django.db.models.functions import Coalesce


# Create your views here.

@login_required
def student_dashboard(request):
    if request.user.role != "student":
        return redirect("home-page")

    profile = request.user.student_profile

    if not profile.profile_completed:
        return render(
            request,
            "students/student_dashboard.html",
            {
                "profile_incomplete": True,
                "profile": profile
            }
        )

    return render(
        request,
        "students/student_dashboard.html",
        {
            "profile_incomplete": False,
            "profile": profile
        }
    )


@login_required
def student_profile(request):
    student = request.user.student_profile
    if request.method=="POST":
        section = request.POST.get("section")
        # Step 1: Personal Information
        if section == "personal":
            student.full_name = request.POST.get('full_name')
            student.gender = request.POST.get('gender')
            student.phone = request.POST.get('phone')
            student.date_of_birth = request.POST.get('dob') 
            if "profile_picture" in request.FILES:
                student.profile_picture = request.FILES["profile_picture"]
            if student.current_step<2:                
                student.current_step = 2
            student.save()
            return JsonResponse({
                "success": True,
                "next_step": 2,
            })
        
        # Step 2: Location
        elif section == "location":

            region_id = request.POST.get("region")
            district_id = request.POST.get("district")
            city_id = request.POST.get("city")
            address = request.POST.get("address")
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")            

            # Basic validation
            if not region_id or not district_id or not city_id:
                return JsonResponse({
                    "success": False,
                    "message": "Please select region, district and city."
                })

            if not address:
                return JsonResponse({
                    "success": False,
                    "message": "Please enter your address."
                })

            # If location already exists, update it
            if student.location:

                location = student.location

                location.region_id = region_id
                location.district_id = district_id
                location.city_id = city_id
                location.address = address
                location.latitude = latitude or None
                location.longitude = longitude or None

                location.save()

            # Otherwise create a new location
            else:
                location = Location.objects.create(
                    region_id=region_id,
                    district_id=district_id,
                    city_id=city_id,
                    address=address,
                    latitude=latitude or None,
                    longitude=longitude or None
                )

                student.location = location
            if student.current_step<3: 
                student.current_step = 3
            student.save()

            return JsonResponse({
                "success": True,
                "message": "Location saved successfully.",
                "next_step": 3
            })
        # Step 3: About
        elif section == "about": 
            student.description = request.POST.get("description")

            if student.current_step<4: 
                student.current_step = 4           
            student.save()

            return JsonResponse({
                "success": True,
                "next_step": 4
            })
        
        # Step 4: Academic Information and Final
        elif section == "academic":
            student.education_level = request.POST.get('education_level')
            student.grade = Grade.objects.get(id=request.POST.get('grade'))
            student.school_college = request.POST.get('school_college')
            student.profile_completed = True
            student.profile_completed_at= timezone.now() 
            student.current_step = 5           
            student.save()
            return JsonResponse({
                "success": True,
                "message": "Academic Information saved successfully.",
                "redirect_url": reverse("student_dashboard")        
            })
        
    regions=Region.objects.all();
    grades=Grade.objects.all();
    return render(
        request,
        "students/profile.html",
        {
            "student": student,
            "regions": regions,
            "current_step": student.current_step,
            "grades": grades
        }
    )

# Json for respective district of selected region
def get_districts(request, region_id):
    districts = District.objects.filter(region=region_id)

    district_data = [
        {
            'id': district.id,
            'name': district.name
        }
        for district in districts
    ]
    return JsonResponse(district_data, safe=False)


# Json for respective city of selected district
def get_cities(request, district_id):
    cities = City.objects.filter(district=district_id)

    city_data = [
        {
            'id': city.id,
            'name': city.name
        }
        for city in cities
    ]

    return JsonResponse(city_data, safe=False)

# find tutors

def find_tutors(request):
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
    return render(
        request,
        'students/tutor-management/find-tutors.html',
        context
    )
  

@require_GET
def address_autocomplete(request):

    query = request.GET.get('q', '').strip()

    if len(query) < 3:
        return JsonResponse({'results': []})

    try:
        response = requests.get(
            'https://photon.komoot.io/api/',
            params={
                'q': query,
                'limit': 5,
                'lat': 27.7172,
                'lon': 85.3240,
            }, 
            headers={
                'User-Agent': 'HomeTutorFinder/1.0'
            },
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        results = []

        for feature in data.get('features', []):

            properties = feature.get('properties', {})
            coordinates = feature.get('geometry', {}).get(
                'coordinates', []
            )

            if len(coordinates) != 2:
                continue

            name_parts = [
                properties.get('name'),
                properties.get('street'),
                properties.get('district'),
                properties.get('city'),
                properties.get('state'),
                properties.get('country'),
            ]

            address = ', '.join(
                dict.fromkeys(
                    part for part in name_parts if part
                )
            )

            results.append({
                'name': address,
                'latitude': coordinates[1],
                'longitude': coordinates[0],
            })

        return JsonResponse({'results': results})

    except requests.RequestException:
        return JsonResponse(
            {'error': 'Address search is temporarily unavailable.'},
            status=503
        )


@login_required
def save_location(request):

    if request.method == 'POST':

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        address = request.POST.get('address')

        try:
            latitude = Decimal(latitude)
            longitude = Decimal(longitude)

            if not (-90 <= latitude <= 90):
                raise ValueError("Invalid latitude")

            if not (-180 <= longitude <= 180):
                raise ValueError("Invalid longitude")

        except (TypeError, ValueError, InvalidOperation):
            messages.error(request, "Please select a valid location.")
            return redirect('select_location')

        student = request.user.student_profile

        student.latitude = latitude
        student.longitude = longitude
        student.address = address

        student.save()

        messages.success(request, "Location saved successfully!")

        return redirect('student_dashboard')

    return redirect('select_location')


@login_required
@require_POST
def send_tutor_request(request):

    if request.user.role != "student":
        return redirect("home-page")

    student = request.user.student_profile

    tutor_teaching_id = request.POST.get('tutor_teaching_id')
    message = request.POST.get('message', '').strip()

    if not tutor_teaching_id:
        messages.error(request, "Please select a valid tutor.")
        return redirect("find_tutors")

    tutor_teaching = get_object_or_404(
        TutorTeaching,
        id=tutor_teaching_id,
        is_active=True,
        tutor__verification_status=1,
        tutor__profile_completed=True
    )

    if tutor_teaching.tutor.user_id == request.user.id:
        messages.error(request, "You cannot send a request to yourself.")
        return redirect("find_tutors")

    existing_request = TutorRequest.objects.filter(
        student=student,
        tutor_teaching=tutor_teaching,
        status__in=['pending', 'accepted','in_progress']
    ).exists()

    if existing_request:
        messages.warning(
            request,
            "You already have an active request or ongoing class with this tutor."
        )
        return redirect("tutor_requests")

    try:
        TutorRequest.objects.create(
            student=student,
            tutor_teaching=tutor_teaching,
            message=message
        )
        messages.success(request, "Tutor request sent successfully!")
    except IntegrityError:
        # Protects against rapid double-clicks on the submit button
        messages.warning(
            request,
            "You already have an active request with this tutor."
        )

    return redirect("tutor_requests")



# @login_required
# def tutor_requests(request):

#     if request.user.role != "student":
#         return redirect("home-page")

#     student = request.user.student_profile

#     tutor_requests = TutorRequest.objects.filter(
#         student=student
#     ).select_related(
#         'tutor_teaching',
#         'tutor_teaching__tutor',
#         'tutor_teaching__grade_subject',
#         'tutor_teaching__grade_subject__grade',
#         'tutor_teaching__grade_subject__subject'
#     ).order_by('-created_at')

#     return render(
#         request,
#         'students/tutor-management/tutor-requests.html',
#         {
#             'tutor_requests': tutor_requests
#         }
#     )
@login_required
def tutor_requests(request):
    if request.user.role != "student":
        return redirect("home-page")

    student = request.user.student_profile
    base_related = (
        'tutor_teaching',
        'tutor_teaching__tutor',
        'tutor_teaching__grade_subject',
        'tutor_teaching__grade_subject__grade',
        'tutor_teaching__grade_subject__subject',
    )
    if request.method == "POST":
        student = request.user.student_profile
        tutor_request_id = request.POST.get('completed_request_id')
        comment = request.POST.get('review_msg', '').strip()
        tutor_rating = request.POST.get('rating')
        if not tutor_request_id:
            messages.error(request, "Please select a valid tutor request.")
            return redirect("tutor_requests")
        # Validate rating is between 1 and 5
        try:
            rating = Decimal(tutor_rating)
            if not (Decimal('1') <= rating <= Decimal('5')):
                raise ValueError
        except (TypeError, InvalidOperation, ValueError):
            messages.error(request, "Please select a star rating between 1 and 5.")
            return redirect("tutor_requests")

        qs = TutorRequest.objects.select_related('tutor_teaching')
        tutor_request = get_object_or_404(
            qs,
            id=tutor_request_id,
            student=student,
            status='completed'
        )
        review, created = TutorReview.objects.get_or_create(
            student=student,
            tutor_teaching=tutor_request.tutor_teaching,
            defaults={
                'comment': comment,
                'rating': rating,
            },
            
        )

        if created:
            # Database was updated with a new review
            messages.success(request, "Your review has been submitted!")
        else:
            # Nothing was saved because a review already existed
            messages.warning(request, "You have already reviewed this class.")

        return redirect("tutor_requests")

    
    # 1. Querysets
    pending_requests = TutorRequest.objects.filter(
        student=student,
        status='pending'
    ).select_related(*base_related).order_by('-created_at')

    accepted_requests = TutorRequest.objects.filter(
        student=student,
        status='accepted'
    ).select_related(*base_related).order_by('-responded_at')

    started_requests = TutorRequest.objects.filter(
        student=student,
        status='in_progress'
    ).select_related(*base_related).order_by('-teaching_started_at')

    completed_requests = TutorRequest.objects.filter(
        student=student,
        status='completed'
    ).select_related(*base_related).order_by('-teaching_completed_at')

    # 2. Summary counts (before search)
    pending_count = pending_requests.count()
    not_started_count = accepted_requests.count()
    in_progress_count = started_requests.count()
    completed_count = completed_requests.count()

    # 3. Search filters
    subject_search = request.GET.get('subject_search', '').strip()
    tutor_search = request.GET.get('tutor_search', '').strip()

    # if subject_search:
    #     student_filter = Q(student__full_name__icontains=student_search)
    #     pending_requests = pending_requests.filter(student_filter)
    #     accepted_requests = accepted_requests.filter(student_filter)
    #     started_requests = started_requests.filter(student_filter)
    #     completed_requests = completed_requests.filter(student_filter)

    if tutor_search:
        tutor_filter = Q(tutor_teaching__tutor__full_name__icontains=tutor_search)
        pending_requests = pending_requests.filter(tutor_filter)
        accepted_requests = accepted_requests.filter(tutor_filter)
        started_requests = started_requests.filter(tutor_filter)
        completed_requests = completed_requests.filter(tutor_filter)

    # 4. Search badge counts (after search, before pagination)
    search_pending_count = pending_requests.count()
    search_not_started_count = accepted_requests.count()
    search_in_progress_count = started_requests.count()
    search_completed_count = completed_requests.count()

    # 5. Pagination
    pending_paginator = Paginator(pending_requests, 3)
    accepted_paginator = Paginator(accepted_requests, 3)
    started_paginator = Paginator(started_requests, 3)
    completed_paginator = Paginator(completed_requests, 3)  

    tab = request.GET.get('tab', 'pending')
    page_number = request.GET.get('page', 1)

    page_obj_pending = pending_paginator.get_page(page_number if tab == 'pending' else 1)
    page_obj_accepted = accepted_paginator.get_page(page_number if tab == 'not_started' else 1)
    page_obj_started = started_paginator.get_page(page_number if tab == 'in_progress' else 1)
    page_obj_completed = completed_paginator.get_page(page_number if tab == 'completed' else 1)

    # 6. Attach existing reviews to the 5 completed requests on the current page
    teaching_ids = [req.tutor_teaching_id for req in page_obj_completed]
    reviews_map = {
        r.tutor_teaching_id: r
        for r in TutorReview.objects.filter(student=student, tutor_teaching_id__in=teaching_ids)
    }
    for req in page_obj_completed:
        req.review = reviews_map.get(req.tutor_teaching_id)


    context = {
        'pending_requests': page_obj_pending,
        'accepted_requests': page_obj_accepted,
        'started_requests': page_obj_started,
        'completed_requests': page_obj_completed,

        'pending_count': pending_count,
        'not_started_count': not_started_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,

        'search_pending_count': search_pending_count,
        'search_not_started_count': search_not_started_count,
        'search_in_progress_count': search_in_progress_count,
        'search_completed_count': search_completed_count,
    }

    # 6. AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        tab_templates = {
            'pending': 'students/tutor-management/tutor-requests-partials/_pending_table.html',
            'not_started': 'students/tutor-management/tutor-requests-partials/_not_started_table.html',
            'in_progress': 'students/tutor-management/tutor-requests-partials/_in_progress_table.html',
            'completed': 'students/tutor-management/tutor-requests-partials/_completed_table.html',
        }

        template = tab_templates.get(tab)
        if not template:
            return JsonResponse({'success': False, 'message': 'Invalid tab requested.'}, status=400)

        html = render_to_string(template, context, request=request)

        return JsonResponse({
            'success': True,
            'html': html,
            'pending_count': pending_count,
            'not_started_count': not_started_count,
            'in_progress_count': in_progress_count,
            'completed_count': completed_count,
            'search_pending_count': search_pending_count,
            'search_not_started_count': search_not_started_count,
            'search_in_progress_count': search_in_progress_count,
            'search_completed_count': search_completed_count,
        })

    # Normal page request
    return render(request, 'students/tutor-management/tutor-requests.html', context)

def my_tutors(request):
    tutors = TutorProfile.objects.filter(verification_status=1).all()
    paginator = Paginator(tutors, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context={
            "tutors":page_obj,
        }
    return render(
        request,
        'students/my-learnings/my-tutors.html',
        context
    )


# my profile
# def my_student_profile(request):
#     student = request.user.student_profile
#     if request.method=="POST": 
#         # personal  
#         student.full_name = request.POST.get('full_name')
#         student.gender = request.POST.get('gender')
#         student.phone = request.POST.get('phone')
#         student.date_of_birth = request.POST.get('dob') 
#         if "profile_picture" in request.FILES:
#             student.profile_picture = request.FILES["profile_picture"]          
        
#         #  Location
#         region_id = request.POST.get("region")
#         district_id = request.POST.get("district")
#         city_id = request.POST.get("city")
#         address = request.POST.get("address")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")         

#         # If location already exists, update it
#         if student.location:
#             location = student.location
#             location.region_id = region_id
#             location.district_id = district_id
#             location.city_id = city_id
#             location.address = address
#             location.latitude = latitude or None
#             location.longitude = longitude or None
#             location.save()

#         # Otherwise create a new location
#         else:

#             location = Location.objects.create(
#                 region_id=region_id,
#                 district_id=district_id,
#                 city_id=city_id,
#                 address=address,
#                 latitude=latitude or None,
#                 longitude=longitude or None
#             )

#             student.location = location
        
#         # About        
#         student.description = request.POST.get("description") 

#         # Academic Information and Final        
#         student.education_level = request.POST.get('education_level')
#         student.grade = Grade.objects.get(id=request.POST.get('grade'))
#         student.school_college = request.POST.get('school_college')
#         student.profile_completed_at= timezone.now()           
#         student.save()

#         messages.success(request, "Profile updated successfully!")
#         return redirect('my_student_profile')
        
#     regions=Region.objects.all();
#     grades=Grade.objects.all();
#     return render(
#         request,
#         "students/my-profile/my-profile.html",
#         {
#             "student": student,
#             "regions": regions,
#             "grades": grades
#         }
#     )


from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

def my_student_profile(request):
    student = request.user.student_profile

    if request.method == "POST":
        # Collected all text/select fields
        data = {
            "full_name": request.POST.get("full_name", "").strip(),
            "gender": request.POST.get("gender", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "dob": request.POST.get("dob", "").strip(),
            "region": request.POST.get("region", "").strip(),
            "district": request.POST.get("district", "").strip(),
            "city": request.POST.get("city", "").strip(),
            "address": request.POST.get("address", "").strip(),
            "description": request.POST.get("description", "").strip(),
            "education_level": request.POST.get("education_level", "").strip(),
            "grade": request.POST.get("grade", "").strip(),
            "school_college": request.POST.get("school_college", "").strip(),
        }

        # Check if any required field is empty
        missing_fields = [
            field.replace("_", " ").title()
            for field, value in data.items()
            if not value
        ]

        # Also check profile picture if the student doesn't have one saved yet
        if not student.profile_picture and "profile_picture" not in request.FILES:
            missing_fields.append("Profile Picture")

        if missing_fields:
            messages.error(
                request,
                f"Please fill in all required fields: {', '.join(missing_fields)}."
            )
            return render(
                request,
                "students/my-profile/my-profile.html",
                {
                    "student": student,
                    "regions": Region.objects.all(),
                    "grades": Grade.objects.all(),
                }
            )

        # Safe Grade lookup
        grade_obj = Grade.objects.filter(id=data["grade"]).first()
        if not grade_obj:
            messages.error(request, "Please select a valid grade.")
            return render(
                request,
                "students/my-profile/my-profile.html",
                {
                    "student": student,
                    "regions": Region.objects.all(),
                    "grades": Grade.objects.all(),
                }
            )

        # Personal
        student.full_name = data["full_name"]
        student.gender = data["gender"]
        student.phone = data["phone"]
        student.date_of_birth = data["dob"]
        if "profile_picture" in request.FILES:
            student.profile_picture = request.FILES["profile_picture"]

        # Location
        latitude = request.POST.get("latitude") or None
        longitude = request.POST.get("longitude") or None

        if student.location:
            location = student.location
            location.region_id = data["region"]
            location.district_id = data["district"]
            location.city_id = data["city"]
            location.address = data["address"]
            location.latitude = latitude
            location.longitude = longitude
            location.save()
        else:
            location = Location.objects.create(
                region_id=data["region"],
                district_id=data["district"],
                city_id=data["city"],
                address=data["address"],
                latitude=latitude,
                longitude=longitude,
            )
            student.location = location

        # About & Academic
        student.description = data["description"]
        student.education_level = data["education_level"]
        student.grade = grade_obj
        student.school_college = data["school_college"]
        student.save()

        messages.success(request, "Profile updated successfully!")
        return redirect(request.path)

    return render(
        request,
        "students/my-profile/my-profile.html",
        {
            "student": student,
            "regions": Region.objects.all(),
            "grades": Grade.objects.all(),
        }
    )
