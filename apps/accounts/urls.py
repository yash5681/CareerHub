from django.urls import path
from apps.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/seeker/', views.register_seeker_view, name='register_seeker'),
    path('register/recruiter/', views.register_recruiter_view, name='register_recruiter'),
    path('profile/', views.seeker_profile_view, name='seeker_profile'),
    path('profile/edit/', views.edit_seeker_profile_view, name='edit_seeker_profile'),
    
    # Nested profile items
    path('profile/education/add/', views.add_education_view, name='add_education'),
    path('profile/education/<int:pk>/delete/', views.delete_education_view, name='delete_education'),
    path('profile/experience/add/', views.add_experience_view, name='add_experience'),
    path('profile/experience/<int:pk>/delete/', views.delete_experience_view, name='delete_experience'),
    path('profile/project/add/', views.add_project_view, name='add_project'),
    path('profile/project/<int:pk>/delete/', views.delete_project_view, name='delete_project'),
    path('profile/certification/add/', views.add_certification_view, name='add_certification'),
    path('profile/certification/<int:pk>/delete/', views.delete_certification_view, name='delete_certification'),
    
    path('settings/', views.account_settings_view, name='settings'),
]
