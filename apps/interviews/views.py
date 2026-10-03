from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from apps.applications.models import JobApplication, ApplicationStatusHistory
from apps.interviews.models import Interview
from apps.interviews.forms import InterviewScheduleForm
from apps.notifications.models import Notification
from apps.accounts.decorators import recruiter_required, job_seeker_required

@login_required
@recruiter_required
def schedule_interview_view(request, application_id):
    """Recruiter schedules interview round for candidate."""
    application = get_object_or_404(
        JobApplication.objects.select_related('job', 'applicant'),
        pk=application_id,
        job__posted_by=request.user
    )

    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.job = application.job
            interview.candidate = application.applicant
            interview.recruiter = request.user
            interview.status = Interview.Status.SCHEDULED
            interview.save()

            # Update application status
            prev_status = application.status
            application.status = JobApplication.Status.INTERVIEW_SCHEDULED
            application.save(update_fields=['status'])

            ApplicationStatusHistory.objects.create(
                application=application,
                previous_status=prev_status,
                new_status=JobApplication.Status.INTERVIEW_SCHEDULED,
                changed_by=request.user,
                comment=f"Interview scheduled for {interview.interview_date} at {interview.interview_time.strftime('%I:%M %p')}"
            )

            # Notify Candidate
            Notification.send(
                recipient=application.applicant,
                title=_("Interview Scheduled!"),
                message=_(f"An interview for '{application.job.title}' is scheduled on {interview.interview_date} at {interview.interview_time.strftime('%I:%M %p')}."),
                notification_type=Notification.NotificationType.INTERVIEW_SCHEDULED,
                link_url="/interviews/my/"
            )

            messages.success(request, _(f"Interview for {application.applicant.get_full_name()} scheduled successfully!"))
            return redirect('applications:recruiter_detail', pk=application.pk)
    else:
        form = InterviewScheduleForm()

    return render(request, 'interviews/schedule_interview.html', {
        'application': application,
        'form': form,
    })


@login_required
@recruiter_required
def recruiter_interviews_list_view(request):
    """Recruiter calendar of interviews."""
    today = timezone.now().date()
    interviews = Interview.objects.filter(recruiter=request.user).select_related(
        'candidate', 'job', 'application'
    )
    upcoming = interviews.filter(interview_date__gte=today, status=Interview.Status.SCHEDULED).order_by('interview_date', 'interview_time')
    past = interviews.filter(interview_date__lt=today).order_by('-interview_date')

    return render(request, 'interviews/recruiter_interviews.html', {
        'upcoming_interviews': upcoming,
        'past_interviews': past,
    })


@login_required
@job_seeker_required
def seeker_interviews_list_view(request):
    """Job seeker interview invitations and schedule."""
    today = timezone.now().date()
    interviews = Interview.objects.filter(candidate=request.user).select_related(
        'recruiter', 'job', 'job__company'
    )
    upcoming = interviews.filter(interview_date__gte=today, status=Interview.Status.SCHEDULED).order_by('interview_date', 'interview_time')
    past = interviews.filter(interview_date__lt=today).order_by('-interview_date')

    return render(request, 'interviews/seeker_interviews.html', {
        'upcoming_interviews': upcoming,
        'past_interviews': past,
    })
