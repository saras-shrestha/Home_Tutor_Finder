from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.timesince import timesince

from .models import Notification

@login_required
def all_notifications(request):
    filter_type = request.GET.get('filter', 'all')
    notifications_qs = Notification.objects.filter(recipient=request.user)

    if filter_type == 'unread':
        notifications_qs = notifications_qs.filter(is_read=False)

    paginator = Paginator(notifications_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pick the right base layout based on user role
    user = request.user
    if user.is_staff or user.is_superuser:
        base_template = 'admin_panel/admin-base.html'      # <-- Replace with your Admin base template path
    elif getattr(user, 'role', None) == 'tutor':  # <-- Or hasattr(user, 'tutor_profile')
        base_template = 'tutors/tutor-base.html'      # <-- Replace with your Tutor base template path
    else:
        base_template = 'students/student-base.html'    # <-- Replace with your Student base template path

    return render(request, 'notifications/all_notifications.html', {
        'page_obj': page_obj,
        'filter_type': filter_type,
        'base_template': base_template,
    })



@login_required
def fetch_notifications(request):
    all_user_notifications = Notification.objects.filter(recipient=request.user)
    unread_count = all_user_notifications.filter(is_read=False).count()

    data = [
        {
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'link': n.link or '#',
            'is_read': n.is_read,
            'time_since': f"{timesince(n.created_at)} ago",
        }
        for n in all_user_notifications[:5]
    ]

    return JsonResponse({
        'unread_count': unread_count,
        'notifications': data,
    })


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
