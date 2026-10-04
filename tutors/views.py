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
        section = request.POST.get("section")
        # Step 1: Personal Information
        if section == "personal":
            print("*****YES*****")
            tutor.full_name = request.POST.get('full_name')
            tutor.gender = request.POST.get('gender')
            tutor.phone = request.POST.get('phone') 
            if "profile_picture" in request.FILES:
                tutor.profile_picture = request.FILES["profile_picture"]
                            
            tutor.current_step = 2
            tutor.save()
            return JsonResponse({
                "success": True,
                "next_step": 2,
            })
        # Step 2: Location
        elif section == "location":
            location_id = request.POST.get("location_id")
            if location_id:
                from core.models import Location
                try:
                    location = Location.objects.get(id=location_id)
                    tutor.location = location
                    tutor.current_step = 3
                    tutor.save()
                    return JsonResponse({
                        "success": True,
                        "next_step": 3,
                    })
                except Location.DoesNotExist:
                    return JsonResponse({
                        "success": False,
                        "message": "Invalid location selected."
                    })
            else:
                return JsonResponse({
                    "success": False,
                    "message": "Location is required."
                })
        # Step 3: About
        elif section == "about": 
            tutor.description = request.POST.get("description", "")

            tutor.current_step = 4
            tutor.save()

            return JsonResponse({
                "success": True,
                "next_step": 4
            })
        # Step 4: Qualification
        elif section == "qualification":

            # Qualification will be saved here

            tutor.current_step = 5
            tutor.save()

            return JsonResponse({
                "success": True,
                "next_step": 5
            })
        # Step 5: Certificationelif section == "certification":

            # Certification will be saved here

            tutor.current_step = 6
            tutor.save()

            return JsonResponse({
                "success": True,
                "next_step": 6
            })

        # --------------------------------
        # STEP 6 - CV / FINAL
        # --------------------------------
        elif section == "cv":

            if "cv" in request.FILES:
                tutor.cv = request.FILES["cv"]

            tutor.profile_completed = True
            tutor.current_step = 7

            tutor.save()

            return JsonResponse({
                "success": True,
                "completed": True
            })

        return JsonResponse({
            "success": False,
            "message": "Invalid section."
        })

    return render(
        request,
        "tutors/profile.html",
        {
            "profile": tutor,
            "current_step": tutor.current_step
        }
    )