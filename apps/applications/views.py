from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.db import transaction
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.jobs.models import Job
from apps.applications.models import JobApplication, ApplicationStatusHistory
from apps.applications.forms import JobApplicationForm, RecruiterStatusUpdateForm
from apps.resumes.models import Resume
from apps.notifications.models import Notification
from apps.accounts.decorators import job_seeker_required, recruiter_required

@login_required
@job_seeker_required
def apply_job_view(request, slug):
    """Job seeker submits application with resume and cover letter."""
    job = get_object_or_404(Job, slug=slug, status=Job.Status.PUBLISHED)

    # Check for existing application
    existing_app = JobApplication.objects.filter(job=job, applicant=request.user).first()
    if existing_app:
        messages.info(request, _(f"You have already applied to '{job.title}'. Current status: {existing_app.get_status_display()}."))
        return redirect('jobs:detail', slug=job.slug)

    # Check if candidate has at least one resume
    if not Resume.objects.filter(user=request.user).exists():
        messages.warning(request, _("Please upload or build a resume before applying to jobs."))
        return redirect('resumes:my_resumes')

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                application = form.save(commit=False)
                application.job = job
                application.applicant = request.user
                application.status = JobApplication.Status.APPLIED
                application.save()

                # Log status history
                ApplicationStatusHistory.objects.create(
                    application=application,
                    previous_status=JobApplication.Status.APPLIED,
                    new_status=JobApplication.Status.APPLIED,
                    changed_by=request.user,
                    comment=_("Application submitted by candidate.")
                )

                # Increment job applications counter
                Job.objects.filter(pk=job.pk).update(applications_count=F('applications_count') + 1)

                # Send notifications
                Notification.send(
                    recipient=job.posted_by,
                    title=_("New Applicant Received"),
                    message=_(f"{request.user.get_full_name()} applied for '{job.title}'."),
                    notification_type=Notification.NotificationType.APPLICATION_SUBMITTED,
                    link_url=f"/applications/recruiter/{application.pk}/"
                )

                Notification.send(
                    recipient=request.user,
                    title=_("Application Submitted"),
                    message=_(f"Your application for '{job.title}' at {job.company.name} was successfully submitted."),
                    notification_type=Notification.NotificationType.APPLICATION_SUBMITTED,
                    link_url="/applications/my/"
                )

            messages.success(request, _(f"Application for '{job.title}' submitted successfully!"))
            return redirect('applications:seeker_list')
    else:
        form = JobApplicationForm(user=request.user)

    return render(request, 'applications/apply_job.html', {'job': job, 'form': form})


@login_required
@job_seeker_required
def seeker_applications_list_view(request):
    """Job seeker views their applications with real-time status tracker."""
    applications = JobApplication.objects.filter(applicant=request.user).select_related(
        'job', 'job__company', 'resume'
    ).order_by('-applied_at')

    return render(request, 'applications/seeker_applications.html', {'applications': applications})


@login_required
@job_seeker_required
def seeker_withdraw_application_view(request, pk):
    """Candidate withdraws application."""
    application = get_object_or_404(JobApplication, pk=pk, applicant=request.user)
    if application.status in [JobApplication.Status.SELECTED, JobApplication.Status.REJECTED]:
        messages.error(request, _("Cannot withdraw an application that has already concluded."))
        return redirect('applications:seeker_list')

    prev_status = application.status
    application.status = JobApplication.Status.WITHDRAWN
    application.save(update_fields=['status'])

    ApplicationStatusHistory.objects.create(
        application=application,
        previous_status=prev_status,
        new_status=JobApplication.Status.WITHDRAWN,
        changed_by=request.user,
        comment=_("Withdrawn by candidate.")
    )

    messages.info(request, _("Application withdrawn."))
    return redirect('applications:seeker_list')


@login_required
@recruiter_required
def recruiter_applications_list_view(request):
    """Recruiter applicant pipeline and filter dashboard."""
    recruiter_jobs = Job.objects.filter(posted_by=request.user)
    job_id = request.GET.get('job_id')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('q', '').strip()

    applications = JobApplication.objects.filter(job__in=recruiter_jobs).select_related(
        'applicant', 'applicant__job_seeker_profile', 'job', 'resume'
    )

    if job_id:
        applications = applications.filter(job_id=job_id)
    if status_filter:
        applications = applications.filter(status=status_filter)
    if search_query:
        applications = applications.filter(
            Q(applicant__first_name__icontains=search_query) |
            Q(applicant__last_name__icontains=search_query) |
            Q(applicant__email__icontains=search_query) |
            Q(applicant__job_seeker_profile__skills_csv__icontains=search_query)
        )

    # Pipeline counts for tabs
    counts = {
        'all': JobApplication.objects.filter(job__in=recruiter_jobs).count(),
        'applied': JobApplication.objects.filter(job__in=recruiter_jobs, status=JobApplication.Status.APPLIED).count(),
        'under_review': JobApplication.objects.filter(job__in=recruiter_jobs, status=JobApplication.Status.UNDER_REVIEW).count(),
        'shortlisted': JobApplication.objects.filter(job__in=recruiter_jobs, status=JobApplication.Status.SHORTLISTED).count(),
        'interview_scheduled': JobApplication.objects.filter(job__in=recruiter_jobs, status=JobApplication.Status.INTERVIEW_SCHEDULED).count(),
        'selected': JobApplication.objects.filter(job__in=recruiter_jobs, status=JobApplication.Status.SELECTED).count(),
        'rejected': JobApplication.objects.filter(job__in=recruiter_jobs, status=JobApplication.Status.REJECTED).count(),
    }

    return render(request, 'applications/recruiter_applications.html', {
        'applications': applications,
        'recruiter_jobs': recruiter_jobs,
        'selected_job_id': job_id,
        'selected_status': status_filter,
        'search_query': search_query,
        'counts': counts,
        'statuses': JobApplication.Status.choices,
    })


@login_required
@recruiter_required
def recruiter_application_detail_view(request, pk):
    """Detailed candidate profile, resume review, and status update workflow."""
    application = get_object_or_404(
        JobApplication.objects.select_related('job', 'applicant', 'resume'),
        pk=pk,
        job__posted_by=request.user
    )

    profile = getattr(application.applicant, 'job_seeker_profile', None)

    if request.method == 'POST':
        form = RecruiterStatusUpdateForm(request.POST, instance=application)
        if form.is_valid():
            prev_status = application.status
            new_status = form.cleaned_data['status']
            comment = form.cleaned_data.get('comment', '')

            with transaction.atomic():
                app_obj = form.save()

                if prev_status != new_status:
                    ApplicationStatusHistory.objects.create(
                        application=app_obj,
                        previous_status=prev_status,
                        new_status=new_status,
                        changed_by=request.user,
                        comment=comment or f"Moved from {prev_status} to {new_status}"
                    )

                    # Notify applicant of status change
                    Notification.send(
                        recipient=application.applicant,
                        title=_("Application Status Updated"),
                        message=_(f"Your application for '{application.job.title}' at {application.job.company.name} is now: {app_obj.get_status_display()}."),
                        notification_type=Notification.NotificationType.APPLICATION_STATUS,
                        link_url="/applications/my/"
                    )

            messages.success(request, _(f"Status updated to '{application.get_status_display()}'."))
            return redirect('applications:recruiter_detail', pk=application.pk)
    else:
        form = RecruiterStatusUpdateForm(instance=application)

    history = application.status_history.select_related('changed_by').all()

    return render(request, 'applications/recruiter_application_detail.html', {
        'application': application,
        'profile': profile,
        'form': form,
        'history': history,
    })


@login_required
@recruiter_required
def recruiter_quick_status_view(request, pk, new_status):
    """One-click shortlist/reject from applicant table."""
    application = get_object_or_404(JobApplication, pk=pk, job__posted_by=request.user)
    
    valid_statuses = dict(JobApplication.Status.choices)
    if new_status in valid_statuses:
        prev_status = application.status
        application.status = new_status
        application.save(update_fields=['status'])

        ApplicationStatusHistory.objects.create(
            application=application,
            previous_status=prev_status,
            new_status=new_status,
            changed_by=request.user,
            comment=f"Quick action: updated to {new_status}"
        )

        Notification.send(
            recipient=application.applicant,
            title=_("Application Status Updated"),
            message=_(f"Your application for '{application.job.title}' is now: {application.get_status_display()}."),
            notification_type=Notification.NotificationType.APPLICATION_STATUS,
            link_url="/applications/my/"
        )

        messages.success(request, _(f"Candidate status moved to {application.get_status_display()}."))

    return redirect('applications:recruiter_list')
