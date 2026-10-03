from django.urls import path
from apps.interviews import views

app_name = 'interviews'

urlpatterns = [
    path('schedule/<int:application_id>/', views.schedule_interview_view, name='schedule'),
    path('recruiter/', views.recruiter_interviews_list_view, name='recruiter_list'),
    path('my/', views.seeker_interviews_list_view, name='seeker_list'),
]
