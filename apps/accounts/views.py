from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils import timezone
from apps.accounts.models import (
    User, JobSeekerProfile, RecruiterProfile, Education,
    Experience, Project, Certification, Language
)
from apps.companies.models import Company
from apps.notifications.models import Notification
from apps.payments.models import SubscriptionPlan, RecruiterSubscription
from apps.accounts.forms import (
    JobSeekerRegistrationForm, RecruiterRegistrationForm,
    LoginForm, JobSeekerProfileForm, EducationForm,
    ExperienceForm, ProjectForm, CertificationForm, LanguageForm
)
from apps.accounts.decorators import job_seeker_required, recruiter_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        remember_me = form.cleaned_data.get('remember_me')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            
            messages.success(request, _(f"Welcome back, {user.first_name or user.username}!"))
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:index')
        else:
            messages.error(request, _("Invalid email or password. Please verify your credentials."))

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, _("You have been signed out safely. Come back soon!"))
    return redirect('core:home')


def register_seeker_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = JobSeekerRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = User.Role.JOB_SEEKER
        user.set_password(form.cleaned_data['password'])
        user.is_verified = True
        user.save()

        # Create Seeker Profile
        profile = JobSeekerProfile.objects.create(
            user=user,
            city=form.cleaned_data.get('city', ''),
            state=form.cleaned_data.get('state', '')
        )
        profile.calculate_completion()

        # Send welcome notification
        Notification.send(
            recipient=user,
            title=_("Welcome to CareerHub!"),
            message=_("Your account is ready. Complete your profile and start applying to top Indian tech opportunities!"),
            notification_type=Notification.NotificationType.SYSTEM,
            link_url='/auth/profile/edit/'
        )

        login(request, user)
        messages.success(request, _("Welcome to CareerHub! Your job seeker account has been created."))
        return redirect('accounts:seeker_profile')

    return render(request, 'accounts/register_seeker.html', {'form': form})


def register_recruiter_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = RecruiterRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = User.Role.RECRUITER
        user.set_password(form.cleaned_data['password'])
        user.is_verified = True
        user.save()

        # Find or create company
        company_name = form.cleaned_data['company_name']
        company, created = Company.objects.get_or_create(
            name=company_name,
            defaults={
                'industry': form.cleaned_data['industry'],
                'company_size': form.cleaned_data['company_size'],
                'city': form.cleaned_data['city'],
                'state': form.cleaned_data['state'],
                'email': user.email,
                'phone': user.phone,
                'about': _(f"{company_name} is hiring passionate professionals across India.")
            }
        )

        # Create Recruiter Profile
        RecruiterProfile.objects.create(
            user=user,
            company=company,
            designation=form.cleaned_data['designation'],
            is_company_admin=True
        )

        # Assign Free Starter Subscription Plan
        free_plan = SubscriptionPlan.objects.filter(price=0).first()
        if not free_plan:
            free_plan = SubscriptionPlan.objects.create(
                name='Free Starter',
                price=0,
                job_posting_limit=2,
                featured_job_limit=0,
                candidate_contacts_limit=10,
                description='Basic recruiting features for growing teams.',
                features_list='2 Active Job Postings\nAccess to Candidate Applications\nDirect In-App Messaging\nStandard Email Support'
            )
        
        RecruiterSubscription.objects.create(
            recruiter=user,
            plan=free_plan,
            active_from=timezone.now(),
            active_until=timezone.now() + timedelta(days=365)
        )

        # Send welcome notification
        Notification.send(
            recipient=user,
            title=_("Employer Account Activated"),
            message=_(f"Welcome to CareerHub Employer portal! You can now publish jobs on behalf of {company.name}."),
            notification_type=Notification.NotificationType.SYSTEM,
            link_url='/jobs/create/'
        )

        login(request, user)
        messages.success(request, _(f"Employer profile created successfully for {company.name}!"))
        return redirect('dashboard:recruiter')

    return render(request, 'accounts/register_recruiter.html', {'form': form})


@login_required
@job_seeker_required
def seeker_profile_view(request):
    profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    profile.calculate_completion()
    return render(request, 'accounts/seeker_profile.html', {
        'profile': profile,
        'educations': profile.educations.all(),
        'experiences': profile.experiences.all(),
        'projects': profile.projects.all(),
        'certifications': profile.certifications.all(),
        'languages': profile.languages.all(),
    })


@login_required
@job_seeker_required
def edit_seeker_profile_view(request):
    profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update user fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.phone = form.cleaned_data['phone']
            if 'avatar' in request.FILES:
                request.user.avatar = request.FILES['avatar']
            request.user.save()

            form.save()
            profile.calculate_completion()
            messages.success(request, _("Profile details updated successfully!"))
            return redirect('accounts:seeker_profile')
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone': request.user.phone,
        }
        form = JobSeekerProfileForm(instance=profile, initial=initial)

    return render(request, 'accounts/edit_seeker_profile.html', {'form': form, 'profile': profile})


@login_required
@job_seeker_required
def add_education_view(request):
    profile = request.user.job_seeker_profile
    form = EducationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        edu = form.save(commit=False)
        edu.profile = profile
        edu.save()
        profile.calculate_completion()
        messages.success(request, _("Education details added successfully!"))
        return redirect('accounts:seeker_profile')
    return render(request, 'accounts/education_form.html', {'form': form})


@login_required
@job_seeker_required
def delete_education_view(request, pk):
    edu = get_object_or_404(Education, pk=pk, profile__user=request.user)
    edu.delete()
    request.user.job_seeker_profile.calculate_completion()
    messages.success(request, _("Education record deleted."))
    return redirect('accounts:seeker_profile')


@login_required
@job_seeker_required
def add_experience_view(request):
    profile = request.user.job_seeker_profile
    form = ExperienceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        exp = form.save(commit=False)
        exp.profile = profile
        exp.save()
        profile.calculate_completion()
        messages.success(request, _("Work experience added successfully!"))
        return redirect('accounts:seeker_profile')
    return render(request, 'accounts/experience_form.html', {'form': form})


@login_required
@job_seeker_required
def delete_experience_view(request, pk):
    exp = get_object_or_404(Experience, pk=pk, profile__user=request.user)
    exp.delete()
    request.user.job_seeker_profile.calculate_completion()
    messages.success(request, _("Work experience removed."))
    return redirect('accounts:seeker_profile')


@login_required
@job_seeker_required
def add_project_view(request):
    profile = request.user.job_seeker_profile
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        proj = form.save(commit=False)
        proj.profile = profile
        proj.save()
        messages.success(request, _("Project details saved!"))
        return redirect('accounts:seeker_profile')
    return render(request, 'accounts/project_form.html', {'form': form})


@login_required
@job_seeker_required
def delete_project_view(request, pk):
    proj = get_object_or_404(Project, pk=pk, profile__user=request.user)
    proj.delete()
    messages.success(request, _("Project removed."))
    return redirect('accounts:seeker_profile')


@login_required
@job_seeker_required
def add_certification_view(request):
    profile = request.user.job_seeker_profile
    form = CertificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cert = form.save(commit=False)
        cert.profile = profile
        cert.save()
        messages.success(request, _("Certification recorded!"))
        return redirect('accounts:seeker_profile')
    return render(request, 'accounts/certification_form.html', {'form': form})


@login_required
@job_seeker_required
def delete_certification_view(request, pk):
    cert = get_object_or_404(Certification, pk=pk, profile__user=request.user)
    cert.delete()
    messages.success(request, _("Certification removed."))
    return redirect('accounts:seeker_profile')


@login_required
def account_settings_view(request):
    pass_form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and 'change_password' in request.POST:
        if pass_form.is_valid():
            user = pass_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _("Your password was updated successfully!"))
            return redirect('accounts:settings')
        else:
            messages.error(request, _("Please correct the errors in the password form."))

    return render(request, 'accounts/settings.html', {'pass_form': pass_form})
