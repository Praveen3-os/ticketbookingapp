import uuid
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .service import handle_chat, log_feedback

logger = logging.getLogger(__name__)


def _get_session_id(request):
    if 'chat_session_id' not in request.session:
        request.session['chat_session_id'] = str(uuid.uuid4())
    return request.session['chat_session_id']


@csrf_exempt
@require_POST
def chat(request):
    """Main chat API endpoint."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_message = (body.get('message') or '').strip()
    if not user_message:
        return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

    if len(user_message) > 1000:
        return JsonResponse({'error': 'Message too long (max 1000 characters).'}, status=400)

    session_id = _get_session_id(request)
    user_name = body.get('name', '')
    user_email = body.get('email', '')

    result = handle_chat(
        user_message=user_message,
        session_id=session_id,
        user_name=user_name,
        user_email=user_email,
    )
    return JsonResponse({
        'reply': result['reply'],
        'source': result.get('source', 'unknown'),
        'ticket_ref': result.get('ticket_ref'),
        'show_payment_action': result.get('show_payment_action', False),
        'message_id': str(uuid.uuid4()),
    })


@csrf_exempt
@require_POST
def instant_pay(request):
    """Allows booking & instant simulated payment directly through the AI chat widget!"""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    from apps.tickets.models import Movie, ShowTime, Booking

    movie_id = body.get('movie_id')
    seats_count = int(body.get('seats', 2))
    payment_method = body.get('payment_method', 'Google Pay (UPI)')

    if movie_id:
        showtime = ShowTime.objects.filter(movie_id=movie_id, is_active=True).first()
    else:
        showtime = ShowTime.objects.filter(is_active=True).first()

    if not showtime:
        return JsonResponse({'error': 'No showtimes available for booking.'}, status=404)

    user = request.user if request.user.is_authenticated else User.objects.filter(is_staff=True).first()
    if not user:
        user = User.objects.first()

    seat_letters = ['C', 'D', 'E', 'B']
    cols = [4, 5, 6, 7]
    allocated_seats = [f"{seat_letters[i % len(seat_letters)]}{cols[i % len(cols)]}" for i in range(seats_count)]
    seat_str = ', '.join(allocated_seats)

    total_price = showtime.price * seats_count

    booking = Booking.objects.create(
        user=user,
        showtime=showtime,
        seats=seats_count,
        seat_numbers=seat_str,
        total_price=total_price,
        payment_method=payment_method,
        status='confirmed',
    )
    showtime.available_seats = max(0, showtime.available_seats - seats_count)
    showtime.save(update_fields=['available_seats'])

    return JsonResponse({
        'status': 'success',
        'booking_ref': booking.booking_ref,
        'payment_id': booking.payment_id,
        'movie_title': showtime.movie.title,
        'theater': showtime.theater.name,
        'timing': f"{showtime.show_date.strftime('%d %b')} at {showtime.show_time.strftime('%I:%M %p')}",
        'seats': booking.seat_numbers,
        'total': float(total_price),
        'payment_method': payment_method,
    })


@csrf_exempt
@require_POST
def feedback(request):
    """Store thumbs-up / thumbs-down feedback in MongoDB."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    session_id = _get_session_id(request)
    log_feedback(
        session_id=session_id,
        message_id=body.get('message_id', ''),
        rating=body.get('rating', ''),
        comment=body.get('comment', ''),
    )
    return JsonResponse({'status': 'ok'})
