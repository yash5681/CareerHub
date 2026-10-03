from django.urls import path
from apps.payments import views

app_name = 'payments'

urlpatterns = [
    path('pricing/', views.pricing_page_view, name='pricing'),
    path('plans/', views.pricing_page_view),
    path('order/<slug:plan_slug>/', views.create_order_view, name='create_order'),
    path('verify/', views.verify_payment_view, name='verify_payment'),
    path('my-plan/', views.recruiter_plan_view, name='recruiter_plan'),
]
