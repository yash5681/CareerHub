from django.urls import path
from apps.blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list_view, name='list'),
    path('<slug:slug>/', views.blog_detail_view, name='detail'),
]
