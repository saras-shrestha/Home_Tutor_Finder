
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


def create_notification(
    recipient,
    title,
    message,
    notification_type='general',
    sender=None,
    link=None
):
    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )


def notify_admins(
    title,
    message,
    notification_type,
    sender=None,
    link=None
):
    admins = User.objects.filter(
        is_staff=True,
        is_active=True
    )

    notifications = [
        Notification(
            recipient=admin,
            sender=sender,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )
        for admin in admins
    ]

    return Notification.objects.bulk_create(notifications)
