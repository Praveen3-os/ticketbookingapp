from django.contrib import admin
from .models import Movie, Theater, ShowTime, Booking, SupportTicket


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'title_tamil', 'genre', 'director', 'certificate', 'duration_mins', 'release_date', 'is_active')
    list_filter = ('genre', 'language', 'certificate', 'is_active')
    search_fields = ('title', 'title_tamil', 'director', 'cast')


@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'city', 'total_seats', 'is_active')
    list_filter = ('city', 'is_active')


@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'theater', 'show_date', 'show_label', 'show_time', 'price', 'available_seats')
    list_filter = ('show_date', 'show_label', 'theater')
    search_fields = ('movie__title',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'user', 'showtime', 'seats', 'total_price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('booking_ref', 'user__username')
    readonly_fields = ('booking_ref', 'created_at', 'updated_at')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_ref', 'name', 'email', 'subject', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('ticket_ref', 'name', 'email', 'subject')
    readonly_fields = ('ticket_ref', 'created_at', 'updated_at')
