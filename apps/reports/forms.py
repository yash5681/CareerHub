from django import forms
from apps.reports.models import JobReport, CompanyReport

class JobReportForm(forms.ModelForm):
    class Meta:
        model = JobReport
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide specific details (e.g. Recruiter asked for security deposit / email domain does not match company)...'
            }),
        }


class CompanyReportForm(forms.ModelForm):
    class Meta:
        model = CompanyReport
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
