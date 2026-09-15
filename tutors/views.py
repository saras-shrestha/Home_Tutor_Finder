from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TutorProfile
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
    if request.method=="POST":
        print("*****YES*****")
        profile_picture = request.POST.get('profile_picture')
        full_name = request.POST.get('full_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('dob')
        phone = request.POST.get('phone')          
        education_level = request.POST.get('education_level')              
        school_college = request.POST.get('school_college')        
        grade = request.POST.get('grade')
        learning_description = request.POST.get('phone')
        if (profile_picture and full_name and gender and date_of_birth and phone and education_level and school_college and grade and learning_description):
            profile_completed = True
            TutorProfile.objects.create(
                user="...",
                profile_picture=profile_picture,
                full_name=full_name,
                gender=gender,
                phone=phone,
                date_of_birth = date_of_birth,
                education_level=education_level,
                grade=grade,
                school_college=school_college,
                description=learning_description,
                profile_completed=profile_completed
            )

    return render(request, 'tutors/profile.html')