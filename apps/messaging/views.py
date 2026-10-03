from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.messaging.models import Conversation, Message
from apps.accounts.models import User
from apps.jobs.models import Job
from apps.notifications.models import Notification

@login_required
def inbox_view(request, conversation_id=None):
    """Unified direct messaging inbox for recruiters and job seekers."""
    user = request.user
    conversations = Conversation.objects.filter(
        Q(seeker=user) | Q(recruiter=user)
    ).select_related('seeker', 'recruiter', 'job').order_by('-updated_at')

    active_conversation = None
    chat_messages = []

    if conversation_id:
        active_conversation = get_object_or_404(
            Conversation.objects.select_related('seeker', 'recruiter', 'job'),
            pk=conversation_id
        )
        # Security check: must be a participant
        if active_conversation.seeker != user and active_conversation.recruiter != user:
            messages.error(request, _("Unauthorized access to private conversation."))
            return redirect('messaging:inbox')

        # Mark incoming messages as read
        active_conversation.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)
        chat_messages = active_conversation.messages.select_related('sender').all()
    elif conversations.exists():
        # Open first conversation by default
        return redirect('messaging:chat', conversation_id=conversations.first().pk)

    active_other_user = None
    if active_conversation:
        active_other_user = active_conversation.recruiter if user == active_conversation.seeker else active_conversation.seeker

    for conv in conversations:
        conv.other_user = conv.recruiter if user == conv.seeker else conv.seeker

    return render(request, 'messaging/inbox.html', {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'active_other_user': active_other_user,
        'chat_messages': chat_messages,
    })


@login_required
def send_message_view(request, conversation_id):
    """Send message in thread (supports regular POST and AJAX JSON)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    conversation = get_object_or_404(Conversation, pk=conversation_id)
    if conversation.seeker != request.user and conversation.recruiter != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'Empty content'}, status=400)

    msg = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    conversation.save(update_fields=['updated_at'])

    # Determine recipient
    recipient = conversation.recruiter if request.user == conversation.seeker else conversation.seeker

    # Trigger database notification
    Notification.send(
        recipient=recipient,
        title=_("New Message Received"),
        message=_(f"{request.user.get_full_name()} sent you a message: '{content[:50]}...'"),
        notification_type=Notification.NotificationType.NEW_MESSAGE,
        link_url=f"/messages/{conversation.pk}/"
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message_id': msg.pk,
            'sender_name': msg.sender.get_full_name(),
            'content': msg.content,
            'created_at': msg.created_at.strftime('%I:%M %p')
        })

    return redirect('messaging:chat', conversation_id=conversation.pk)


@login_required
def start_conversation_view(request, recipient_id):
    """Initiate conversation between recruiter and candidate."""
    recipient = get_object_or_404(User, pk=recipient_id)
    job_id = request.GET.get('job_id')
    job = Job.objects.filter(pk=job_id).first() if job_id else None

    if request.user == recipient:
        messages.warning(request, _("Cannot start a conversation with yourself."))
        return redirect('messaging:inbox')

    # Identify seeker and recruiter roles
    if request.user.is_recruiter:
        recruiter = request.user
        seeker = recipient
    else:
        recruiter = recipient
        seeker = request.user

    conversation, created = Conversation.objects.get_or_create(
        seeker=seeker,
        recruiter=recruiter,
        job=job
    )

    return redirect('messaging:chat', conversation_id=conversation.pk)
