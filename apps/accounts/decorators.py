from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _

def job_seeker_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, _("Please log in to access this page."))
            return redirect('accounts:login')
        if not (request.user.is_job_seeker or request.user.is_admin_user):
            messages.error(request, _("This feature is only accessible to Job Seekers."))
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def recruiter_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, _("Please log in to access employer features."))
            return redirect('accounts:login')
        if not (request.user.is_recruiter or request.user.is_admin_user):
            messages.error(request, _("This feature is only accessible to Recruiters / Employers."))
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, _("Admin authentication required."))
            return redirect('accounts:login')
        if not request.user.is_admin_user:
            messages.error(request, _("Access restricted to platform administrators."))
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view
