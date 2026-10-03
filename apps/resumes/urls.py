from django.urls import path
from apps.resumes import views

app_name = 'resumes'

urlpatterns = [
    path('', views.resume_list_view, name='my_resumes'),
    path('upload/', views.resume_upload_view, name='upload'),
    path('builder/', views.resume_builder_view, name='builder'),
    path('<int:pk>/preview/', views.resume_preview_view, name='preview'),
    path('<int:pk>/set-primary/', views.set_primary_resume_view, name='set_primary'),
    path('<int:pk>/delete/', views.delete_resume_view, name='delete'),
]
