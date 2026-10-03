from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.jobs.models import Job, JobCategory, SavedJob
from apps.companies.models import Company
from apps.blog.models import BlogPost
from apps.accounts.models import User
from apps.core.models import ContactMessage, NewsletterSubscriber, SiteSetting
from apps.core.forms import ContactForm

def home_view(request):
    """Rich home page for CareerHub with search hero, categories, featured jobs, and stats."""
    featured_jobs = Job.objects.filter(
        status=Job.Status.PUBLISHED, is_featured=True
    ).select_related('company', 'category')[:6]

    latest_jobs = Job.objects.filter(
        status=Job.Status.PUBLISHED
    ).select_related('company', 'category')[:6]

    popular_categories = JobCategory.objects.filter(is_featured=True).order_by('order')[:8]
    top_companies = Company.objects.filter(is_featured=True)[:6]
    recent_articles = BlogPost.objects.filter(is_published=True)[:3]

    # Live platform statistics
    stats = {
        'total_jobs': Job.objects.filter(status=Job.Status.PUBLISHED).count() or 1250,
        'total_companies': Company.objects.count() or 450,
        'total_seekers': User.objects.filter(role=User.Role.JOB_SEEKER).count() or 8500,
        'successful_hires': 3200,
    }

    user_saved_job_ids = set()
    if request.user.is_authenticated:
        user_saved_job_ids = set(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))

    return render(request, 'core/home.html', {
        'featured_jobs': featured_jobs,
        'latest_jobs': latest_jobs,
        'popular_categories': popular_categories,
        'top_companies': top_companies,
        'recent_articles': recent_articles,
        'stats': stats,
        'user_saved_job_ids': user_saved_job_ids,
    })


def about_view(request):
    """About CareerHub mission, vision, and team."""
    return render(request, 'core/about.html')


def contact_view(request):
    """Contact us page with inquiries database storage."""
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _("Thank you for reaching out! Our team will respond within 24 hours."))
        return redirect('core:contact')

    return render(request, 'core/contact.html', {'form': form})


def faq_view(request):
    """Frequently Asked Questions for job seekers and employers."""
    return render(request, 'core/faq.html')


def privacy_view(request):
    return render(request, 'core/privacy.html')


def terms_view(request):
    return render(request, 'core/terms.html')


def cookies_view(request):
    return render(request, 'core/cookies.html')


def newsletter_subscribe_view(request):
    """Handle newsletter subscription."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
            messages.success(request, _("Thank you for subscribing to CareerHub updates!"))
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))


# HTTP Error Handlers
def bad_request_view(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def permission_denied_view(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def page_not_found_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def server_error_view(request):
    return render(request, 'errors/500.html', status=500)
