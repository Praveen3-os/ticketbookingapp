from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('show/<int:showtime_id>/', views.select_seats, name='select_seats'),
    path('show/<int:showtime_id>/book/', views.book_showtime, name='book_showtime'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('booking/<str:ref>/', views.booking_detail, name='booking_detail'),
    path('cancel/<str:ref>/', views.cancel_booking, name='cancel_booking'),
    path('support/', views.support_ticket_create, name='support_ticket'),
    path('support/success/<str:ref>/', views.support_success, name='support_success'),
]
