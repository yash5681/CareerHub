from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class JobApplication(models.Model):
    class Status(models.TextChoices):
        APPLIED = 'applied', _('Applied')
        UNDER_REVIEW = 'under_review', _('Under Review')
        SHORTLISTED = 'shortlisted', _('Shortlisted')
        INTERVIEW_SCHEDULED = 'interview_scheduled', _('Interview Scheduled')
        SELECTED = 'selected', _('Selected / Offered')
        REJECTED = 'rejected', _('Rejected')
        WITHDRAWN = 'withdrawn', _('Withdrawn')

    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    cover_letter = models.TextField(_('Cover Letter / Pitch'), blank=True)
    status = models.CharField(_('Application Status'), max_length=30, choices=Status.choices, default=Status.APPLIED)
    recruiter_notes = models.TextField(_('Private Recruiter Notes'), blank=True,
                                      help_text=_("Notes visible only to hiring team"))
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Job Application')
        verbose_name_plural = _('Job Applications')
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.get_full_name()} -> {self.job.title} ({self.get_status_display()})"

    @property
    def badge_color_class(self):
        mapping = {
            self.Status.APPLIED: 'bg-primary-subtle text-primary border border-primary',
            self.Status.UNDER_REVIEW: 'bg-info-subtle text-info-emphasis border border-info',
            self.Status.SHORTLISTED: 'bg-warning-subtle text-warning-emphasis border border-warning',
            self.Status.INTERVIEW_SCHEDULED: 'bg-purple-subtle text-purple border',
            self.Status.SELECTED: 'bg-success-subtle text-success border border-success',
            self.Status.REJECTED: 'bg-danger-subtle text-danger border border-danger',
            self.Status.WITHDRAWN: 'bg-secondary-subtle text-secondary border border-secondary',
        }
        return mapping.get(self.status, 'bg-light text-dark')


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=30, choices=JobApplication.Status.choices)
    new_status = models.CharField(max_length=30, choices=JobApplication.Status.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Application Status History')
        verbose_name_plural = _('Application Status Histories')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.application.id}: {self.previous_status} -> {self.new_status}"
