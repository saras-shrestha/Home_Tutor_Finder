from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StudentProfile
from core.models import Region, District, City
from django.http import JsonResponse
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
        education_level = request.POST.get('education_level')              
        school_college = request.POST.get('school_college')        
        grade = request.POST.get('grade')
        learning_description = request.POST.get('phone')
        if (profile_picture and full_name and gender and date_of_birth and phone and education_level and school_college and grade and learning_description):
            profile_completed = True
            StudentProfile.objects.create(
                user=request.user,
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
    regions=Region.objects.all();
    return render(request, 'students/profile.html',{
        "regions": regions
    })

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