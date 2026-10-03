from django import forms
from django.utils.translation import gettext_lazy as _
from apps.resumes.models import Resume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'file', 'is_primary']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Backend Engineer Resume 2026'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'file': _("Upload PDF or DOCX format (Max 5MB)."),
            'is_primary': _("Set this as your default resume for 1-click job applications.")
        }


class ResumeBuilderForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'template_name', 'summary_override', 'is_primary']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Targeted Full-Stack Developer Resume'}),
            'template_name': forms.Select(attrs={'class': 'form-select'}),
            'summary_override': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Tailor your summary specifically for this resume version...'
            }),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
