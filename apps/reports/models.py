from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class JobReport(models.Model):
    class Reason(models.TextChoices):
        FAKE_JOB = 'fake_job', _('Fake Job or Suspicious Posting')
        INCORRECT_INFO = 'incorrect_info', _('Incorrect / Inaccurate Information')
        SPAM = 'spam', _('Spam or Duplicate Listing')
        SCAM_PAYMENT = 'scam', _('Asking for Money / Security Deposit Scam')
        EXPIRED = 'expired', _('Job Position Already Filled / Expired')
        OTHER = 'other', _('Other Violation')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending Review')
        RESOLVED = 'resolved', _('Action Taken / Resolved')
        DISMISSED = 'dismissed', _('Dismissed / False Alarm')

    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_reports')
    reason = models.CharField(_('Reason for Reporting'), max_length=30, choices=Reason.choices)
    details = models.TextField(_('Detailed Explanation'))
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    admin_notes = models.TextField(_('Admin Moderation Notes'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Job Report')
        verbose_name_plural = _('Job Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on {self.job.title} by {self.reported_by.email} ({self.get_reason_display()})"


class CompanyReport(models.Model):
    class Reason(models.TextChoices):
        INCORRECT_COMPANY = 'incorrect_company', _('Fraudulent / Impersonating Company')
        SPAM = 'spam', _('Spamming Applicants')
        UNETHICAL = 'unethical', _('Unethical Hiring Practices')
        OTHER = 'other', _('Other Concern')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending Review')
        RESOLVED = 'resolved', _('Resolved')
        DISMISSED = 'dismissed', _('Dismissed')

    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_reports')
    reason = models.CharField(_('Reason for Reporting'), max_length=30, choices=Reason.choices)
    details = models.TextField(_('Details'))
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    admin_notes = models.TextField(_('Admin Notes'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Company Report')
        verbose_name_plural = _('Company Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on {self.company.name} ({self.get_reason_display()})"
