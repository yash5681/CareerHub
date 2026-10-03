from django.db import models
from django.utils.translation import gettext_lazy as _

class ContactMessage(models.Model):
    name = models.CharField(_('Full Name'), max_length=150)
    email = models.EmailField(_('Email Address'))
    phone = models.CharField(_('Phone Number'), max_length=20, blank=True)
    subject = models.CharField(_('Subject'), max_length=200)
    message = models.TextField(_('Message'))
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} ({self.subject})"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(_('Subscriber Email'), unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Newsletter Subscriber')
        verbose_name_plural = _('Newsletter Subscribers')

    def __str__(self):
        return self.email


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=100, default='CareerHub')
    tagline = models.CharField(max_length=255, default='India’s Leading Career Platform')
    contact_email = models.EmailField(default='support@careerhub.in')
    contact_phone = models.CharField(max_length=50, default='+91 98765 43210')
    address = models.TextField(default='Cyber City, Sector 24, Gurugram, Haryana 122002, India')
    
    linkedin_url = models.URLField(default='https://linkedin.com/company/careerhub')
    twitter_url = models.URLField(default='https://twitter.com/careerhub_in')
    facebook_url = models.URLField(default='https://facebook.com/careerhub.india')
    instagram_url = models.URLField(default='https://instagram.com/careerhub_in')
    
    class Meta:
        verbose_name = _('Site Setting')
        verbose_name_plural = _('Site Settings')

    def __str__(self):
        return self.site_name
