from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        APPLICATION_SUBMITTED = 'application_submitted', _('Application Submitted')
        APPLICATION_STATUS = 'application_status', _('Application Status Updated')
        INTERVIEW_SCHEDULED = 'interview_scheduled', _('Interview Scheduled')
        INTERVIEW_UPDATED = 'interview_updated', _('Interview Updated')
        NEW_MESSAGE = 'new_message', _('New Message Received')
        PAYMENT_SUCCESS = 'payment_success', _('Payment Completed')
        JOB_PUBLISHED = 'job_published', _('Job Published')
        SYSTEM = 'system', _('System Notification')

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(_('Notification Title'), max_length=200)
    message = models.TextField(_('Message Content'))
    notification_type = models.CharField(max_length=35, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    link_url = models.CharField(_('Destination Link'), max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.recipient.email}: {self.title}"

    @classmethod
    def send(cls, recipient, title, message, notification_type=NotificationType.SYSTEM, link_url=''):
        return cls.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            link_url=link_url
        )
