import random
import string
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class JobCategory(models.Model):
    name = models.CharField(_('Category Name'), max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    icon = models.CharField(_('FontAwesome Icon Class'), max_length=100, default='fa-solid fa-briefcase',
                            help_text=_("e.g. 'fa-solid fa-laptop-code', 'fa-solid fa-chart-line'"))
    description = models.TextField(_('Category Description'), blank=True)
    is_featured = models.BooleanField(_('Featured on Homepage'), default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Job Category')
        verbose_name_plural = _('Job Categories')
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def open_jobs_count(self):
        return self.jobs.filter(status=Job.Status.PUBLISHED).count()


class Skill(models.Model):
    name = models.CharField(_('Skill Name'), max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Location(models.Model):
    state = models.CharField(_('State / UT'), max_length=100)
    city = models.CharField(_('City'), max_length=100)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    is_popular = models.BooleanField(_('Popular Hub'), default=False)

    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')
        unique_together = ('state', 'city')
        ordering = ['state', 'city']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.city}-{self.state}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.city}, {self.state}"


class Job(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = 'full_time', _('Full Time')
        PART_TIME = 'part_time', _('Part Time')
        INTERNSHIP = 'internship', _('Internship')
        FREELANCE = 'freelance', _('Freelance')
        CONTRACT = 'contract', _('Contract')

    class WorkMode(models.TextChoices):
        ON_SITE = 'on_site', _('On-site')
        REMOTE = 'remote', _('Remote')
        HYBRID = 'hybrid', _('Hybrid')

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        CLOSED = 'closed', _('Closed')

    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='jobs')
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(_('Job Title'), max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    
    category = models.ForeignKey(JobCategory, on_delete=models.PROTECT, related_name='jobs')
    department = models.CharField(_('Department'), max_length=100, blank=True)
    
    job_type = models.CharField(_('Job Type'), max_length=30, choices=JobType.choices, default=JobType.FULL_TIME)
    work_mode = models.CharField(_('Work Mode'), max_length=30, choices=WorkMode.choices, default=WorkMode.ON_SITE)
    
    location_city = models.CharField(_('Job City'), max_length=100)
    location_state = models.CharField(_('Job State'), max_length=100)
    
    experience_min = models.DecimalField(_('Minimum Experience (Years)'), max_digits=4, decimal_places=1, default=0.0)
    experience_max = models.DecimalField(_('Maximum Experience (Years)'), max_digits=4, decimal_places=1, default=3.0)
    
    salary_min = models.DecimalField(_('Minimum Salary (₹ LPA)'), max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(_('Maximum Salary (₹ LPA)'), max_digits=10, decimal_places=2, null=True, blank=True)
    hide_salary = models.BooleanField(_('Hide salary from public job card (Competitive CTC)'), default=False)
    
    openings_count = models.PositiveIntegerField(_('Number of Openings'), default=1)
    
    description = models.TextField(_('Job Overview / Description'))
    responsibilities = models.TextField(_('Key Responsibilities'), blank=True)
    requirements = models.TextField(_('Candidate Requirements & Qualifications'), blank=True)
    benefits = models.TextField(_('Perks, Benefits & Culture'), blank=True)
    education_required = models.CharField(_('Education Qualification'), max_length=200, blank=True,
                                          help_text=_("e.g. B.E/B.Tech, BCA, MCA, Any Graduate"))
    
    skills = models.ManyToManyField(Skill, related_name='jobs', blank=True)
    
    application_deadline = models.DateField(_('Application Deadline'), null=True, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    is_featured = models.BooleanField(_('Featured Job Post'), default=False)
    is_fresher_friendly = models.BooleanField(_('Fresher Friendly (0 Experience)'), default=False)
    
    views_count = models.PositiveIntegerField(default=0)
    saves_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['job_type', 'work_mode']),
            models.Index(fields=['location_city', 'location_state']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            self.slug = f"{slugify(self.title)}-{slugify(self.company.name)}-{rand_suffix}"
        if self.experience_min == 0:
            self.is_fresher_friendly = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    @property
    def is_active(self):
        if self.status != self.Status.PUBLISHED:
            return False
        if self.application_deadline and self.application_deadline < timezone.now().date():
            return False
        return True

    @property
    def salary_display(self):
        if self.hide_salary:
            return _("Competitive / Not Disclosed")
        if self.salary_min and self.salary_max:
            return f"₹{self.salary_min:g} - ₹{self.salary_max:g} LPA"
        if self.salary_min:
            return f"₹{self.salary_min:g}+ LPA"
        if self.salary_max:
            return f"Up to ₹{self.salary_max:g} LPA"
        return _("Best in Industry")

    @property
    def experience_display(self):
        if self.experience_min == 0 and (self.experience_max is None or self.experience_max == 0):
            return _("Fresher (0 yrs)")
        if self.experience_min and self.experience_max:
            return f"{self.experience_min:g}-{self.experience_max:g} yrs"
        if self.experience_min:
            return f"{self.experience_min:g}+ yrs"
        return _("Any Experience")


class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Saved Job')
        verbose_name_plural = _('Saved Jobs')
        unique_together = ('user', 'job')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} saved {self.job.title}"


class JobAlert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_alerts')
    title = models.CharField(_('Alert Name'), max_length=150, help_text=_("e.g. Django Jobs in Bangalore"))
    keywords = models.CharField(_('Keywords / Skills'), max_length=200, blank=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    location = models.CharField(_('Location / City'), max_length=150, blank=True)
    job_type = models.CharField(_('Job Type'), max_length=30, blank=True)
    work_mode = models.CharField(_('Work Mode'), max_length=30, blank=True)
    min_salary = models.DecimalField(_('Minimum Salary (₹ LPA)'), max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Job Alert')
        verbose_name_plural = _('Job Alerts')
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert: {self.title} ({self.user.email})"
