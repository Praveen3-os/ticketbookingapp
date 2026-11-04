from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('instant_pay/', views.instant_pay, name='instant_pay'),
    path('feedback/', views.feedback, name='feedback'),
]
