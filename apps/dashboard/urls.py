from django.urls import path
from apps.dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('seeker/', views.seeker_dashboard_view, name='seeker'),
    path('recruiter/', views.recruiter_dashboard_view, name='recruiter'),
    
    # Custom Admin Management Routes
    path('admin/', views.admin_overview_view, name='admin_overview'),
    path('admin/analytics/', views.admin_analytics_view, name='admin_analytics'),
    path('admin/users/', views.admin_users_view, name='admin_users'),
    path('admin/users/<int:pk>/toggle/', views.admin_toggle_user_status_view, name='admin_toggle_user'),
    path('admin/jobs/', views.admin_jobs_view, name='admin_jobs'),
    path('admin/jobs/<int:pk>/toggle-featured/', views.admin_toggle_job_featured_view, name='admin_toggle_featured'),
    path('admin/companies/', views.admin_companies_view, name='admin_companies'),
    path('admin/companies/<int:pk>/toggle-verified/', views.admin_toggle_company_verified_view, name='admin_toggle_verified'),
    path('admin/applications/', views.admin_applications_view, name='admin_applications'),
    path('admin/reports/', views.admin_reports_view, name='admin_reports'),
    path('admin/reports/<str:report_type>/<int:pk>/<str:action>/', views.admin_resolve_report_view, name='admin_resolve_report'),
    path('admin/categories/', views.admin_categories_view, name='admin_categories'),
    path('admin/payments/', views.admin_payments_view, name='admin_payments'),
]
