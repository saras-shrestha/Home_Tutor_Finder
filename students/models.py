from django.db import models
from accounts.models import User
from core.models import Grade, Location

# Create your models here.
class StudentProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    EDUCATION_LEVEL_CHOICES = (
        ('primary', 'Primary Level (Class 1–5)'),
        ('basic', 'Basic Level (Class 6–8)'),
        ('secondary', 'Secondary Level (Class 9–10)'),
        ('higher_secondary', 'Higher Secondary Level (+2)'),
        ('undergraduate', "Undergraduate Level (Bachelor's)"),
        ('postgraduate', "Postgraduate Level (Master's)"),        
        ('other', 'Other'),
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
        related_name="student_grade"
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
    current_step = models.PositiveSmallIntegerField(default=1)
    profile_completed = models.BooleanField(default=False)
    profile_completed_at = models.DateTimeField(
        null=True, blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return f"{self.full_name}"