from django.urls import path
from apps.companies import views

app_name = 'companies'

urlpatterns = [
    path('', views.company_list_view, name='list'),
    path('my-company/', views.my_company_view, name='my_company'),
    path('<slug:slug>/', views.company_detail_view, name='detail'),
    path('<slug:slug>/review/', views.add_company_review_view, name='add_review'),
]
