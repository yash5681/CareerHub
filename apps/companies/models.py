from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Company(models.Model):
    class CompanySize(models.TextChoices):
        STARTUP = '1-10', _('1-10 Employees (Startup)')
        SMALL = '11-50', _('11-50 Employees (Small)')
        MEDIUM = '51-200', _('51-200 Employees (Medium)')
        LARGE = '201-500', _('201-500 Employees (Mid-Market)')
        ENTERPRISE = '500+', _('500+ Employees (Enterprise)')

    name = models.CharField(_('Company Name'), max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    logo = models.ImageField(_('Company Logo'), upload_to='companies/logos/%Y/', blank=True, null=True)
    cover_image = models.ImageField(_('Cover Image'), upload_to='companies/covers/%Y/', blank=True, null=True)
    
    tagline = models.CharField(_('Tagline / Punchline'), max_length=255, blank=True)
    about = models.TextField(_('About Company'))
    industry = models.CharField(_('Industry / Sector'), max_length=150, help_text=_("e.g. Information Technology, FinTech, E-Commerce"))
    company_size = models.CharField(_('Company Size'), max_length=30, choices=CompanySize.choices, default=CompanySize.MEDIUM)
    founded_year = models.PositiveIntegerField(_('Year Founded'), null=True, blank=True)
    
    website = models.URLField(_('Company Website'), blank=True)
    email = models.EmailField(_('Corporate Contact Email'))
    phone = models.CharField(_('Corporate Phone'), max_length=30, blank=True)
    
    city = models.CharField(_('Headquarters City'), max_length=100)
    state = models.CharField(_('Headquarters State'), max_length=100)
    address = models.TextField(_('Office Address'), blank=True)
    
    linkedin_url = models.URLField(_('LinkedIn Page'), blank=True)
    twitter_url = models.URLField(_('Twitter / X'), blank=True)
    benefits = models.TextField(_('Perks & Benefits'), blank=True,
                                help_text=_("e.g. Health Insurance, Flexible Hours, Annual Bonus, ESOPs"))
    
    is_verified = models.BooleanField(_('Verified Employer Badge'), default=False)
    is_featured = models.BooleanField(_('Featured Employer'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Company.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def active_jobs_count(self):
        return self.jobs.filter(status='published').count()

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if not reviews.exists():
            return 0.0
        return round(reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0.0, 1)

    @property
    def total_reviews_count(self):
        return self.reviews.filter(is_approved=True).count()


class CompanyReview(models.Model):
    RATING_CHOICES = [(i, f"{i} Stars") for i in range(1, 6)]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_reviews')
    rating = models.PositiveSmallIntegerField(_('Rating'), choices=RATING_CHOICES, default=5)
    title = models.CharField(_('Review Title'), max_length=200)
    pros = models.TextField(_('Pros'), blank=True)
    cons = models.TextField(_('Cons'), blank=True)
    review_text = models.TextField(_('Detailed Review'))
    is_approved = models.BooleanField(_('Approved by Moderator'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Company Review')
        verbose_name_plural = _('Company Reviews')
        ordering = ['-created_at']
        unique_together = ('company', 'user')

    def __str__(self):
        return f"{self.rating}★ Review for {self.company.name} by {self.user.get_full_name()}"
