from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from apps.resumes.models import Resume
from apps.resumes.forms import ResumeUploadForm, ResumeBuilderForm
from apps.accounts.models import JobSeekerProfile
from apps.accounts.decorators import job_seeker_required

@login_required
@job_seeker_required
def resume_list_view(request):
    """View and manage all user resumes (uploaded & builder)."""
    resumes = Resume.objects.filter(user=request.user).order_by('-is_primary', '-created_at')
    upload_form = ResumeUploadForm()
    return render(request, 'resumes/resume_list.html', {
        'resumes': resumes,
        'upload_form': upload_form,
    })


@login_required
@job_seeker_required
def resume_upload_view(request):
    """Process file upload for resume."""
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.resume_type = Resume.ResumeType.UPLOADED
            resume.save()
            messages.success(request, _(f"Resume '{resume.title}' uploaded successfully!"))
            return redirect('resumes:my_resumes')
        else:
            resumes = Resume.objects.filter(user=request.user).order_by('-is_primary', '-created_at')
            return render(request, 'resumes/resume_list.html', {
                'resumes': resumes,
                'upload_form': form,
            })
    return redirect('resumes:my_resumes')


@login_required
@job_seeker_required
def resume_builder_view(request):
    """Generate and customize a clean, ATS-compliant resume from user profile."""
    profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ResumeBuilderForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.resume_type = Resume.ResumeType.BUILDER
            resume.save()
            messages.success(request, _(f"Resume '{resume.title}' generated successfully!"))
            return redirect('resumes:preview', pk=resume.pk)
    else:
        form = ResumeBuilderForm(initial={'title': f"{request.user.first_name}'s Professional Resume"})

    return render(request, 'resumes/resume_builder.html', {
        'form': form,
        'profile': profile,
        'educations': profile.educations.all(),
        'experiences': profile.experiences.all(),
        'projects': profile.projects.all(),
        'certifications': profile.certifications.all(),
        'languages': profile.languages.all(),
    })


@login_required
def resume_preview_view(request, pk):
    """Clean printable/downloadable ATS resume preview."""
    resume = get_object_or_404(Resume, pk=pk)

    # Authorization check: only owner, applying recruiter, or admin can preview
    is_owner = (resume.user == request.user)
    is_recruiter = request.user.is_authenticated and (request.user.is_recruiter or request.user.is_admin_user)
    if not (is_owner or is_recruiter):
        messages.error(request, _("Unauthorized access to candidate resume."))
        return redirect('core:home')

    profile = getattr(resume.user, 'job_seeker_profile', None)

    return render(request, 'resumes/resume_preview.html', {
        'resume': resume,
        'profile': profile,
        'candidate': resume.user,
        'educations': profile.educations.all() if profile else [],
        'experiences': profile.experiences.all() if profile else [],
        'projects': profile.projects.all() if profile else [],
        'certifications': profile.certifications.all() if profile else [],
        'languages': profile.languages.all() if profile else [],
        'skills': profile.get_skills_list() if profile else [],
    })


@login_required
@job_seeker_required
def set_primary_resume_view(request, pk):
    """Set resume as default for applications."""
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    resume.is_primary = True
    resume.save()
    messages.success(request, _(f"'{resume.title}' is now your primary application resume."))
    return redirect('resumes:my_resumes')


@login_required
@job_seeker_required
def delete_resume_view(request, pk):
    """Safely delete resume."""
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    resume.delete()
    messages.success(request, _("Resume deleted."))
    return redirect('resumes:my_resumes')
