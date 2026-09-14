from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def student_dashboard(request):
    if request.user.role != "student":
        return redirect("home")

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
    if request.method=="POST":
        print("*****YES*****")
        profile_picture = request.POST.get('profile_picture')
        full_name = request.POST.get('full_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('dob')
        phone = request.POST.get('phone')
        description = request.POST.get('phone')  
        education_level = request.POST.get('education_level')              
        school_college = request.POST.get('school_college')        
        grade = request.POST.get('grade')
        


    return render(request, 'students/profile.html')