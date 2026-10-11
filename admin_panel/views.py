from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from tutors.models import TutorProfile
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

    pending_tutors=TutorProfile.objects.prefetch_related('qualifications')[:4]
    
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
        'admin_panel/tutors-list.html',
        context
    )
