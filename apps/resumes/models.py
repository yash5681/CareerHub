import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_resume_file(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = settings.ALLOWED_RESUME_EXTENSIONS
    if ext not in valid_extensions:
        raise ValidationError(_(f"Unsupported file format. Please upload {', '.join(valid_extensions)} only."))
    if value.size > settings.MAX_RESUME_SIZE:
        raise ValidationError(_("File size exceeds 5MB limit. Please upload a smaller file."))

class Resume(models.Model):
    class ResumeType(models.TextChoices):
        UPLOADED = 'uploaded', _('Uploaded File (PDF / DOCX)')
        BUILDER = 'builder', _('CareerHub Resume Builder')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(_('Resume Title / Label'), max_length=150, help_text=_("e.g. Python Developer Resume"))
    resume_type = models.CharField(max_length=20, choices=ResumeType.choices, default=ResumeType.UPLOADED)
    file = models.FileField(upload_to='resumes/%Y/%m/', validators=[validate_resume_file], blank=True, null=True)
    template_name = models.CharField(max_length=50, default='modern',
                                     choices=[('modern', 'Modern Elegant'), ('classic', 'Classic Corporate'), ('minimal', 'Minimalist Tech')])
    is_primary = models.BooleanField(_('Set as Primary Resume'), default=False)
    summary_override = models.TextField(blank=True, help_text=_("Customized summary specifically for this resume"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Resume')
        verbose_name_plural = _('Resumes')
        ordering = ['-is_primary', '-created_at']

    def save(self, *args, **kwargs):
        # If this resume is set to primary, unset others for this user
        if self.is_primary:
            Resume.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        # If this is the user's only resume, make it primary automatically
        elif not Resume.objects.filter(user=self.user).exclude(pk=self.pk).exists():
            self.is_primary = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_resume_type_display()}) - {self.user.get_full_name()}"
