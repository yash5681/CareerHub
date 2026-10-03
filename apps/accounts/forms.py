from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import (
    JobSeekerProfile, RecruiterProfile, Education, Experience,
    Project, Certification, Language
)
from apps.companies.models import Company
from apps.jobs.models import JobCategory

User = get_user_model()

class JobSeekerRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(label=_("First Name"), max_length=50, required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Rahul'}))
    last_name = forms.CharField(label=_("Last Name"), max_length=50, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sharma'}))
    email = forms.EmailField(label=_("Email Address"), required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'rahul.sharma@example.com'}))
    phone = forms.CharField(label=_("Mobile Number"), max_length=15, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'}))
    city = forms.CharField(label=_("Current City"), max_length=100, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bengaluru'}))
    state = forms.CharField(label=_("State"), max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Karnataka'}))
    preferred_category = forms.ModelChoiceField(
        label=_("Target Job Category"), queryset=JobCategory.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
                               validators=[validate_password])
    confirm_password = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))
    terms_accepted = forms.BooleanField(label=_("I accept the CareerHub Terms of Service & Privacy Policy"), required=True,
                                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("An account with this email address already exists."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', _("Passwords do not match."))
        return cleaned_data


class RecruiterRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(label=_("First Name"), max_length=50, required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Priya'}))
    last_name = forms.CharField(label=_("Last Name"), max_length=50, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Nair'}))
    email = forms.EmailField(label=_("Work / Corporate Email"), required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'priya@techinnovations.in'}))
    phone = forms.CharField(label=_("Contact Phone"), max_length=15, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 12345'}))
    company_name = forms.CharField(label=_("Company Name"), max_length=150, required=True,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TechInnovations Solutions Ltd'}))
    designation = forms.CharField(label=_("Your Designation"), max_length=100, required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Head of Talent Acquisition'}))
    industry = forms.CharField(label=_("Industry / Sector"), max_length=100, required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. FinTech / Software'}))
    company_size = forms.ChoiceField(label=_("Company Size"), choices=Company.CompanySize.choices,
                                     widget=forms.Select(attrs={'class': 'form-select'}))
    city = forms.CharField(label=_("HQ City"), max_length=100, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mumbai'}))
    state = forms.CharField(label=_("HQ State"), max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Maharashtra'}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
                               validators=[validate_password])
    confirm_password = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))
    terms_accepted = forms.BooleanField(label=_("I confirm I am an authorized representative of this company"), required=True,
                                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("An account with this email address already exists."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', _("Passwords do not match."))
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(label=_("Email Address"),
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com', 'autocomplete': 'email'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••', 'autocomplete': 'current-password'}))
    remember_me = forms.BooleanField(required=False, label=_("Keep me signed in on this device"),
                                     widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


class JobSeekerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, label=_("First Name"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, label=_("Last Name"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, label=_("Phone"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    avatar = forms.ImageField(required=False, label=_("Profile Photo"), widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = JobSeekerProfile
        fields = [
            'headline', 'summary', 'current_job_title', 'total_experience_years',
            'current_salary', 'expected_salary', 'notice_period_days', 'work_preference',
            'skills_csv', 'city', 'state', 'preferred_location', 'date_of_birth',
            'gender', 'linkedin_url', 'github_url', 'portfolio_url', 'address'
        ]
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Full-Stack Python/Django Engineer'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Highlight your core expertise, career journey, and top accomplishments...'}),
            'current_job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Engineer'}),
            'total_experience_years': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'current_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 12.5 (in ₹ LPA)'}),
            'expected_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 18.0 (in ₹ LPA)'}),
            'notice_period_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'work_preference': forms.Select(attrs={'class': 'form-select'}),
            'skills_csv': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, PostgreSQL, React, AWS, Docker'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bengaluru, Hyderabad, Remote'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/username'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourportfolio.dev'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'field_of_study', 'start_year', 'end_year', 'grade', 'description']
        widgets = {
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B.Tech Computer Science'}),
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Indian Institute of Technology'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science & Engineering'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8.8 CGPA / 82%'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company_name', 'job_title', 'location', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Razorpay Software'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Backend Developer'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bengaluru'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Key responsibilities and business impact delivered...'}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'technologies', 'project_url', 'start_date', 'end_date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. High-throughput Payment Engine'}),
            'technologies': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, Celery, Redis, PostgreSQL'}),
            'project_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/...'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuing_organization', 'issue_date', 'expiration_date', 'credential_id', 'credential_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AWS Certified Solutions Architect'}),
            'issuing_organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Amazon Web Services'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'credential_id': forms.TextInput(attrs={'class': 'form-control'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ['language', 'proficiency']
        widgets = {
            'language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. English, Hindi, Gujarati'}),
            'proficiency': forms.Select(attrs={'class': 'form-select'}),
        }
