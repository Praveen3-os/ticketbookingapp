from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('health/', views.health, name='health'),
    path('error-codes/', views.error_codes_view, name='error_codes'),
    path('admin/request-logs/', views.request_logs_view, name='request_logs'),
]

