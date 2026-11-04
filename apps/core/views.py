import requests
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from apps.core.models import RequestLog, ErrorCode

logger = logging.getLogger(__name__)

FEATURES = [
    ('🎬', 'Latest Tamil Movies', 'Leo, Jailer, Ponniyin Selvan, Vidaamuyarchi — all the biggest Kollywood hits.'),
    ('🏛️', 'Top Chennai Theaters', 'Rohini, Sathyam, AGS, Kamala, Kasi, PVR — all your favourite screens.'),
    ('⚡', 'Instant FDFS Booking', 'Grab First Day First Show tickets the moment they go live.'),
    ('🤖', 'CineBot AI Assistant', '24/7 help — FAQs, error codes, and instant support ticket creation.'),
    ('♻️', 'Easy Cancellation', 'Cancel up to 2 hours before showtime for a full refund.'),
    ('📱', 'Mobile Friendly', 'Book from any device — our site works perfectly on mobile.'),
]

ABOUT_STATS = [
    ('🎬', '50,000+', 'Tickets Booked'),
    ('🎥', '10+', 'Tamil Movies'),
    ('🏛️', '10', 'Chennai Theaters'),
    ('⭐', '4.9/5', 'User Rating'),
]

TECH_STACK = [
    ('Backend', 'Django 4.2, Python 3.9'),
    ('Frontend', 'Vanilla JS, CSS3 (dark theme, responsive)'),
    ('SQL DB', 'SQLite (dev) / PostgreSQL (prod)'),
    ('NoSQL DB', 'MongoDB — chat logs & feedback'),
    ('AI', 'OpenAI GPT-3.5-turbo + FAQ fuzzy matching'),
    ('Hosting', 'Gunicorn + WhiteNoise + HTTPS'),
]


def home(request):
    from apps.tickets.models import Movie
    latest_movies = Movie.objects.filter(is_active=True)[:6]
    weather = _get_weather('Chennai')
    return render(request, 'core/home.html', {
        'latest_movies': latest_movies,
        'weather': weather,
        'features': FEATURES,
    })


def about(request):
    return render(request, 'core/about.html', {'stats': ABOUT_STATS, 'stack': TECH_STACK})


def contact(request):
    return render(request, 'core/contact.html')


def health(request):
    from django.db import connection
    db_ok = False
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        pass
    return JsonResponse({
        'status': 'ok' if db_ok else 'degraded',
        'database': 'connected' if db_ok else 'error',
        'version': '1.0.0',
    }, status=200 if db_ok else 503)


def request_logs_view(request):
    if not request.user.is_staff:
        return custom_404(request, None)
    logs = RequestLog.objects.all()[:200]
    return render(request, 'core/request_logs.html', {'logs': logs})


def error_codes_view(request):
    codes = ErrorCode.objects.all()
    return render(request, 'core/error_codes.html', {'codes': codes})


def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    return render(request, 'errors/500.html', status=500)


def _get_weather(city: str) -> dict:
    api_key = settings.WEATHER_API_KEY
    timeout = getattr(settings, 'WEATHER_API_TIMEOUT', 5)
    if not api_key:
        return _weather_fallback(city, reason='no_api_key')
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return {
            'city': data['name'], 'temp': round(data['main']['temp']),
            'description': data['weather'][0]['description'].title(),
            'icon': data['weather'][0]['icon'], 'source': 'live',
        }
    except requests.Timeout:
        logger.warning("Weather API timed out for city=%s", city)
        return _weather_fallback(city, reason='timeout')
    except Exception as exc:
        logger.warning("Weather API error: %s", exc)
        return _weather_fallback(city, reason='error')


def _weather_fallback(city: str, reason: str) -> dict:
    return {'city': city, 'temp': '--', 'description': 'Weather unavailable', 'icon': '01d', 'source': 'fallback', 'reason': reason}
