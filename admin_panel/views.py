from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from tutors.models import TutorProfile
from students.models import StudentProfile
from django.core.paginator import Paginator

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

@login_required(login_url='admin_login')
def admin_dashboard(request):

    if not request.user.is_staff:
        return redirect('login')

    pending_tutors=TutorProfile.objects.prefetch_related('qualifications')[:2]
    
    context={
        "pending_tutors":pending_tutors,
    }

    return render(
        request,
        'admin_panel/admin_dashboard.html',
        context
    )

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

def tutors_list(request):
    tutors = TutorProfile.objects.all()
    paginator = Paginator(tutors, 2)
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

def students_list(request):
    students = StudentProfile.objects.all()
    paginator = Paginator(students, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context={
            "students":page_obj,
        }
    return render(
        request,
        'admin_panel/students-list.html',
        context
    )
def tutors_approval(request):
    pending_tutors=TutorProfile.objects.prefetch_related('qualifications')
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

def tutor_review(request, id):
    tutor=get_object_or_404(TutorProfile, id=id)
    if request.method == "POST":
        status=request.POST.get("review_status")
        if "review_update" in request.POST:
            if status == 1:
                tutor.verification_status = 1
            if status == 2:
                tutor.verification_status = 2
                rejection_reason = request.POST.get("rejection_reason")
            tutor.save()
            return redirect("tutors_approval")
    context={
        "tutor":tutor
    }
    return render(request, 'admin_panel/tutors/tutor-review.html', context)

# locations
def regions(request):
    return render(request, 'admin_panel/location/regions.html')