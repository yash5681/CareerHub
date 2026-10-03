from django.urls import path
from apps.jobs import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list_view, name='list'),
    path('categories/', views.categories_list_view, name='categories'),
    path('create/', views.job_create_view, name='create'),
    path('manage/', views.manage_jobs_view, name='manage_jobs'),
    path('saved/', views.saved_jobs_view, name='saved_jobs'),
    path('alerts/', views.job_alerts_view, name='alerts'),
    path('alerts/<int:pk>/delete/', views.delete_job_alert_view, name='delete_alert'),
    path('recommended/', views.recommended_jobs_view, name='recommended'),
    path('<int:job_id>/save/', views.toggle_save_job_view, name='toggle_save'),
    path('<slug:slug>/', views.job_detail_view, name='detail'),
    path('<slug:slug>/edit/', views.job_edit_view, name='edit'),
]
