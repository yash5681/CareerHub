from django.urls import path
from apps.applications import views

app_name = 'applications'

urlpatterns = [
    path('apply/<slug:slug>/', views.apply_job_view, name='apply'),
    path('my/', views.seeker_applications_list_view, name='seeker_list'),
    path('my/<int:pk>/withdraw/', views.seeker_withdraw_application_view, name='withdraw'),
    path('recruiter/', views.recruiter_applications_list_view, name='recruiter_list'),
    path('recruiter/<int:pk>/', views.recruiter_application_detail_view, name='recruiter_detail'),
    path('recruiter/<int:pk>/status/<str:new_status>/', views.recruiter_quick_status_view, name='quick_status'),
]
