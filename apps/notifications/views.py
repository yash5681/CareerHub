from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.notifications.models import Notification

@login_required
def notifications_list_view(request):
    """View all notifications with unread indicators and quick links."""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Optional unread only filter
    if request.GET.get('filter') == 'unread':
        notifications = notifications.filter(is_read=False)

    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
    })


@login_required
def read_notification_view(request, pk):
    """Mark single notification as read and redirect to its link."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    
    if notification.link_url:
        return redirect(notification.link_url)
    return redirect('notifications:list')


@login_required
def mark_all_notifications_read_view(request):
    """AJAX endpoint to mark all notifications read."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, _("All notifications marked as read."))
    return redirect('notifications:list')
