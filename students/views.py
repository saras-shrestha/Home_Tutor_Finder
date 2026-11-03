from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StudentProfile
from django.urls import reverse
from core.models import GradeSubject, Region, District, City, Location, Grade
from django.http import JsonResponse
from django.utils import timezone
import requests
from django.views.decorators.http import require_GET
from django.contrib import messages
from decimal import Decimal, InvalidOperation

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

    student_location = None

    if hasattr(request.user, 'student_profile'):
        student_location = request.user.student_profile.location

    context = {
        'grades': Grade.objects.all().order_by('id'),

        'grade_subjects': GradeSubject.objects.select_related(
            'grade',
            'subject'
        ).order_by('grade__id', 'subject__name'),

        'student_location': student_location,
    }

    return render(request, 'students/tutor-management/find-tutors.html', context)

@require_GET
def address_autocomplete(request):

    query = request.GET.get('q', '').strip()

    if len(query) < 3:
        return JsonResponse({'results': []})

    try:
        response = requests.get(
            'https://photon.komoot.io/api/',
            params={
                'q': query,
                'limit': 5,
                'lat': 27.7172,
                'lon': 85.3240,
            }, 
            headers={
                'User-Agent': 'HomeTutorFinder/1.0'
            },
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        results = []

        for feature in data.get('features', []):

            properties = feature.get('properties', {})
            coordinates = feature.get('geometry', {}).get(
                'coordinates', []
            )

            if len(coordinates) != 2:
                continue

            name_parts = [
                properties.get('name'),
                properties.get('street'),
                properties.get('district'),
                properties.get('city'),
                properties.get('state'),
                properties.get('country'),
            ]

            address = ', '.join(
                dict.fromkeys(
                    part for part in name_parts if part
                )
            )

            results.append({
                'name': address,
                'latitude': coordinates[1],
                'longitude': coordinates[0],
            })

        return JsonResponse({'results': results})

    except requests.RequestException:
        return JsonResponse(
            {'error': 'Address search is temporarily unavailable.'},
            status=503
        )


@login_required
def save_location(request):

    if request.method == 'POST':

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        address = request.POST.get('address')

        try:
            latitude = Decimal(latitude)
            longitude = Decimal(longitude)

            if not (-90 <= latitude <= 90):
                raise ValueError("Invalid latitude")

            if not (-180 <= longitude <= 180):
                raise ValueError("Invalid longitude")

        except (TypeError, ValueError, InvalidOperation):
            messages.error(request, "Please select a valid location.")
            return redirect('select_location')

        student = request.user.student_profile

        student.latitude = latitude
        student.longitude = longitude
        student.address = address

        student.save()

        messages.success(request, "Location saved successfully!")

        return redirect('student_dashboard')

    return redirect('select_location')