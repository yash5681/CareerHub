from django import forms
from django.utils.translation import gettext_lazy as _
from apps.applications.models import JobApplication
from apps.resumes.models import Resume

class JobApplicationForm(forms.ModelForm):
    resume = forms.ModelChoiceField(
        label=_("Select Resume"),
        queryset=Resume.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cover_letter = forms.CharField(
        label=_("Cover Letter / Note to Recruiter"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _("Explain why you're a great fit for this position, highlight relevant projects, and mention your availability...")
        })
    )

    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['resume'].queryset = Resume.objects.filter(user=user)
            # Pre-select primary resume if available
            primary_resume = Resume.objects.filter(user=user, is_primary=True).first()
            if primary_resume:
                self.fields['resume'].initial = primary_resume


class RecruiterStatusUpdateForm(forms.ModelForm):
    comment = forms.CharField(
        label=_("Reason / Note for Status Change"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional note about this transition'})
    )

    class Meta:
        model = JobApplication
        fields = ['status', 'recruiter_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'recruiter_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Private internal feedback for the hiring committee'}),
        }
