from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.jobs.models import Job, JobCategory, Skill, SavedJob, JobAlert, Location
from apps.jobs.forms import JobPostForm, JobAlertForm
from apps.applications.models import JobApplication
from apps.accounts.decorators import recruiter_required, job_seeker_required

def job_list_view(request):
    """Main job search and discovery engine with advanced filtering and pagination."""
    queryset = Job.objects.filter(status=Job.Status.PUBLISHED).select_related('company', 'category').prefetch_related('skills')

    # Keyword Search (title, description, company, skills)
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(company__name__icontains=q) |
            Q(skills__name__icontains=q)
        ).distinct()

    # Location Filter (City or State)
    location = request.GET.get('location', '').strip()
    if location:
        queryset = queryset.filter(
            Q(location_city__icontains=location) |
            Q(location_state__icontains=location)
        )

    # Category Filter
    category_slug = request.GET.get('category', '').strip()
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    # Job Type Filter
    job_type = request.GET.get('job_type', '').strip()
    if job_type:
        queryset = queryset.filter(job_type=job_type)

    # Work Mode Filter
    work_mode = request.GET.get('work_mode', '').strip()
    if work_mode:
        queryset = queryset.filter(work_mode=work_mode)

    # Fresher Friendly Filter
    fresher = request.GET.get('fresher')
    if fresher == '1':
        queryset = queryset.filter(is_fresher_friendly=True)

    # Experience Filter
    exp = request.GET.get('experience')
    if exp:
        try:
            exp_val = float(exp)
            queryset = queryset.filter(experience_min__lte=exp_val, experience_max__gte=exp_val)
        except ValueError:
            pass

    # Salary Filter
    min_sal = request.GET.get('min_salary')
    if min_sal:
        try:
            queryset = queryset.filter(salary_max__gte=float(min_sal))
        except ValueError:
            pass

    # Sorting
    sort_by = request.GET.get('sort', 'latest')
    if sort_by == 'salary_high':
        queryset = queryset.order_by('-is_featured', '-salary_max', '-created_at')
    elif sort_by == 'experience':
        queryset = queryset.order_by('-is_featured', 'experience_min')
    else:  # default 'latest'
        queryset = queryset.order_by('-is_featured', '-created_at')

    # Pagination: 10 jobs per page
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get user's saved job IDs if authenticated
    user_saved_job_ids = set()
    if request.user.is_authenticated:
        user_saved_job_ids = set(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))

    categories = JobCategory.objects.all()
    job_types = Job.JobType.choices
    work_modes = Job.WorkMode.choices

    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'job_types': job_types,
        'work_modes': work_modes,
        'user_saved_job_ids': user_saved_job_ids,
        'selected_category': category_slug,
        'selected_job_type': job_type,
        'selected_work_mode': work_mode,
        'search_query': q,
        'search_location': location,
        'sort_by': sort_by,
        'total_jobs_count': paginator.count,
    })


def job_detail_view(request, slug):
    """Job detail page with company info, similar jobs, and application status."""
    job = get_object_or_404(
        Job.objects.select_related('company', 'category').prefetch_related('skills'),
        slug=slug
    )

    # Increment view counter atomically
    Job.objects.filter(pk=job.pk).update(views_count=F('views_count') + 1)

    has_applied = False
    is_saved = False
    user_application = None

    if request.user.is_authenticated:
        user_application = JobApplication.objects.filter(job=job, applicant=request.user).first()
        has_applied = user_application is not None
        is_saved = SavedJob.objects.filter(job=job, user=request.user).exists()

    # Similar jobs in same category
    similar_jobs = Job.objects.filter(
        category=job.category,
        status=Job.Status.PUBLISHED
    ).exclude(pk=job.pk).select_related('company')[:4]

    # More jobs from this company
    company_jobs = Job.objects.filter(
        company=job.company,
        status=Job.Status.PUBLISHED
    ).exclude(pk=job.pk)[:3]

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'has_applied': has_applied,
        'is_saved': is_saved,
        'user_application': user_application,
        'similar_jobs': similar_jobs,
        'company_jobs': company_jobs,
    })


@login_required
@recruiter_required
def job_create_view(request):
    """Recruiter post a new job."""
    recruiter_profile = getattr(request.user, 'recruiter_profile', None)
    if not recruiter_profile or not recruiter_profile.company:
        messages.warning(request, _("Please configure your company profile before posting a job."))
        return redirect('companies:my_company')

    # Check recruiter subscription limits
    subscription = getattr(request.user, 'subscription', None)
    if subscription and not subscription.can_post_job:
        messages.error(request, _("You have reached your active job posting limit. Please upgrade your plan."))
        return redirect('payments:pricing')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = recruiter_profile.company
            job.posted_by = request.user
            job.save()

            # Process comma-separated skills
            skills_csv = form.cleaned_data.get('skills_csv', '')
            if skills_csv:
                skill_names = [s.strip() for s in skills_csv.split(',') if s.strip()]
                for s_name in skill_names:
                    skill, created = Skill.objects.get_or_create(name__iexact=s_name, defaults={'name': s_name})
                    job.skills.add(skill)

            if subscription:
                subscription.jobs_posted_this_cycle += 1
                subscription.save(update_fields=['jobs_posted_this_cycle'])

            messages.success(request, _(f"Job posting '{job.title}' published successfully!"))
            return redirect('jobs:detail', slug=job.slug)
    else:
        form = JobPostForm(initial={'location_city': recruiter_profile.company.city, 'location_state': recruiter_profile.company.state})

    return render(request, 'jobs/job_create.html', {'form': form, 'company': recruiter_profile.company})


@login_required
@recruiter_required
def job_edit_view(request, slug):
    """Edit existing job posting."""
    job = get_object_or_404(Job, slug=slug, posted_by=request.user)
    
    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()
            skills_csv = form.cleaned_data.get('skills_csv', '')
            if skills_csv:
                job.skills.clear()
                skill_names = [s.strip() for s in skills_csv.split(',') if s.strip()]
                for s_name in skill_names:
                    skill, created = Skill.objects.get_or_create(name__iexact=s_name, defaults={'name': s_name})
                    job.skills.add(skill)

            messages.success(request, _("Job posting updated successfully!"))
            return redirect('jobs:detail', slug=job.slug)
    else:
        existing_skills = ", ".join(job.skills.values_list('name', flat=True))
        form = JobPostForm(instance=job, initial={'skills_csv': existing_skills})

    return render(request, 'jobs/job_edit.html', {'form': form, 'job': job})


@login_required
@recruiter_required
def manage_jobs_view(request):
    """Recruiter dashboard table of posted jobs."""
    jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    return render(request, 'jobs/manage_jobs.html', {'jobs': jobs})


@login_required
def toggle_save_job_view(request, job_id):
    """AJAX endpoint to bookmark or unbookmark a job."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    job = get_object_or_404(Job, pk=job_id)
    saved_record = SavedJob.objects.filter(user=request.user, job=job).first()

    if saved_record:
        saved_record.delete()
        Job.objects.filter(pk=job.pk).update(saves_count=F('saves_count') - 1)
        return JsonResponse({'status': 'removed', 'message': _("Job removed from bookmarks.")})
    else:
        SavedJob.objects.create(user=request.user, job=job)
        Job.objects.filter(pk=job.pk).update(saves_count=F('saves_count') + 1)
        return JsonResponse({'status': 'saved', 'message': _("Job saved to your bookmarks!")})


@login_required
@job_seeker_required
def saved_jobs_view(request):
    """Seeker list of bookmarked jobs."""
    saved_items = SavedJob.objects.filter(user=request.user).select_related('job', 'job__company').order_by('-created_at')
    return render(request, 'jobs/saved_jobs.html', {'saved_items': saved_items})


@login_required
@job_seeker_required
def job_alerts_view(request):
    """Seeker manage job alerts."""
    form = JobAlertForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        alert = form.save(commit=False)
        alert.user = request.user
        alert.save()
        messages.success(request, _("Job alert configured successfully!"))
        return redirect('jobs:alerts')

    alerts = JobAlert.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'jobs/job_alerts.html', {'form': form, 'alerts': alerts})


@login_required
@job_seeker_required
def delete_job_alert_view(request, pk):
    alert = get_object_or_404(JobAlert, pk=pk, user=request.user)
    alert.delete()
    messages.success(request, _("Job alert removed."))
    return redirect('jobs:alerts')


@login_required
@job_seeker_required
def recommended_jobs_view(request):
    """Recommendation engine based on seeker's skills, category, and preferred location."""
    profile = getattr(request.user, 'job_seeker_profile', None)
    matching_jobs = Job.objects.filter(status=Job.Status.PUBLISHED).select_related('company', 'category')

    if profile:
        seeker_skills = profile.get_skills_list()
        pref_location = profile.preferred_location or profile.city

        filters = Q()
        if seeker_skills:
            for s in seeker_skills:
                filters |= Q(skills__name__icontains=s) | Q(title__icontains=s)
        if pref_location:
            filters |= Q(location_city__icontains=pref_location) | Q(work_mode=Job.WorkMode.REMOTE)

        if filters:
            matching_jobs = matching_jobs.filter(filters).distinct()

    paginator = Paginator(matching_jobs[:30], 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    user_saved_job_ids = set(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))

    return render(request, 'jobs/recommended_jobs.html', {
        'page_obj': page_obj,
        'user_saved_job_ids': user_saved_job_ids,
    })


def categories_list_view(request):
    """Directory of all job categories."""
    categories = JobCategory.objects.all().order_by('order', 'name')
    return render(request, 'jobs/categories_list.html', {'categories': categories})
