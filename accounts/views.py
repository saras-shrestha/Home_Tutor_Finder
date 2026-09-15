from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from students.models import StudentProfile
from tutors.models import TutorProfile
from .forms import RegisterForm

# Create your views here.

def homePage(request):
    return render(request, 'index.html')

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
    return redirect('login')

def password_forgot(request):
    return render(request, 'accounts/forgot_password.html')
# @login_required
# def student_dashboard(request):
#     return render(request, 'accounts/student_dashboard.html')
@login_required
def tutor_dashboard(request):
    return render(request, 'accounts/tutor_dashboard.html')