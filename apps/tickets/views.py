import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Movie, Theater, ShowTime, Booking, SupportTicket
from .forms import BookingForm, SupportTicketForm

logger = logging.getLogger(__name__)


def movie_list(request):
    """Browse all Tamil movies now showing."""
    genre = request.GET.get('genre', '')
    movies = Movie.objects.filter(is_active=True)
    if genre:
        movies = movies.filter(genre=genre)
    return render(request, 'tickets/movie_list.html', {
        'movies': movies,
        'genres': Movie.GENRE_CHOICES,
        'selected_genre': genre,
    })


def movie_detail(request, pk):
    """Movie detail — pick theater & showtime."""
    movie = get_object_or_404(Movie, pk=pk, is_active=True)
    showtimes = ShowTime.objects.filter(
        movie=movie, is_active=True
    ).select_related('theater').order_by('show_date', 'show_time')

    # Group by date → theater
    grouped = {}
    for st in showtimes:
        date_key = st.show_date
        grouped.setdefault(date_key, {})
        grouped[date_key].setdefault(st.theater, []).append(st)

    return render(request, 'tickets/movie_detail.html', {
        'movie': movie,
        'grouped_shows': grouped,
    })


def select_seats(request, showtime_id):
    """Select number of seats for a showtime."""
    showtime = get_object_or_404(ShowTime, pk=showtime_id, is_active=True)
    form = BookingForm()
    return render(request, 'tickets/select_seats.html', {
        'showtime': showtime,
        'form': form,
    })


@login_required
def book_showtime(request, showtime_id):
    """Handle booking submission."""
    showtime = get_object_or_404(ShowTime, pk=showtime_id, is_active=True)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            seats = form.cleaned_data['seats']
            with transaction.atomic():
                st = ShowTime.objects.select_for_update().get(pk=showtime_id)
                if st.available_seats < seats:
                    messages.error(
                        request,
                        f'❌ Error SEAT-001: Only {st.available_seats} seat(s) remaining for this show. '
                        'Please reduce seat count or pick another showtime.'
                    )
                    return redirect('tickets:select_seats', showtime_id=showtime_id)

                booking = Booking.objects.create(
                    user=request.user,
                    showtime=st,
                    seats=seats,
                    total_price=st.price * seats,
                    status='confirmed',
                )
                st.available_seats -= seats
                st.save(update_fields=['available_seats'])

            messages.success(request, f'🎬 Booking confirmed! Ref: {booking.booking_ref}')
            return redirect('tickets:booking_detail', ref=booking.booking_ref)
    else:
        form = BookingForm()

    return render(request, 'tickets/select_seats.html', {'showtime': showtime, 'form': form})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related(
        'showtime__movie', 'showtime__theater'
    )
    return render(request, 'tickets/my_bookings.html', {'bookings': bookings})


@login_required
def booking_detail(request, ref):
    booking = get_object_or_404(Booking, booking_ref=ref, user=request.user)
    return render(request, 'tickets/booking_detail.html', {'booking': booking})


@login_required
def cancel_booking(request, ref):
    booking = get_object_or_404(Booking, booking_ref=ref, user=request.user)
    if request.method == 'POST':
        if booking.status == 'confirmed':
            with transaction.atomic():
                booking.status = 'cancelled'
                booking.save(update_fields=['status'])
                st = ShowTime.objects.select_for_update().get(pk=booking.showtime_id)
                st.available_seats += booking.seats
                st.save(update_fields=['available_seats'])
            messages.success(request, '✅ Booking cancelled. Refund will be processed in 3-5 days.')
        else:
            messages.warning(request, 'This booking cannot be cancelled.')
        return redirect('tickets:my_bookings')
    return render(request, 'tickets/cancel_confirm.html', {'booking': booking})


def support_ticket_create(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            messages.success(request, f'Support ticket created: {ticket.ticket_ref}')
            return redirect('tickets:support_success', ref=ticket.ticket_ref)
    else:
        form = SupportTicketForm()
    return render(request, 'tickets/support_ticket.html', {'form': form})


def support_success(request, ref):
    ticket = get_object_or_404(SupportTicket, ticket_ref=ref)
    return render(request, 'tickets/support_success.html', {'ticket': ticket})
