from django.db import models

from accounts.models import User
from core.models import Location

# Create your models here.
class TutorProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="tutor_profile"
    )

    profile_picture = models.ImageField(
            upload_to="tutor_profiles/",
            null=True,
            blank=True
    )
    full_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        null=True,
        blank=True
    )
    phone = models.CharField(max_length=15, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    experience = models.PositiveIntegerField(
        default=0,
        help_text="Experience in years"
    )
    cv = models.FileField(
        upload_to='tutor_cvs/',
        blank=True,
        null=True
    )   
    description = models.TextField(
        blank=True
    )  
    hourly_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )     
    location = models.OneToOneField(
        Location,
        on_delete=models.CASCADE,
        related_name="tutor_profile",
        null=True,
        blank=True
    )
    profile_completed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return f"{self.full_name}"