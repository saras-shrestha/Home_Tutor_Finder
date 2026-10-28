from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StudentProfile
from django.urls import reverse
from core.models import Region, District, City, Location, Grade
from django.http import JsonResponse
from django.utils import timezone
# Create your views here.

@login_required
def student_dashboard(request):
    if request.user.role != "student":
        return redirect("home-page")

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
    student = request.user.student_profile
    if request.method=="POST":
        section = request.POST.get("section")
        # Step 1: Personal Information
        if section == "personal":
            student.full_name = request.POST.get('full_name')
            student.gender = request.POST.get('gender')
            student.phone = request.POST.get('phone')
            student.date_of_birth = request.POST.get('dob') 
            if "profile_picture" in request.FILES:
                student.profile_picture = request.FILES["profile_picture"]
            if student.current_step<2:                
                student.current_step = 2
            student.save()
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
            if student.location:

                location = student.location

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

                student.location = location
            if student.current_step<3: 
                student.current_step = 3
            student.save()

            return JsonResponse({
                "success": True,
                "message": "Location saved successfully.",
                "next_step": 3
            })
        # Step 3: About
        elif section == "about": 
            student.description = request.POST.get("description")

            if student.current_step<4: 
                student.current_step = 4           
            student.save()

            return JsonResponse({
                "success": True,
                "next_step": 4
            })
        
        # Step 4: Academic Information and Final
        elif section == "academic":
            student.education_level = request.POST.get('education_level')
            student.grade = Grade.objects.get(id=request.POST.get('grade'))
            student.school_college = request.POST.get('school_college')
            student.profile_completed = True
            student.profile_completed_at= timezone.now() 
            student.current_step = 5           
            student.save()
            return JsonResponse({
                "success": True,
                "message": "Academic Information saved successfully.",
                "redirect_url": reverse("student_dashboard")        
            })
        
    regions=Region.objects.all();
    grades=Grade.objects.all();
    return render(
        request,
        "students/profile.html",
        {
            "student": student,
            "regions": regions,
            "current_step": student.current_step,
            "grades": grades
        }
    )

# Json for respective district of selected region
def get_districts(request, region_id):
    districts = District.objects.filter(region=region_id)

    district_data = [
        {
            'id': district.id,
            'name': district.name
        }
        for district in districts
    ]
    return JsonResponse(district_data, safe=False)


# Json for respective city of selected district
def get_cities(request, district_id):
    cities = City.objects.filter(district=district_id)

    city_data = [
        {
            'id': city.id,
            'name': city.name
        }
        for city in cities
    ]

    return JsonResponse(city_data, safe=False)

# find tutors
def find_tutors(request):
    return render(request, 'students/tutor-management/find-tutors.html')