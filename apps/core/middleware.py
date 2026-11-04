import time
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Logs every request's method, path, status code, IP, and response time."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        elapsed = (time.monotonic() - start) * 1000  # ms

        ip = (
            request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            or request.META.get('REMOTE_ADDR', '')
        )

        logger.info(
            "%s %s %s %.1fms %s",
            request.method,
            request.path,
            response.status_code,
            elapsed,
            ip,
        )

        # Async-safe: use try/except to skip DB write if migrations haven't run
        try:
            from apps.core.models import RequestLog
            RequestLog.objects.create(
                method=request.method,
                path=request.path[:512],
                status_code=response.status_code,
                ip_address=ip or None,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                response_time_ms=round(elapsed, 2),
            )
        except Exception:
            pass

        return response

