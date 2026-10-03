from django.urls import path
from apps.notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_list_view, name='list'),
    path('read/<int:pk>/', views.read_notification_view, name='read'),
    path('mark-all-read/', views.mark_all_notifications_read_view, name='mark_all_read'),
]
