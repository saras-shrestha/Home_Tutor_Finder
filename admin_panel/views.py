from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from tutors.models import TutorProfile, TutorRequest
from students.models import StudentProfile
from .models import AdminProfile
from core.models import Grade, Subject, GradeSubject
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string

def is_admin(user):
    return user.is_authenticated and user.is_staff
    
admin_required = user_passes_test(
    is_admin,
    login_url='admin_login'
)
def admin_login(request):
    # Already logged-in admin
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            return render(
                request,
                'admin_panel/admin_login.html',
                {
                    'error': 'You do not have permission to access the admin panel.'
                }
            )

        return render(
            request,
            'admin_panel/admin_login.html',
            {
                'error': 'Invalid username or password.'
            }
        )
    return render(request, 'admin_panel/admin_login.html')

@admin_required
def admin_dashboard(request):

    pending_tutors=TutorProfile.objects.prefetch_related('qualifications')[:2]
    
    context={
        "pending_tutors":pending_tutors,
    }

    return render(
        request,
        'admin_panel/admin_dashboard.html',
        context
    )

@admin_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@admin_required
def students_list(request):
    students = StudentProfile.objects.all()

    # Search by student name
    search = request.GET.get('search', '').strip()
    
    if search:
        students = students.filter(
            Q(full_name__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    # Filter by grade
    grade_id = request.GET.get('grade')
    
    if grade_id:
        students = students.filter(
            grade=grade_id
        )

    paginator = Paginator(students, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context={
            "students":page_obj,
            'grades': Grade.objects.all(),
        }
    return render(
        request,
        'admin_panel/students/students-list.html',
        context
    )

def student_info(request, student_id):

    student = StudentProfile.objects.get(
            id=student_id          
        )

    context = {
        'student': student,
    }

    return render(
        request,
        'admin_panel/students/student-info.html',
        context
    )

@admin_required
def my_admin_profile(request):
    if hasattr(request.user, "admin_profile"):
        admin = request.user.admin_profile
    else:
        admin, created = AdminProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Collected all text/select fields
        data = {
            "full_name": request.POST.get("full_name", "").strip(),
            "gender": request.POST.get("gender", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
        }

        # Check if any required field is empty
        missing_fields = [
            field.replace("_", " ").title()
            for field, value in data.items()
            if not value
        ]

        # Also check profile picture if the student doesn't have one saved yet
        if not admin.profile_picture and "profile_picture" not in request.FILES:
            missing_fields.append("Profile Picture")        

        if missing_fields:
            messages.error(
                request,
                f"Please fill in all required fields: {', '.join(missing_fields)}."
            )
        
        if "profile_picture" in request.FILES:
            profile_picture = request.FILES["profile_picture"]

        admin_profile, created = AdminProfile.objects.update_or_create(
            user = request.user,
            defaults={
                'profile_picture': profile_picture,
                'full_name': data['full_name'],
                'gender': data['gender'],
                'phone': data['phone']
            }
        )
        messages.success(request, "Profile updated successfully!")
        return redirect(request.path)
    context={
        'admin':admin
    }
            
    return render(request, 'admin_panel/my-profile/my-profile.html', context)
        


@admin_required
def tutors_list(request):
    tutors = TutorProfile.objects.filter(verification_status=1).all()
    paginator = Paginator(tutors, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context={
            "tutors":page_obj,
        }
    return render(
        request,
        'admin_panel/tutors/tutors-list.html',
        context
    )

@admin_required
def tutors_approval(request):
    pending_tutors=TutorProfile.objects.filter(verification_status__in=[0, 2]).prefetch_related('qualifications')
    paginator = Paginator(pending_tutors, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context={
        "pending_tutors":page_obj,
    }    
    return render(
        request,
            'admin_panel/tutors/pending-tutors-approval.html',
            context
    )

@admin_required
def tutor_review(request, id):
    tutor=get_object_or_404(TutorProfile, id=id)
    if request.method == "POST":
        status=request.POST.get("decision")
        if status == "verified":
            tutor.verification_status = 1
        if status == "rejected":
            tutor.verification_status = 2
            tutor.current_step = 6
            tutor.profile_completed=False
            rejection_reason = request.POST.get("rejection_reason").strip()
            tutor.rejection_reason = rejection_reason
        if status == "update_reason":
            rejection_reason = request.POST.get("update_reason").strip()
            tutor.rejection_reason = rejection_reason
            tutor.save()
            return redirect("tutors_approval")
        tutor.save()
        return redirect("tutors_list")
    context={
        "tutor":tutor
    }
    return render(request, 'admin_panel/tutors/tutor-review.html', context)

@admin_required
def tutor_info(request, id):
    tutor=get_object_or_404(TutorProfile, id=id)
    if request.method == "POST":
            status=request.POST.get("decision")
            if status == "reactivate":
                tutor.user.is_active = True
                
            if status == "suspended":
                tutor.user.is_active = False                
                suspension_reason = request.POST.get("suspension_reason")
                tutor.suspension_reason = suspension_reason
            tutor.user.save()
            tutor.save()
            return redirect("tutors_list")
    context={
        "tutor":tutor
    }
    return render(request, 'admin_panel/tutors/tutor-info.html', context)

@admin_required
def student_tutor_requests(request):

    base_related = (
        'student__user',
        'tutor_teaching__tutor',
        'tutor_teaching__grade_subject__grade',
        'tutor_teaching__grade_subject__subject',
    )

    # 1. Querysets
    pending_requests = TutorRequest.objects.filter(
        status='pending'
    ).select_related(*base_related).order_by('-created_at')

    accepted_requests = TutorRequest.objects.filter(
        status='accepted'
    ).select_related(*base_related).order_by('-responded_at')

    started_requests = TutorRequest.objects.filter(
        status='in_progress'
    ).select_related(*base_related).order_by('-teaching_started_at')

    completed_requests = TutorRequest.objects.filter(
        status='completed'
    ).select_related(*base_related).order_by('-teaching_completed_at')

    # 2. Summary counts (before search)
    pending_count = pending_requests.count()
    not_started_count = accepted_requests.count()
    in_progress_count = started_requests.count()
    completed_count = completed_requests.count()

    # 3. Search filters
    student_search = request.GET.get('student_search', '').strip()
    tutor_search = request.GET.get('tutor_search', '').strip()

    if student_search:
        student_filter = Q(student__full_name__icontains=student_search)
        pending_requests = pending_requests.filter(student_filter)
        accepted_requests = accepted_requests.filter(student_filter)
        started_requests = started_requests.filter(student_filter)
        completed_requests = completed_requests.filter(student_filter)

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
    pending_paginator = Paginator(pending_requests, 5)
    accepted_paginator = Paginator(accepted_requests, 5)
    started_paginator = Paginator(started_requests, 5)
    completed_paginator = Paginator(completed_requests, 5)  

    tab = request.GET.get('tab', 'pending')
    page_number = request.GET.get('page', 1)

    page_obj_pending = pending_paginator.get_page(page_number if tab == 'pending' else 1)
    page_obj_accepted = accepted_paginator.get_page(page_number if tab == 'not_started' else 1)
    page_obj_started = started_paginator.get_page(page_number if tab == 'in_progress' else 1)
    page_obj_completed = completed_paginator.get_page(page_number if tab == 'completed' else 1)

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
            'pending': 'admin_panel/student-tutor/_pending_table.html',
            'not_started': 'admin_panel/student-tutor/_not_started_table.html',
            'in_progress': 'admin_panel/student-tutor/_in_progress_table.html',
            'completed': 'admin_panel/student-tutor/_completed_table.html',
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
    return render(request, 'admin_panel/student-tutor/student-tutor-requests.html', context)

# locations
@admin_required
def regions(request):
    return render(request, 'admin_panel/location/regions.html')

# grades
@admin_required
def grades_list(request):
    if request.method == "POST":
        grade=request.POST.get("grade")
        if grade:
            Grade.objects.create(
            name=grade
        )
    grades=Grade.objects.all()
    paginator = Paginator(grades, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context={
            "grades":page_obj,
        }
    return render(
        request,
        'admin_panel/grade-subject/grades-list.html',
        context
    )

@admin_required
def grade_edit(request, id):
    grade=get_object_or_404(Grade, id=id)
    if request.method == "POST":
        updated_grade=request.POST.get("grade")
        if updated_grade:
            grade.name = updated_grade        
            grade.save() 
        return redirect('grades_list')   
    
    context={
        "grade":grade
    }
    return render(request, 'admin_panel/grade-subject/grade-edit.html', context)

@admin_required
def grade_delete(request, id):
    grade = get_object_or_404(Grade, id=id)
    if request.method == "POST":
        grade.delete()
        return redirect('grades_list')

    return redirect('grades_list')

# subjects
@admin_required
def subjects_list(request):
    if request.method == "POST":
        subject=request.POST.get("subject")
        if subject:
            Subject.objects.create(
            name=subject
        )
    subjects=Subject.objects.all()
    paginator = Paginator(subjects, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context={
            "subjects":page_obj,
        }
    return render(
        request,
        'admin_panel/grade-subject/subjects-list.html',
        context
    )

@admin_required
def subject_edit(request, id):
    subject=get_object_or_404(Subject, id=id)
    if request.method == "POST":
        updated_subject=request.POST.get("subject")
        if updated_subject:
            subject.name = updated_subject        
            subject.save() 
        return redirect('subjects_list')   
    
    context={
        "subject":subject
    }
    return render(request, 'admin_panel/grade-subject/subject-edit.html', context)

@admin_required
def subject_delete(request, id):
    subject = get_object_or_404(Subject, id=id)
    if request.method == "POST":
        subject.delete()
        return redirect('subjects_list')

    return redirect('subjects_list')


def grade_subject(request):
    grades = Grade.objects.all()
    subjects = Subject.objects.all().order_by('name')

    grade_id = request.POST.get('grade') if request.method == 'POST' else request.GET.get('grade')

    selected_grade = None
    assigned_subjects = GradeSubject.objects.none()

    if grade_id:
        selected_grade = get_object_or_404(Grade, id=grade_id)

        assigned_subjects = GradeSubject.objects.filter(
            grade=selected_grade
        ).select_related('subject')

    if request.method == 'POST':

        subject_ids = request.POST.getlist('subjects')

        selected_subjects = Subject.objects.filter(
            id__in=subject_ids
        )

        with transaction.atomic():

            # Update existing mappings
            GradeSubject.objects.filter(
                grade=selected_grade
            ).delete()

            GradeSubject.objects.bulk_create([
                GradeSubject(
                    grade=selected_grade,
                    subject=subject
                )
                for subject in selected_subjects
            ])

        messages.success(
            request,
            f"Subjects updated for {selected_grade.name}."
        )

        return redirect(
            f"{request.path}?grade={selected_grade.id}"
        )

    assigned_subject_ids = list(
        assigned_subjects.values_list('subject_id', flat=True)
    )

    context = {
        'grades': grades,
        'subjects': subjects,
        'selected_grade': selected_grade,
        'assigned_subjects': assigned_subjects,
        'assigned_subject_ids': assigned_subject_ids,
    }

    return render(
        request,
        'admin_panel/grade-subject/grade-subject.html',
        context
    )


def get_grade_subjects(request, grade_id):

    assigned_subjects = GradeSubject.objects.filter(
        grade_id=grade_id
    ).select_related('subject')

    subjects = [
        {
            'id': item.subject.id,
            'name': item.subject.name
        }
        for item in assigned_subjects
    ]

    return JsonResponse({
        'subjects': subjects
    })