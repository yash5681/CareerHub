from django.urls import path
from apps.core import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('privacy-policy/', views.privacy_view, name='privacy'),
    path('privacy/', views.privacy_view),
    path('terms-of-service/', views.terms_view, name='terms'),
    path('terms/', views.terms_view),
    path('cookie-policy/', views.cookies_view, name='cookies'),
    path('newsletter/subscribe/', views.newsletter_subscribe_view, name='newsletter_subscribe'),
]
