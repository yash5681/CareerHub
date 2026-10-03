from django.urls import path
from apps.messaging import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('<int:conversation_id>/', views.inbox_view, name='chat'),
    path('<int:conversation_id>/send/', views.send_message_view, name='send'),
    path('start/<int:recipient_id>/', views.start_conversation_view, name='start'),
]
