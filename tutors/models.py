from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.
class TutorProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
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
    location = models.ForeignKey(
        'core.Location',
        on_delete=models.SET_NULL,
        related_name="tutor_locations",
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

class TutorTeaching(models.Model):
    tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.CASCADE,
        related_name='teachings'
    )

    subject = models.ForeignKey(
        'core.Subject',
        on_delete=models.PROTECT,
        related_name='tutor_teachings'
    )

    grade = models.ForeignKey(
        'core.Grade',
        on_delete=models.PROTECT,
        related_name='tutor_teachings'
    )

    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tutor', 'subject', 'grade'],
                name='unique_tutor_subject_grade'
            )
        ]

    def __str__(self):
        return f"{self.tutor.full_name} - {self.subject} - {self.grade}"


class TutorAvailability(models.Model):
    DAYS = [
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]

    tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )

    day = models.CharField(
        max_length=10,
        choices=DAYS
    )

    start_time = models.TimeField()

    end_time = models.TimeField()
    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(
                    "End time must be after start time."
                )

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return (
            f"{self.tutor.full_name} - "
            f"{self.day} "
            f"{self.start_time} - {self.end_time}"
        )