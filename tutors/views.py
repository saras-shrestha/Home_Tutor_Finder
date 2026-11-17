from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from core.models import Grade, Subject, GradeSubject, Location, Region
from .models import Qualification, TutorTeaching, TutorAvailability, TutorRequest
from django.http import JsonResponse
from django.utils import timezone 
from .forms import TutorAvailabilityForm 
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

# Create your views here.

@login_required
def tutor_dashboard(request):
    if request.user.role != "tutor":
        return redirect("home")

    else:
        profile = request.user.tutor_profile

        if not profile.profile_completed:
            return render(
                request,
                "tutors/tutor_dashboard.html",
                {
                    "profile_incomplete": True,
                    "profile": profile
                }
            )
        
        else:

            return render(
                request,
                "tutors/tutor_dashboard.html",
                {
                    "profile_incomplete": False,
                    "profile": profile
                }
            )

@login_required
def tutor_profile(request):
    tutor = request.user.tutor_profile
    if request.method=="POST":
        section = request.POST.get("section")
        # Step 1: Personal Information
        if section == "personal":
            tutor.full_name = request.POST.get('full_name')
            tutor.gender = request.POST.get('gender')
            tutor.phone = request.POST.get('phone') 
            if "profile_picture" in request.FILES:
                tutor.profile_picture = request.FILES["profile_picture"]
            if tutor.current_step<2:                
                tutor.current_step = 2
            tutor.save()
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
            if tutor.location:

                location = tutor.location

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

                tutor.location = location
            if tutor.current_step<3: 
                tutor.current_step = 3
            tutor.save()

            return JsonResponse({
                "success": True,
                "message": "Location saved successfully.",
                "next_step": 3
            })
        # Step 3: About
        elif section == "about": 
            tutor.description = request.POST.get("description")

            if tutor.current_step<4: 
                tutor.current_step = 4           
            tutor.save()

            return JsonResponse({
                "success": True,
                "next_step": 4
            })
        
        # Step 4: Qualification
        elif section == "qualification":

            qualification, created = Qualification.objects.get_or_create(
                tutor=tutor
            )

            qualification.highest_qualification = request.POST.get(
                "high_qualification"
            )

            qualification.study_field = request.POST.get(
                "study_field"
            )

            qualification.degree_name = request.POST.get(
                "degree_name"
            )

            qualification.college = request.POST.get(
                "college_name"
            )

            qualification.university = request.POST.get(
                "university"
            )

            qualification.country = request.POST.get(
                "study_country"
            )

            gpa = request.POST.get("tutor_gpa")

            qualification.gpa = gpa if gpa else None

            qualification.save()

            if tutor.current_step<5: 
                tutor.current_step = 5
            tutor.save()

            return JsonResponse({
                "success": True,
                "message": "Qualification saved successfully.",
                "next_step": 5
            })
        # Step 5: Certificationel
        if section == "certification":
            if "certificate" in request.FILES:
                tutor.certificate = request.FILES["certificate"]
            if tutor.current_step<6: 
                tutor.current_step = 6
            tutor.save()

            return JsonResponse({
                "success": True,
                "next_step": 6
            })
        
        # STEP 6 - CV and FINAL
        elif section == "cv":

            cv = request.FILES.get("cv")

            if not cv:
                return JsonResponse({
                    "success": False,
                    "message": "Please upload your CV."
                })

            tutor.cv = cv
            tutor.profile_completed = True
            tutor.profile_completed_at= timezone.now()
            tutor.current_step = 7
            tutor.save()

            return JsonResponse({
                "success": True,
                "completed": True,
                "redirect_url": reverse("tutor_dashboard")
            })

    regions=Region.objects.all();
    return render(
        request,
        "tutors/profile.html",
        {
            "tutor": tutor,
            "regions": regions,
            "current_step": tutor.current_step
        }
    )

@login_required
def tutor_availability(request):
    tutor = request.user.tutor_profile

    if request.method == 'POST':
        form = TutorAvailabilityForm(request.POST)

        if form.is_valid():
            slot = form.save(commit=False)
            slot.tutor = tutor
            slot.full_clean()
            slot.save()

            messages.success(request, 'Availability saved successfully.')
            return redirect('tutor_availability')
    else:
        form = TutorAvailabilityForm()

    availabilities = TutorAvailability.objects.filter(
        tutor=tutor
    ).order_by('day', 'start_time')

    return render(request, 'tutors/availability/availability.html', {
        'form': form,
        'availabilities': availabilities,
    })


@login_required
def edit_availability(request, pk):
    tutor = request.user.tutor_profile

    slot = get_object_or_404(
        TutorAvailability, pk=pk, tutor=tutor
    )

    if request.method == 'POST':
        form = TutorAvailabilityForm(request.POST, instance=slot)

        if form.is_valid():
            updated_slot = form.save(commit=False)
            updated_slot.tutor = tutor
            updated_slot.full_clean()
            updated_slot.save()

            messages.success(request, 'Availability updated.')
            return redirect('tutor_availability')
    else:
        form = TutorAvailabilityForm(instance=slot)

    return render(request, 'tutors/availability/edit_availability.html', {
        'form': form,
        'slot': slot,
    })


@login_required
def delete_availability(request, pk):
    tutor = request.user.tutor_profile

    slot = get_object_or_404(
        TutorAvailability, pk=pk, tutor=tutor
    )

    if request.method == 'POST':
        slot.delete()
        messages.success(request, 'Availability deleted.')

    return redirect('tutor_availability')

# Manage Location
def manage_location(request):
    tutor = request.user.tutor_profile
    
    if request.method=="POST":
        region_id = request.POST.get("region")
        district_id = request.POST.get("district")
        city_id = request.POST.get("city")
        address = request.POST.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")     

        # If location already exists, update it
        if tutor.location:

            location = tutor.location

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

            tutor.location = location
        tutor.save()
        return redirect('tutor_dashboard')

    regions=Region.objects.all();
    return render(
        request,
        "tutors/location/location.html",
        {
            "tutor": tutor,
            "regions": regions
        }
    )

def teaching_fees(request):
    grades = Grade.objects.all()
    tutor = request.user.tutor_profile

    if request.method == "POST":
        grade=request.POST.get("grade")
        subject=request.POST.get("subject")
        fee = request.POST.get("fee")
        fee_type = request.POST.get("feeType")

        if grade and subject and fee and fee_type:
            grade_subject = get_object_or_404(
                GradeSubject,
                grade_id=grade,
                subject_id=subject
            )

            TutorTeaching.objects.update_or_create(
                tutor=tutor,
                grade_subject=grade_subject,
                defaults={
                    'fee': fee,
                    'fee_type': fee_type,
                }
            )

            return redirect('teaching_fees')

    fee_structures = TutorTeaching.objects.filter(tutor=tutor)

    return render(request, "tutors/fees/teaching_fees.html", {
        'grades': grades,
        'fee_types': TutorTeaching.FeeType.choices,
        'fee_structures': fee_structures,
    })

# Json for respective subjects of selected grade
def get_subjects(request, grade_id):
    subjects = GradeSubject.objects.filter(
            grade_id=grade_id
        ).select_related('subject').order_by('subject__name')

    subject_data = [
        {
            'id': subject.subject.id,
            'name': subject.subject.name
        }
        for subject in subjects
    ]
    return JsonResponse(subject_data, safe=False)

@login_required
def edit_fee_structure(request, pk):
    tutor = request.user.tutor_profile

    fee_structure = get_object_or_404(
        TutorTeaching, pk=pk, tutor=tutor
    )

    if request.method == "POST":
        fee = request.POST.get('fee')
        fee_type = request.POST.get('feeType')

        if fee and fee_type:
            fee_structure.fee = fee
            fee_structure.fee_type = fee_type
            fee_structure.save()

            return redirect('teaching_fees')
        
    return render(request, 'tutors/fees/edit_fee_structure.html', {
        # 'form': form,
        'fee_structure': fee_structure,
        'fee_types': TutorTeaching.FeeType.choices
    })


@login_required
def delete_fee_structure(request, pk):
    tutor = request.user.tutor_profile

    fee_structure = get_object_or_404(
        TutorTeaching, pk=pk, tutor=tutor
    )

    if request.method == 'POST':
        fee_structure.delete()
        messages.success(request, 'Fee structure deleted.')

    return redirect('teaching_fees')

@login_required
def pending_student_request(request):
    tutor = request.user.tutor_profile
    pending_requests = TutorRequest.objects.filter(
        tutor_teaching__tutor=tutor,
        status='pending'
    ).select_related(
        'student',
        'student__user',
        'tutor_teaching__grade_subject__grade',
        'tutor_teaching__grade_subject__subject'
    )
    paginator = Paginator(pending_requests, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
        
    context={
        "pending_requests":page_obj,
    }    
    return render(request, 'tutors/teaching_management/pending-request.html', context)

@login_required
def respond_student_request(request, request_id):

    if request.method == 'POST':

        tutor = request.user.tutor_profile

        tutor_request = get_object_or_404(
            TutorRequest,
            id=request_id,
            tutor_teaching__tutor=tutor,
            status='pending'
        )

        status = request.POST.get('status')

        if status not in ['accepted', 'rejected']:
            messages.error(request, "Invalid action.")
            return redirect('pending_request')

        tutor_request.status = status
        tutor_request.responded_at = timezone.now()
        tutor_request.save()

        messages.success(request, f"Request {status} successfully.")

    return redirect('pending_request')
    
# @login_required
# def accepted_student_request(request):
#     tutor = request.user.tutor_profile

#     accepted_requests = TutorRequest.objects.filter(
#         tutor_teaching__tutor=tutor,
#         status='accepted'
#     ).select_related(
#         'student',
#         'tutor_teaching__grade_subject__grade',
#         'tutor_teaching__grade_subject__subject'
#     )

#     paginator = Paginator(accepted_requests, 5)
#     page_obj = paginator.get_page(request.GET.get('page'))

#     context = {
#         'accepted_requests': page_obj
#     }

#     return render(
#         request,
#         'tutors/teaching_management/accepted-request.html',
#         context
#     )


# @login_required
# def accepted_student_request(request):

#     tutor = request.user.tutor_profile

#     # Accepted requests - teaching not started
#     accepted_students = TutorRequest.objects.filter(
#         tutor_teaching__tutor=tutor,
#         status='accepted'
#     ).select_related(
#         'student',
#         'student__user',
#         'tutor_teaching',
#         'tutor_teaching__grade_subject',
#         'tutor_teaching__grade_subject__grade',
#         'tutor_teaching__grade_subject__subject'
#     ).order_by('-responded_at')

#     # Students whose teaching has started
#     started_students = TutorRequest.objects.filter(
#         tutor_teaching__tutor=tutor,
#         status='in_progress'
#     ).select_related(
#         'student',
#         'student__user',
#         'tutor_teaching',
#         'tutor_teaching__grade_subject',
#         'tutor_teaching__grade_subject__grade',
#         'tutor_teaching__grade_subject__subject'
#     ).order_by('-teaching_started_at')

#     # Search by student name
#     search = request.GET.get('search', '').strip()

#     if search:
#         name_filter = (
#             Q(student__user__first_name__icontains=search) |
#             Q(student__user__last_name__icontains=search) |
#             Q(student__user__username__icontains=search)
#         )

#         accepted_students = accepted_students.filter(name_filter)
#         started_students = started_students.filter(name_filter)

#     # Filter by grade
#     grade_id = request.GET.get('grade')

#     if grade_id:
#         accepted_students = accepted_students.filter(
#             tutor_teaching__grade_subject__grade_id=grade_id
#         )

#         started_students = started_students.filter(
#             tutor_teaching__grade_subject__grade_id=grade_id
#         )

#     context = {
#         'accepted_students': accepted_students,
#         'started_students': started_students,
#         'grades': Grade.objects.all(),
#     }

#     return render(
#             request,
#             'tutors/teaching_management/accepted-request.html',
#             context
#         )


@login_required
def accepted_student_request(request):

    tutor = request.user.tutor_profile

    # Not Started students
    accepted_students = TutorRequest.objects.filter(
        tutor_teaching__tutor=tutor,
        status='accepted'
    ).select_related(
        'student',
        'student__user',
        'tutor_teaching',
        'tutor_teaching__grade_subject',
        'tutor_teaching__grade_subject__grade',
        'tutor_teaching__grade_subject__subject'
    ).order_by('-responded_at')

    # In Progress students
    started_students = TutorRequest.objects.filter(
        tutor_teaching__tutor=tutor,
        status='in_progress'
    ).select_related(
        'student',
        'student__user',
        'tutor_teaching',
        'tutor_teaching__grade_subject',
        'tutor_teaching__grade_subject__grade',
        'tutor_teaching__grade_subject__subject'
    ).order_by('-teaching_started_at')

    # Search
    search = request.GET.get('search', '').strip()

    if search:
        name_filter = (
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search) |
            Q(student__user__username__icontains=search)
        )

        accepted_students = accepted_students.filter(name_filter)
        started_students = started_students.filter(name_filter)

    # Grade filter
    grade_id = request.GET.get('grade')

    if grade_id:
        accepted_students = accepted_students.filter(
            tutor_teaching__grade_subject__grade_id=grade_id
        )

        started_students = started_students.filter(
            tutor_teaching__grade_subject__grade_id=grade_id
        )

    # Context
    context = {
        'accepted_students': accepted_students,
        'started_students': started_students,
        'grades': Grade.objects.all(),
    }

    # AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        tab = request.GET.get('tab')

        if tab == 'not_started':

            html = render_to_string(
                'tutors/teaching_management/_not_started_table.html',
                context,
                request=request
            )

        elif tab == 'in_progress':

            html = render_to_string(
                'tutors/teaching_management/_in_progress_table.html',
                context,
                request=request
            )

        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid tab requested.'
            }, status=400)

        return JsonResponse({
            'success': True,
            'html': html,
            'not_started_count': accepted_students.count(),
            'in_progress_count': started_students.count()
        })

    # Normal page request
    return render(
        request,
        'tutors/teaching_management/accepted-request.html',
        context
    )

@login_required
def rejected_student_request(request):
    tutor = request.user.tutor_profile

    rejected_requests = TutorRequest.objects.filter(
        tutor_teaching__tutor=tutor,
        status='rejected'
    ).select_related(
        'student',
        'tutor_teaching__grade_subject__grade',
        'tutor_teaching__grade_subject__subject'
    )

    paginator = Paginator(rejected_requests, 5)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'rejected_requests': page_obj
    }

    return render(
        request,
        'tutors/teaching_management/rejected-request.html',
        context
    )


@login_required
def my_students(request):

    tutor = request.user.tutor_profile

    # Get accepted requests belonging to this tutor
    students = TutorRequest.objects.filter(
        tutor_teaching__tutor=tutor,
        status='in_progress'
    ).select_related(
        'student',
        'student__user',
        'tutor_teaching',
        'tutor_teaching__grade_subject',
        'tutor_teaching__grade_subject__grade',
        'tutor_teaching__grade_subject__subject'
    ).order_by('-teaching_started_at')

    # Search by student name
    search = request.GET.get('search', '').strip()

    if search:
        students = students.filter(
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search) |
            Q(student__user__username__icontains=search)
        )

    # Filter by grade
    grade_id = request.GET.get('grade')

    if grade_id:
        students = students.filter(
            tutor_teaching__grade_subject__grade_id=grade_id
        )

    context = {
        'students': students,
        'grades': Grade.objects.all(),
    }
    return render(request, 'tutors/teaching_management/my-students.html', context)
    

@login_required
def completed_sessions(request):

    tutor = request.user.tutor_profile

    # Get completed requests belonging to this tutor
    sessions = TutorRequest.objects.filter(
        tutor_teaching__tutor=tutor,
        status='completed'
    ).select_related(
        'student',
        'student__user',
        'tutor_teaching',
        'tutor_teaching__grade_subject',
        'tutor_teaching__grade_subject__grade',
        'tutor_teaching__grade_subject__subject'
    ).order_by('-updated_at')

    # Search by student name
    search = request.GET.get('search', '').strip()

    if search:
        sessions = sessions.filter(
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search) |
            Q(student__user__username__icontains=search)
        )

    # Filter by subject
    subject_id = request.GET.get('subject')

    if subject_id:
        sessions = sessions.filter(
            tutor_teaching__grade_subject__subject_id=subject_id
        )

    # Filter by completion date
    completed_date = request.GET.get('date')

    if completed_date:
        sessions = sessions.filter(
            updated_at__date=completed_date
        )

    context = {
        'sessions': sessions,
        'subjects': Subject.objects.all(),
    }

    return render(
        request,
        'tutors/teaching_management/completed_sessions.html',
        context
    )

@login_required
def student_details(request, req_id):
    

    student_request = get_object_or_404(
        TutorRequest.objects.select_related(
            'student',
            'student__user',
            'tutor_teaching',
            'tutor_teaching__grade_subject',
            'tutor_teaching__grade_subject__grade',
            'tutor_teaching__grade_subject__subject'
        ),
        id=req_id,
        tutor_teaching__tutor=request.user.tutor_profile,
        status='in_progress'
    )

    context = {
        'student_request': student_request,
    }

    return render(
        request,
        'tutors/teaching_management/student-details.html',
        context
    )

@login_required
@require_POST
def start_teaching(request, start_request_id):

    tutor = request.user.tutor_profile

    student_request = get_object_or_404(
        TutorRequest,
        id=start_request_id,
        tutor_teaching__tutor=tutor,
        status='accepted'
    )

    student_request.status = 'in_progress'
    student_request.teaching_started_at = timezone.now()
    student_request.save()

    return JsonResponse({
        'success': True,
        'message': 'Teaching started successfully!'
    })