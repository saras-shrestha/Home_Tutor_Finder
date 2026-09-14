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

    class EducationLevel(models.TextChoices):
        SCHOOL = "Sc","School"
        COLLEGE = "Clz", "College"
        UNIVERSITY = "uNI"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    full_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        null=True,
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
    phone = models.CharField(max_length=15, blank=True)
   
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students"
    )

    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(
        null=True,
        blank=True
    )
    profile_picture = models.ImageField(
        upload_to="student_profiles/",
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