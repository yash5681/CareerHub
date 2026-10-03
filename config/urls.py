from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Internationalization switcher
    path('i18n/', include('django.conf.urls.i18n')),

    # Standard Django Admin
    path('django-admin/', admin.site.urls),

    # Core Public Pages & Static content (Home, About, Contact, Terms, Privacy, FAQ)
    path('', include('apps.core.urls', namespace='core')),

    # Authentication & Profiles
    path('auth/', include('apps.accounts.urls', namespace='accounts')),

    # Jobs & Search
    path('jobs/', include('apps.jobs.urls', namespace='jobs')),

    # Companies
    path('companies/', include('apps.companies.urls', namespace='companies')),

    # Applications
    path('applications/', include('apps.applications.urls', namespace='applications')),

    # Resumes & Builder
    path('resumes/', include('apps.resumes.urls', namespace='resumes')),

    # Interviews
    path('interviews/', include('apps.interviews.urls', namespace='interviews')),

    # Direct Messaging
    path('messages/', include('apps.messaging.urls', namespace='messaging')),

    # Activity Notifications
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),

    # Razorpay Payments & Subscriptions
    path('payments/', include('apps.payments.urls', namespace='payments')),

    # Reviews
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),

    # Moderation & Reports
    path('reports/', include('apps.reports.urls', namespace='reports')),

    # Career Blog
    path('blog/', include('apps.blog.urls', namespace='blog')),

    # Dashboards (Seeker, Recruiter, Custom Admin)
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Error Handlers
handler400 = 'apps.core.views.bad_request_view'
handler403 = 'apps.core.views.permission_denied_view'
handler404 = 'apps.core.views.page_not_found_view'
handler500 = 'apps.core.views.server_error_view'
