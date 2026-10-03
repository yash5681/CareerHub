from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class SubscriptionPlan(models.Model):
    class BillingPeriod(models.TextChoices):
        MONTHLY = 'monthly', _('Per Month')
        YEARLY = 'yearly', _('Per Year')
        ONE_TIME = 'one_time', _('One-Time')

    name = models.CharField(_('Plan Name'), max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    price = models.DecimalField(_('Price (₹ INR)'), max_digits=10, decimal_places=2, default=0.00)
    billing_period = models.CharField(max_length=20, choices=BillingPeriod.choices, default=BillingPeriod.MONTHLY)
    
    job_posting_limit = models.PositiveIntegerField(_('Job Posting Limit'), default=2)
    featured_job_limit = models.PositiveIntegerField(_('Featured Job Postings Limit'), default=0)
    candidate_contacts_limit = models.PositiveIntegerField(_('Candidate Direct Messages Limit'), default=20)
    
    description = models.CharField(_('Short Description'), max_length=255, blank=True)
    features_list = models.TextField(_('Key Features (One feature per line)'),
                                     help_text=_("e.g.\nPost up to 15 Active Jobs\n3 Featured Jobs on Homepage\nPriority Candidate Pipeline\nEmail Support"))
    
    is_popular = models.BooleanField(_('Highlight as Most Popular'), default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
        ordering = ['order', 'price']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - ₹{self.price:g} ({self.get_billing_period_display()})"

    def get_features(self):
        return [f.strip() for f in self.features_list.split('\n') if f.strip()]

    @property
    def is_free(self):
        return self.price == 0


class Payment(models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', _('Order Created')
        SUCCESS = 'success', _('Payment Successful')
        FAILED = 'failed', _('Payment Failed')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, related_name='payments')
    
    razorpay_order_id = models.CharField(_('Razorpay Order ID'), max_length=150, unique=True)
    razorpay_payment_id = models.CharField(_('Razorpay Payment ID'), max_length=150, blank=True)
    razorpay_signature = models.CharField(_('Razorpay Signature'), max_length=255, blank=True)
    
    amount = models.DecimalField(_('Amount Paid (₹)'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('Currency'), max_length=10, default='INR')
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.CREATED)
    
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.razorpay_order_id} - ₹{self.amount} ({self.get_status_display()})"


class RecruiterSubscription(models.Model):
    recruiter = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='active_subscriptions')
    active_from = models.DateTimeField(default=timezone.now)
    active_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    jobs_posted_this_cycle = models.PositiveIntegerField(default=0)
    featured_jobs_posted_this_cycle = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Recruiter Subscription')
        verbose_name_plural = _('Recruiter Subscriptions')

    def __str__(self):
        return f"{self.recruiter.get_full_name()} - {self.plan.name} (Valid till {self.active_until.strftime('%d %b %Y')})"

    @property
    def has_expired(self):
        return timezone.now() > self.active_until

    @property
    def can_post_job(self):
        if not self.is_active or self.has_expired:
            return False
        return self.jobs_posted_this_cycle < self.plan.job_posting_limit

    @property
    def can_post_featured_job(self):
        if not self.is_active or self.has_expired:
            return False
        return self.featured_jobs_posted_this_cycle < self.plan.featured_job_limit
