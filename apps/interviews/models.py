from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Interview(models.Model):
    class InterviewType(models.TextChoices):
        VIDEO = 'video', _('Video Call (Online)')
        PHONE = 'phone', _('Phone / Telephonic Round')
        IN_PERSON = 'in_person', _('In-Person (Office / On-site)')

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', _('Scheduled')
        RESCHEDULED = 'rescheduled', _('Rescheduled')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')

    application = models.ForeignKey('applications.JobApplication', on_delete=models.CASCADE, related_name='interviews')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='interviews')
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interviews_as_candidate')
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_interviews')
    
    interview_type = models.CharField(_('Interview Type'), max_length=20, choices=InterviewType.choices, default=InterviewType.VIDEO)
    interview_date = models.DateField(_('Interview Date'))
    interview_time = models.TimeField(_('Interview Time'))
    
    meeting_url = models.URLField(_('Meeting URL (Google Meet / Zoom / Teams)'), blank=True)
    location_address = models.TextField(_('Office / Venue Address'), blank=True,
                                        help_text=_("Required for In-person rounds"))
    
    interview_round = models.CharField(_('Round Name'), max_length=100, default='Technical Round',
                                       help_text=_("e.g. Technical Round 1, HR Discussion, Coding Challenge"))
    notes = models.TextField(_('Instructions for Candidate'), blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Interview')
        verbose_name_plural = _('Interviews')
        ordering = ['interview_date', 'interview_time']

    def __str__(self):
        return f"{self.interview_round} for {self.candidate.get_full_name()} ({self.job.title})"
