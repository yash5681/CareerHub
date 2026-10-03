from django import forms
from django.utils.translation import gettext_lazy as _
from apps.companies.models import Company, CompanyReview

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'logo', 'cover_image', 'tagline', 'industry', 'company_size',
            'founded_year', 'website', 'email', 'phone', 'city', 'state',
            'address', 'about', 'benefits', 'linkedin_url', 'twitter_url'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tagline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Empowering financial freedom across India'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'company_size': forms.Select(attrs={'class': 'form-select'}),
            'founded_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://company.com'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Health Insurance, Flexible Hours, Annual Offsite...'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


class CompanyReviewForm(forms.ModelForm):
    class Meta:
        model = CompanyReview
        fields = ['rating', 'title', 'pros', 'cons', 'review_text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Great engineering culture and high ownership'}),
            'pros': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What are the best parts about working here?'}),
            'cons': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What can be improved?'}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detailed advice and review for future applicants...'}),
        }
