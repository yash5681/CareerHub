from django import forms
from django.utils.translation import gettext_lazy as _
from apps.interviews.models import Interview

class InterviewScheduleForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            'interview_round', 'interview_type', 'interview_date',
            'interview_time', 'meeting_url', 'location_address', 'notes'
        ]
        widgets = {
            'interview_round': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Technical Round 1: System Design'}),
            'interview_type': forms.Select(attrs={'class': 'form-select'}),
            'interview_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'interview_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'meeting_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://meet.google.com/xyz-abc-def'}),
            'location_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address for In-Person interview (if applicable)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Candidate instructions (e.g. Keep laptop ready, camera on, portfolio handy)'}),
        }
