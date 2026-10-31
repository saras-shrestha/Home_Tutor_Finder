from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from tutors.models import TutorProfile
from students.models import StudentProfile
from core.models import Grade, Subject, GradeSubject
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db import transaction

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
    paginator = Paginator(students, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context={
            "students":page_obj,
        }
    return render(
        request,
        'admin_panel/students/students-list.html',
        context
    )

@admin_required
def tutors_list(request):
    tutors = TutorProfile.objects.exclude(verification_status=0).all()
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
    pending_tutors=TutorProfile.objects.filter(verification_status=0).prefetch_related('qualifications')
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
            rejection_reason = request.POST.get("rejection_reason")
            tutor.rejection_reason = rejection_reason
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
                tutor.verification_status = 4
            if status == "suspended":
                tutor.verification_status = 3
                suspension_reason = request.POST.get("suspension_reason")
                tutor.suspension_reason = suspension_reason
            tutor.save()
            return redirect("tutors_list")
    context={
        "tutor":tutor
    }
    return render(request, 'admin_panel/tutors/tutor-info.html', context)

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