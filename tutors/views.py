from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from core.models import Location, Region
from .models import TutorProfile, Qualification
from django.http import JsonResponse
from django.utils import timezone
from .models import TutorAvailability
from .forms import TutorAvailabilityForm
from django.contrib import messages
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
            tutor.full_name = request.POST.get('full_name')
            tutor.gender = request.POST.get('gender')
            tutor.phone = request.POST.get('phone') 
            if "profile_picture" in request.FILES:
                tutor.profile_picture = request.FILES["profile_picture"]
            if tutor.current_step<2:                
                tutor.current_step = 2
            tutor.save()
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
            if tutor.location:

                location = tutor.location

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

                tutor.location = location
            if tutor.current_step<3: 
                tutor.current_step = 3
            tutor.save()

            return JsonResponse({
                "success": True,
                "message": "Location saved successfully.",
                "next_step": 3
            })
        # Step 3: About
        elif section == "about": 
            tutor.description = request.POST.get("description")

            if tutor.current_step<4: 
                tutor.current_step = 4           
            tutor.save()

            return JsonResponse({
                "success": True,
                "next_step": 4
            })
        
        # Step 4: Qualification
        elif section == "qualification":

            qualification, created = Qualification.objects.get_or_create(
                tutor=tutor
            )

            qualification.highest_qualification = request.POST.get(
                "high_qualification"
            )

            qualification.study_field = request.POST.get(
                "study_field"
            )

            qualification.degree_name = request.POST.get(
                "degree_name"
            )

            qualification.college = request.POST.get(
                "college_name"
            )

            qualification.university = request.POST.get(
                "university"
            )

            qualification.country = request.POST.get(
                "study_country"
            )

            gpa = request.POST.get("tutor_gpa")

            qualification.gpa = gpa if gpa else None

            qualification.save()

            if tutor.current_step<5: 
                tutor.current_step = 5
            tutor.save()

            return JsonResponse({
                "success": True,
                "message": "Qualification saved successfully.",
                "next_step": 5
            })
        # Step 5: Certificationel
        if section == "certification":
            if "certificate" in request.FILES:
                tutor.certificate = request.FILES["certificate"]
            if tutor.current_step<6: 
                tutor.current_step = 6
            tutor.save()

            return JsonResponse({
                "success": True,
                "next_step": 6
            })
        
        # STEP 6 - CV and FINAL
        elif section == "cv":

            cv = request.FILES.get("cv")

            if not cv:
                return JsonResponse({
                    "success": False,
                    "message": "Please upload your CV."
                })

            tutor.cv = cv
            tutor.profile_completed = True
            tutor.profile_completed_at= timezone.now()
            tutor.current_step = 7
            tutor.save()

            return JsonResponse({
                "success": True,
                "completed": True,
                "redirect_url": reverse("tutor_dashboard")
            })

    regions=Region.objects.all();
    return render(
        request,
        "tutors/profile.html",
        {
            "tutor": tutor,
            "regions": regions,
            "current_step": tutor.current_step
        }
    )

@login_required
def tutor_availability(request):
    tutor = request.user.tutor_profile

    if request.method == 'POST':
        form = TutorAvailabilityForm(request.POST)

        if form.is_valid():
            slot = form.save(commit=False)
            slot.tutor = tutor
            slot.full_clean()
            slot.save()

            messages.success(request, 'Availability saved successfully.')
            return redirect('tutor_availability')
    else:
        form = TutorAvailabilityForm()

    availabilities = TutorAvailability.objects.filter(
        tutor=tutor
    ).order_by('day', 'start_time')

    return render(request, 'tutors/availability/availability.html', {
        'form': form,
        'availabilities': availabilities,
    })


@login_required
def edit_availability(request, pk):
    tutor = request.user.tutor_profile

    slot = get_object_or_404(
        TutorAvailability, pk=pk, tutor=tutor
    )

    if request.method == 'POST':
        form = TutorAvailabilityForm(request.POST, instance=slot)

        if form.is_valid():
            updated_slot = form.save(commit=False)
            updated_slot.tutor = tutor
            updated_slot.full_clean()
            updated_slot.save()

            messages.success(request, 'Availability updated.')
            return redirect('tutor_availability')
    else:
        form = TutorAvailabilityForm(instance=slot)

    return render(request, 'tutors/availability/edit_availability.html', {
        'form': form,
        'slot': slot,
    })


@login_required
def delete_availability(request, pk):
    tutor = request.user.tutor_profile

    slot = get_object_or_404(
        TutorAvailability, pk=pk, tutor=tutor
    )

    if request.method == 'POST':
        slot.delete()
        messages.success(request, 'Availability deleted.')

    return redirect('tutor_availability')

# Manage Location
def manage_location(request):
    tutor = request.user.tutor_profile
    
    if request.method=="POST":
        region_id = request.POST.get("region")
        district_id = request.POST.get("district")
        city_id = request.POST.get("city")
        address = request.POST.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")     

        # If location already exists, update it
        if tutor.location:

            location = tutor.location

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

            tutor.location = location
        tutor.save()
        return redirect('tutor_dashboard')

    regions=Region.objects.all();
    return render(
        request,
        "tutors/location/location.html",
        {
            "tutor": tutor,
            "regions": regions
        }
    )

