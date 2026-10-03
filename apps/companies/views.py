from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.companies.models import Company, CompanyReview
from apps.companies.forms import CompanyForm, CompanyReviewForm
from apps.jobs.models import Job
from apps.accounts.decorators import recruiter_required, job_seeker_required

def company_list_view(request):
    """Directory of companies hiring on CareerHub."""
    companies = Company.objects.all().order_by('-is_featured', 'name')

    q = request.GET.get('q', '').strip()
    if q:
        companies = companies.filter(Q(name__icontains=q) | Q(industry__icontains=q) | Q(city__icontains=q))

    industry = request.GET.get('industry', '').strip()
    if industry:
        companies = companies.filter(industry__icontains=industry)

    city = request.GET.get('city', '').strip()
    if city:
        companies = companies.filter(city__icontains=city)

    paginator = Paginator(companies, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Unique industries and cities for filter dropdowns
    industries = Company.objects.values_list('industry', flat=True).distinct()
    cities = Company.objects.values_list('city', flat=True).distinct()

    return render(request, 'companies/company_list.html', {
        'page_obj': page_obj,
        'industries': industries,
        'cities': cities,
        'search_query': q,
        'selected_industry': industry,
        'selected_city': city,
    })


def company_detail_view(request, slug):
    """Company profile with active jobs, culture, and employee reviews."""
    company = get_object_or_404(Company, slug=slug)
    open_jobs = Job.objects.filter(company=company, status=Job.Status.PUBLISHED).order_by('-created_at')
    reviews = company.reviews.filter(is_approved=True).select_related('user')

    review_form = None
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        if not user_review and request.user.is_job_seeker:
            review_form = CompanyReviewForm()

    return render(request, 'companies/company_detail.html', {
        'company': company,
        'open_jobs': open_jobs,
        'reviews': reviews,
        'review_form': review_form,
        'user_review': user_review,
    })


@login_required
@job_seeker_required
def add_company_review_view(request, slug):
    """Job seeker submits company review."""
    company = get_object_or_404(Company, slug=slug)
    if company.reviews.filter(user=request.user).exists():
        messages.warning(request, _("You have already reviewed this company."))
        return redirect('companies:detail', slug=company.slug)

    if request.method == 'POST':
        form = CompanyReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.company = company
            review.user = request.user
            review.is_approved = True
            review.save()
            messages.success(request, _("Thank you! Your company review has been published."))
            return redirect('companies:detail', slug=company.slug)
    return redirect('companies:detail', slug=company.slug)


@login_required
@recruiter_required
def my_company_view(request):
    """Recruiter edit and maintain company profile."""
    recruiter_profile = request.user.recruiter_profile
    company = recruiter_profile.company

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            comp_obj = form.save()
            if not company:
                recruiter_profile.company = comp_obj
                recruiter_profile.save(update_fields=['company'])
            messages.success(request, _("Company profile updated successfully!"))
            return redirect('companies:my_company')
    else:
        form = CompanyForm(instance=company)

    return render(request, 'companies/my_company.html', {
        'form': form,
        'company': company,
    })
