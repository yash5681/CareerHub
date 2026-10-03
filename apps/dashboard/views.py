from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from apps.accounts.models import User, JobSeekerProfile
from apps.jobs.models import Job, JobCategory, SavedJob
from apps.companies.models import Company
from apps.applications.models import JobApplication
from apps.interviews.models import Interview
from apps.payments.models import Payment, SubscriptionPlan
from apps.reports.models import JobReport, CompanyReport
from apps.notifications.models import Notification
from apps.accounts.decorators import job_seeker_required, recruiter_required, admin_required

@login_required
def index_view(request):
    """Router that dispatches user to their respective role dashboard."""
    if request.user.is_admin_user:
        return redirect('dashboard:admin_overview')
    elif request.user.is_recruiter:
        return redirect('dashboard:recruiter')
    return redirect('dashboard:seeker')


@login_required
@job_seeker_required
def seeker_dashboard_view(request):
    """Job seeker analytics and control center."""
    profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    profile.calculate_completion()

    applications = JobApplication.objects.filter(applicant=request.user)
    total_apps = applications.count()
    shortlisted_apps = applications.filter(status=JobApplication.Status.SHORTLISTED).count()
    interview_apps = applications.filter(status=JobApplication.Status.INTERVIEW_SCHEDULED).count()
    saved_count = SavedJob.objects.filter(user=request.user).count()

    today = timezone.now().date()
    upcoming_interviews = Interview.objects.filter(
        candidate=request.user,
        interview_date__gte=today,
        status=Interview.Status.SCHEDULED
    ).select_related('job', 'job__company')[:3]

    recent_notifications = Notification.objects.filter(recipient=request.user)[:5]
    recent_applications = applications.select_related('job', 'job__company')[:5]

    return render(request, 'dashboard/seeker_dashboard.html', {
        'profile': profile,
        'total_apps': total_apps,
        'shortlisted_apps': shortlisted_apps,
        'interview_apps': interview_apps,
        'saved_count': saved_count,
        'upcoming_interviews': upcoming_interviews,
        'recent_notifications': recent_notifications,
        'recent_applications': recent_applications,
    })


@login_required
@recruiter_required
def recruiter_dashboard_view(request):
    """Recruiter command center for job metrics, candidate pipeline, and hiring."""
    my_jobs = Job.objects.filter(posted_by=request.user)
    total_jobs = my_jobs.count()
    active_jobs = my_jobs.filter(status=Job.Status.PUBLISHED).count()

    my_applications = JobApplication.objects.filter(job__in=my_jobs)
    total_applicants = my_applications.count()
    shortlisted_count = my_applications.filter(status=JobApplication.Status.SHORTLISTED).count()

    today = timezone.now().date()
    upcoming_interviews = Interview.objects.filter(
        recruiter=request.user,
        interview_date__gte=today,
        status=Interview.Status.SCHEDULED
    ).select_related('candidate', 'job')[:5]

    recent_applications = my_applications.select_related('applicant', 'job').order_by('-applied_at')[:8]
    subscription = getattr(request.user, 'subscription', None)

    return render(request, 'dashboard/recruiter_dashboard.html', {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applicants': total_applicants,
        'shortlisted_count': shortlisted_count,
        'upcoming_interviews': upcoming_interviews,
        'recent_applications': recent_applications,
        'subscription': subscription,
    })


@login_required
@admin_required
def admin_overview_view(request):
    """Custom Administrative Portal with system-wide analytics."""
    kpis = {
        'total_users': User.objects.count(),
        'job_seekers': User.objects.filter(role=User.Role.JOB_SEEKER).count(),
        'recruiters': User.objects.filter(role=User.Role.RECRUITER).count(),
        'total_companies': Company.objects.count(),
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(status=Job.Status.PUBLISHED).count(),
        'total_applications': JobApplication.objects.count(),
        'pending_reports': JobReport.objects.filter(status=JobReport.Status.PENDING).count() + CompanyReport.objects.filter(status=CompanyReport.Status.PENDING).count(),
        'total_revenue': Payment.objects.filter(status=Payment.Status.SUCCESS).aggregate(Sum('amount'))['amount__sum'] or 0,
    }

    recent_users = User.objects.all().order_by('-date_joined')[:6]
    recent_jobs = Job.objects.select_related('company').order_by('-created_at')[:6]
    recent_reports = JobReport.objects.select_related('job', 'reported_by').filter(status=JobReport.Status.PENDING)[:5]

    return render(request, 'dashboard/admin_overview.html', {
        'kpis': kpis,
        'recent_users': recent_users,
        'recent_jobs': recent_jobs,
        'recent_reports': recent_reports,
    })


@login_required
@admin_required
def admin_analytics_view(request):
    """Deep analytics breakdown for admin."""
    category_breakdown = JobCategory.objects.annotate(job_count=Count('jobs')).order_by('-job_count')[:10]
    workmode_breakdown = Job.objects.values('work_mode').annotate(count=Count('id'))
    status_breakdown = JobApplication.objects.values('status').annotate(count=Count('id'))

    return render(request, 'dashboard/admin_analytics.html', {
        'category_breakdown': category_breakdown,
        'workmode_breakdown': workmode_breakdown,
        'status_breakdown': status_breakdown,
    })


@login_required
@admin_required
def admin_users_view(request):
    """Admin user management view."""
    users = User.objects.all().order_by('-date_joined')
    role = request.GET.get('role')
    if role:
        users = users.filter(role=role)
    q = request.GET.get('q', '').strip()
    if q:
        users = users.filter(Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))

    return render(request, 'dashboard/admin_users.html', {'users': users})


@login_required
@admin_required
def admin_toggle_user_status_view(request, pk):
    """Activate/Deactivate user account."""
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj.is_superuser:
        messages.error(request, _("Cannot deactivate a superuser account."))
        return redirect('dashboard:admin_users')
    
    user_obj.is_active = not user_obj.is_active
    user_obj.save(update_fields=['is_active'])
    status_str = "activated" if user_obj.is_active else "deactivated"
    messages.success(request, _(f"User {user_obj.email} {status_str} successfully."))
    return redirect('dashboard:admin_users')


@login_required
@admin_required
def admin_jobs_view(request):
    """Admin job postings control."""
    jobs = Job.objects.select_related('company', 'posted_by').order_by('-created_at')
    return render(request, 'dashboard/admin_jobs.html', {'jobs': jobs})


@login_required
@admin_required
def admin_toggle_job_featured_view(request, pk):
    """Feature or unfeature a job posting."""
    job = get_object_or_404(Job, pk=pk)
    job.is_featured = not job.is_featured
    job.save(update_fields=['is_featured'])
    state = "promoted to Featured" if job.is_featured else "unfeatured"
    messages.success(request, _(f"Job '{job.title}' {state}."))
    return redirect('dashboard:admin_jobs')


@login_required
@admin_required
def admin_companies_view(request):
    """Admin employer verification panel."""
    companies = Company.objects.all().order_by('-created_at')
    return render(request, 'dashboard/admin_companies.html', {'companies': companies})


@login_required
@admin_required
def admin_toggle_company_verified_view(request, pk):
    """Toggle employer verified trust badge."""
    comp = get_object_or_404(Company, pk=pk)
    comp.is_verified = not comp.is_verified
    comp.save(update_fields=['is_verified'])
    badge_state = "granted Verified status" if comp.is_verified else "revoked Verified status"
    messages.success(request, _(f"Company {comp.name} {badge_state}."))
    return redirect('dashboard:admin_companies')


@login_required
@admin_required
def admin_applications_view(request):
    """Admin application monitor."""
    applications = JobApplication.objects.select_related('job', 'job__company', 'applicant').order_by('-applied_at')[:50]
    return render(request, 'dashboard/admin_applications.html', {'applications': applications})


@login_required
@admin_required
def admin_reports_view(request):
    """Admin grievance and report moderation queue."""
    job_reports = JobReport.objects.select_related('job', 'reported_by').all()
    company_reports = CompanyReport.objects.select_related('company', 'reported_by').all()
    return render(request, 'dashboard/admin_reports.html', {
        'job_reports': job_reports,
        'company_reports': company_reports,
    })


@login_required
@admin_required
def admin_resolve_report_view(request, report_type, pk, action):
    """Resolve or dismiss report."""
    if report_type == 'job':
        report = get_object_or_404(JobReport, pk=pk)
    else:
        report = get_object_or_404(CompanyReport, pk=pk)

    if action == 'resolve':
        report.status = JobReport.Status.RESOLVED
        messages.success(request, _("Report marked as resolved."))
    else:
        report.status = JobReport.Status.DISMISSED
        messages.info(request, _("Report dismissed."))

    report.save(update_fields=['status'])
    return redirect('dashboard:admin_reports')


@login_required
@admin_required
def admin_categories_view(request):
    """Manage job categories & taxonomy."""
    categories = JobCategory.objects.all().order_by('order', 'name')
    return render(request, 'dashboard/admin_categories.html', {'categories': categories})


@login_required
@admin_required
def admin_payments_view(request):
    """Admin payments and transaction history."""
    payments = Payment.objects.select_related('user', 'plan').order_by('-created_at')
    return render(request, 'dashboard/admin_payments.html', {'payments': payments})
