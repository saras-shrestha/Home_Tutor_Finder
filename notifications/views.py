
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
@require_POST
def mark_as_read(request, pk):

    notification = Notification.objects.filter(
        pk=pk,
        recipient=request.user
    ).first()

    if not notification:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found.'
        }, status=404)

    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])

    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    return JsonResponse({
        'success': True,
        'unread_count': unread_count
    })


@login_required
@require_POST
def mark_all_as_read(request):

    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({
        'success': True,
        'unread_count': 0
    })
