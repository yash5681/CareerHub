import os
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(
    regex=r'^\+?[0-9]{10,15}$',
    message=_("Phone number must be entered in the format: '+919999999999' or '9999999999'. Up to 15 digits allowed.")
)

class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for auth."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set.'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if not user.username:
            user.username = email.split('@')[0] + '_' + self.make_random_password(length=4)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        JOB_SEEKER = 'job_seeker', _('Job Seeker')
        RECRUITER = 'recruiter', _('Recruiter / Employer')
        ADMIN = 'admin', _('Administrator')

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.JOB_SEEKER)
    email = models.EmailField(_('Email Address'), unique=True)
    phone = models.CharField(_('Phone Number'), validators=[phone_regex], max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_job_seeker(self):
        return self.role == self.Role.JOB_SEEKER

    @property
    def is_recruiter(self):
        return self.role == self.Role.RECRUITER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser


class JobSeekerProfile(models.Model):
    class WorkPreference(models.TextChoices):
        ANY = 'any', _('Any Mode')
        ON_SITE = 'on_site', _('On-site / In-Office')
        REMOTE = 'remote', _('Remote / Work from Home')
        HYBRID = 'hybrid', _('Hybrid')

    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')
        PREFER_NOT_TO_SAY = 'prefer_not_to_say', _('Prefer not to say')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_seeker_profile')
    headline = models.CharField(_('Professional Headline'), max_length=255, blank=True, 
                                help_text=_("e.g. Senior Django Developer | Python & AWS Specialist"))
    summary = models.TextField(_('Career Summary'), blank=True,
                               help_text=_("A brief summary of your expertise, career goals, and key achievements."))
    current_job_title = models.CharField(_('Current Job Title'), max_length=150, blank=True)
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)
    gender = models.CharField(_('Gender'), max_length=25, choices=Gender.choices, default=Gender.PREFER_NOT_TO_SAY, blank=True)
    
    city = models.CharField(_('City'), max_length=100, blank=True)
    state = models.CharField(_('State'), max_length=100, blank=True)
    address = models.TextField(_('Permanent / Residential Address'), blank=True)
    preferred_location = models.CharField(_('Preferred Work City/Region'), max_length=200, blank=True)
    
    total_experience_years = models.DecimalField(_('Total Experience (Years)'), max_digits=4, decimal_places=1, default=0.0)
    current_salary = models.DecimalField(_('Current CTC (in ₹ LPA)'), max_digits=10, decimal_places=2, null=True, blank=True)
    expected_salary = models.DecimalField(_('Expected CTC (in ₹ LPA)'), max_digits=10, decimal_places=2, null=True, blank=True)
    notice_period_days = models.IntegerField(_('Notice Period (Days)'), default=30)
    work_preference = models.CharField(_('Work Preference'), max_length=20, choices=WorkPreference.choices, default=WorkPreference.ANY)
    
    skills_csv = models.TextField(_('Key Skills (Comma-separated)'), blank=True,
                                  help_text=_("e.g. Python, Django, PostgreSQL, Docker, React, REST APIs"))
    
    linkedin_url = models.URLField(_('LinkedIn Profile URL'), blank=True)
    github_url = models.URLField(_('GitHub Profile URL'), blank=True)
    portfolio_url = models.URLField(_('Portfolio / Personal Website'), blank=True)
    
    profile_views = models.PositiveIntegerField(default=0)
    completion_percentage = models.PositiveSmallIntegerField(default=25)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Job Seeker Profile')
        verbose_name_plural = _('Job Seeker Profiles')

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"

    def get_skills_list(self):
        if not self.skills_csv:
            return []
        return [s.strip() for s in self.skills_csv.split(',') if s.strip()]

    def calculate_completion(self):
        """Calculates dynamic profile completion percentage."""
        score = 20  # Base user registration
        if self.headline: score += 10
        if self.summary: score += 10
        if self.city and self.state: score += 10
        if self.skills_csv: score += 10
        if self.total_experience_years is not None: score += 5
        if self.expected_salary: score += 5
        if self.user.avatar: score += 10
        if self.educations.exists(): score += 10
        if self.experiences.exists(): score += 10
        self.completion_percentage = min(score, 100)
        self.save(update_fields=['completion_percentage'])
        return self.completion_percentage


class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    designation = models.CharField(_('Designation / Job Title'), max_length=150, blank=True,
                                   help_text=_("e.g. Talent Acquisition Lead, HR Manager, Founder"))
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='recruiters')
    department = models.CharField(_('Department'), max_length=100, blank=True)
    is_company_admin = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Recruiter Profile')
        verbose_name_plural = _('Recruiter Profiles')

    def __str__(self):
        company_name = self.company.name if self.company else "No Company"
        return f"{self.user.get_full_name()} ({self.designation} at {company_name})"


class Education(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(_('Degree / Course'), max_length=150, help_text=_("e.g. B.Tech in Computer Science, BCA, MBA"))
    institution = models.CharField(_('College / University / School'), max_length=255)
    field_of_study = models.CharField(_('Field of Study / Specialization'), max_length=150, blank=True)
    start_year = models.PositiveIntegerField(_('Starting Year'))
    end_year = models.PositiveIntegerField(_('Completion Year / Expected'), null=True, blank=True)
    grade = models.CharField(_('Grade / Percentage / CGPA'), max_length=50, blank=True)
    description = models.TextField(_('Activities / Coursework'), blank=True)

    class Meta:
        verbose_name = _('Education')
        verbose_name_plural = _('Educations')
        ordering = ['-start_year']

    def __str__(self):
        return f"{self.degree} from {self.institution}"


class Experience(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='experiences')
    company_name = models.CharField(_('Company / Organization'), max_length=200)
    job_title = models.CharField(_('Job Title / Designation'), max_length=150)
    location = models.CharField(_('Job Location'), max_length=150, blank=True)
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'), null=True, blank=True)
    is_current = models.BooleanField(_('I currently work here'), default=False)
    description = models.TextField(_('Key Responsibilities & Achievements'), blank=True)

    class Meta:
        verbose_name = _('Work Experience')
        verbose_name_plural = _('Work Experiences')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


class Project(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(_('Project Title'), max_length=200)
    technologies = models.CharField(_('Technologies Used'), max_length=255, blank=True,
                                   help_text=_("e.g. Python, Django, PostgreSQL, Bootstrap 5"))
    project_url = models.URLField(_('Project URL / GitHub Link'), blank=True)
    start_date = models.DateField(_('Start Date'), null=True, blank=True)
    end_date = models.DateField(_('End Date'), null=True, blank=True)
    description = models.TextField(_('Project Description & Highlights'), blank=True)

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-id']

    def __str__(self):
        return self.title


class Certification(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(_('Certification Title'), max_length=200)
    issuing_organization = models.CharField(_('Issuing Organization'), max_length=200)
    issue_date = models.DateField(_('Issue Date'))
    expiration_date = models.DateField(_('Expiration Date'), null=True, blank=True)
    credential_id = models.CharField(_('Credential ID'), max_length=100, blank=True)
    credential_url = models.URLField(_('Credential URL'), blank=True)

    class Meta:
        verbose_name = _('Certification')
        verbose_name_plural = _('Certifications')
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.name} by {self.issuing_organization}"


class Language(models.Model):
    class Proficiency(models.TextChoices):
        BASIC = 'basic', _('Basic / Elementary')
        CONVERSATIONAL = 'conversational', _('Conversational')
        FLUENT = 'fluent', _('Fluent / Professional')
        NATIVE = 'native', _('Native / Bilingual')

    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='languages')
    language = models.CharField(_('Language'), max_length=100)
    proficiency = models.CharField(_('Proficiency'), max_length=30, choices=Proficiency.choices, default=Proficiency.FLUENT)

    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')

    def __str__(self):
        return f"{self.language} ({self.get_proficiency_display()})"


class Achievement(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(_('Achievement Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    date = models.DateField(_('Date'), null=True, blank=True)

    class Meta:
        verbose_name = _('Achievement')
        verbose_name_plural = _('Achievements')

    def __str__(self):
        return self.title
