from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.jobs.models import Job
from apps.companies.models import Company
from apps.reports.models import JobReport, CompanyReport
from apps.reports.forms import JobReportForm, CompanyReportForm

@login_required
def report_job_view(request, slug):
    """File a grievance or fraud report on a suspicious job posting."""
    job = get_object_or_404(Job, slug=slug)

    if request.method == 'POST':
        form = JobReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.job = job
            report.reported_by = request.user
            report.save()
            messages.success(request, _("Your report has been submitted to CareerHub Trust & Safety team."))
            return redirect('jobs:detail', slug=job.slug)
    else:
        form = JobReportForm()

    return render(request, 'reports/report_job.html', {'job': job, 'form': form})


@login_required
def report_company_view(request, slug):
    """File a report on an employer or company profile."""
    company = get_object_or_404(Company, slug=slug)

    if request.method == 'POST':
        form = CompanyReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.company = company
            report.reported_by = request.user
            report.save()
            messages.success(request, _("Your grievance report has been submitted for administrative review."))
            return redirect('companies:detail', slug=company.slug)
    else:
        form = CompanyReportForm()

    return render(request, 'reports/report_company.html', {'company': company, 'form': form})
