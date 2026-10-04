from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TutorProfile
from django.http import JsonResponse
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
        print("*****YES*****")
        tutor = request.user.tutor_profile
        # tutor.profile_picture = request.POST.get('profile_picture')
        tutor.full_name = request.POST.get('full_name')
        tutor.gender = request.POST.get('gender')
        tutor.phone = request.POST.get('phone') 
        if "profile_picture" in request.FILES:
            tutor.profile_picture = request.FILES["profile_picture"]
            print("*****asdfghjkl;*****")
        print("*****asdfghjkl;*****")
        tutor.save()
        return JsonResponse({
            "success": True,
            "message": "Personal information saved successfully."
        })
        print("*****asdfghjkl;*****")
        # # personal information 
        # if (profile_picture and full_name and gender and phone):
            
        #     # TutorProfile.objects.create(
        #     #     profile_picture=profile_picture,
        #     #     full_name=full_name,
        #     #     gender=gender,
        #     #     phone=phone,
        #     # )
            
        # education_level = request.POST.get('education_level')              
        # school_college = request.POST.get('school_college')        
        # grade = request.POST.get('grade')
        # learning_description = request.POST.get('phone')
        # if (profile_picture and full_name and gender and phone and education_level and school_college and grade and learning_description):
        #     profile_completed = True
        #     TutorProfile.objects.create(
               
        #         education_level=education_level,
        #         grade=grade,
        #         school_college=school_college,
        #         description=learning_description,
        #         profile_completed=profile_completed
        #     )
  
    return render(request, 'tutors/profile.html')