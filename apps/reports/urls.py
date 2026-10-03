from django.urls import path
from apps.reports import views

app_name = 'reports'

urlpatterns = [
    path('job/<slug:slug>/', views.report_job_view, name='report_job'),
    path('company/<slug:slug>/', views.report_company_view, name='report_company'),
]
