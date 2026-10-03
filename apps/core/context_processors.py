from datetime import datetime
from django.conf import settings
from apps.core.models import SiteSetting
from apps.notifications.models import Notification
from apps.messaging.models import Conversation

def global_context(request):
    context = {
        'current_year': datetime.now().year,
        'LANGUAGES': settings.LANGUAGES,
        'unread_notifications_count': 0,
        'unread_messages_count': 0,
    }

    try:
        context['site_setting'] = SiteSetting.objects.first()
    except Exception:
        context['site_setting'] = None

    if request.user.is_authenticated:
        try:
            context['unread_notifications_count'] = Notification.objects.filter(
                recipient=request.user, is_read=False
            ).count()
        except Exception:
            context['unread_notifications_count'] = 0

        try:
            if request.user.is_job_seeker:
                convs = Conversation.objects.filter(seeker=request.user)
                context['unread_messages_count'] = sum(c.unread_count_for(request.user) for c in convs)
            elif request.user.is_recruiter:
                convs = Conversation.objects.filter(recruiter=request.user)
                context['unread_messages_count'] = sum(c.unread_count_for(request.user) for c in convs)
        except Exception:
            context['unread_messages_count'] = 0

    return context
