from django.db import models

from accounts.models import User
from core.models import Grade
from core.models import Location

# Create your models here.
class StudentProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    EDUCATION_LEVEL_CHOICES = (
        ("school", "School"),
        ("plus_two", "+2"),
        ("bachelor", "Bachelor"),
        ("master", "Master"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    profile_picture = models.ImageField(
            upload_to="student_profiles/",
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
    date_of_birth = models.DateField(
        null=True,
        blank=True
    )
    education_level = models.CharField(
            max_length=20,
            choices=EDUCATION_LEVEL_CHOICES,
            blank=True
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="students"
    )
    school_college = models.CharField(
        max_length=200,
        blank=True
    )    
    description = models.TextField(
        blank=True
    )       
    location = models.OneToOneField(
        Location,
        on_delete=models.CASCADE,
        related_name="student_location",
        null=True,
        blank=True
    )
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return f"{self.full_name}"