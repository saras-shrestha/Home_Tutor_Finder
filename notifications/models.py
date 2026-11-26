from django.db import models
from django.conf import settings

# Create your models here.

class Notification(models.Model):

    NOTIFICATION_TYPES = [
        # Tutor registration and profile approval
        ('profile_completed', 'Profile Completed'),
        ('tutor_approved', 'Tutor Approved'),
        ('tutor_rejected', 'Tutor Rejected'),

        # Student tutor requests
        ('tutor_request', 'New Tutor Request'),
        ('request_accepted', 'Request Accepted'),
        ('request_rejected', 'Request Rejected'),
        ('request_cancelled', 'Request Cancelled'),

        # Teaching schedule and course
        ('schedule_created', 'Schedule Created'),
        ('schedule_updated', 'Schedule Updated'),
        ('schedule_cancelled', 'Schedule Cancelled'),
        ('course_completed', 'Course Completed'),

        # General
        ('general', 'General Notification'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        default='general'
    )

    title = models.CharField(max_length=150)

    message = models.TextField()

    link = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['recipient', 'is_read']
            ),
            models.Index(
                fields=['recipient', '-created_at']
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient}"
