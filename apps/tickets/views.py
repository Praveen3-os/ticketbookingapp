import logging
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Movie, Theater, ShowTime, Booking, SupportTicket
from .forms import SupportTicketForm

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
    """Visual seat selection & show timings for a showtime."""
    showtime = get_object_or_404(ShowTime, pk=showtime_id, is_active=True)

    # Fetch other available show timings for the same movie on this date
    other_showtimes = ShowTime.objects.filter(
        movie=showtime.movie,
        theater=showtime.theater,
        show_date=showtime.show_date,
        is_active=True,
    ).order_by('show_time')

    # Collect already booked seat numbers
    booked_bookings = Booking.objects.filter(showtime=showtime, status='confirmed')
    booked_seats = set()
    for b in booked_bookings:
        if b.seat_numbers:
            for s in b.seat_numbers.split(','):
                booked_seats.add(s.strip().upper())

    # Pre-occupy a few random seats for realism if none booked yet
    if not booked_seats:
        sample_occupied = ['A4', 'B3', 'B7', 'C5', 'C6', 'D2', 'D8', 'E5', 'F6']
        booked_seats = set(sample_occupied)

    # Rows A through F, columns 1 to 10
    rows = ['A', 'B', 'C', 'D', 'E', 'F']
    cols = list(range(1, 11))

    return render(request, 'tickets/select_seats.html', {
        'showtime': showtime,
        'other_showtimes': other_showtimes,
        'booked_seats': list(booked_seats),
        'rows': rows,
        'cols': cols,
    })


@login_required
def book_showtime(request, showtime_id):
    """Handle booking submission with seat selection & payment."""
    showtime = get_object_or_404(ShowTime, pk=showtime_id, is_active=True)
    if request.method == 'POST':
        seat_numbers_raw = request.POST.get('seat_numbers', '').strip()
        payment_method = request.POST.get('payment_method', 'Google Pay (UPI)')

        seats_list = [s.strip().upper() for s in seat_numbers_raw.split(',') if s.strip()]
        seat_count = len(seats_list) if seats_list else int(request.POST.get('seats', 1))

        if not seats_list:
            seats_list = [f"A{i+1}" for i in range(seat_count)]
            seat_numbers_raw = ', '.join(seats_list)

        with transaction.atomic():
            st = ShowTime.objects.select_for_update().get(pk=showtime_id)
            if st.available_seats < seat_count:
                messages.error(
                    request,
                    f'❌ Error SEAT-001: Seats are no longer available for this showtime. '
                    'Please select different seats or another show timing.'
                )
                return redirect('tickets:select_seats', showtime_id=showtime_id)

            booking = Booking.objects.create(
                user=request.user,
                showtime=st,
                seats=seat_count,
                seat_numbers=seat_numbers_raw,
                total_price=st.price * seat_count,
                payment_method=payment_method,
                status='confirmed',
            )
            st.available_seats -= seat_count
            st.save(update_fields=['available_seats'])

        messages.success(request, f'🎟️ Tickets Booked! Reference: {booking.booking_ref} | Seats: {booking.seat_numbers}')
        return redirect('tickets:booking_detail', ref=booking.booking_ref)

    return redirect('tickets:select_seats', showtime_id=showtime_id)


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
            messages.success(request, f'✅ Booking {booking.booking_ref} cancelled. Refund of ₹{booking.total_price} will be credited to {booking.payment_method} in 3-5 days.')
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
