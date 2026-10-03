from django import forms
from django.utils.translation import gettext_lazy as _
from apps.jobs.models import Job, JobAlert, JobCategory, Skill

class JobPostForm(forms.ModelForm):
    skills_csv = forms.CharField(
        label=_("Key Skills (Comma-separated)"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Python, Django, PostgreSQL, Docker, AWS, React'
        }),
        help_text=_("Enter the top technical and functional skills required.")
    )

    class Meta:
        model = Job
        fields = [
            'title', 'category', 'department', 'job_type', 'work_mode',
            'location_city', 'location_state', 'experience_min', 'experience_max',
            'salary_min', 'salary_max', 'hide_salary', 'openings_count',
            'description', 'responsibilities', 'requirements', 'benefits',
            'education_required', 'application_deadline', 'status', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Backend Python Engineer'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Engineering & Technology'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'work_mode': forms.Select(attrs={'class': 'form-select'}),
            'location_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bengaluru'}),
            'location_state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Karnataka'}),
            'experience_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'e.g. 2'}),
            'experience_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'e.g. 5'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min CTC in ₹ LPA (e.g. 12)'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max CTC in ₹ LPA (e.g. 20)'}),
            'hide_salary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'openings_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Comprehensive overview of the role and what the team is building...'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Day-to-day responsibilities and technical expectations...'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Must-have qualifications, skills, and industry experience...'}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g. Health insurance for family, flexible remote policy, learning stipend...'}),
            'education_required': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B.Tech / B.E / MCA or equivalent'}),
            'application_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class JobAlertForm(forms.ModelForm):
    class Meta:
        model = JobAlert
        fields = ['title', 'keywords', 'category', 'location', 'job_type', 'work_mode', 'min_salary']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python Developer in Bengaluru'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Django, Python, REST'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City or State'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}, choices=[('', 'Any Job Type')] + list(Job.JobType.choices)),
            'work_mode': forms.Select(attrs={'class': 'form-select'}, choices=[('', 'Any Work Mode')] + list(Job.WorkMode.choices)),
            'min_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 10'}),
        }
