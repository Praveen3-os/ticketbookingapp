import uuid
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from .service import handle_chat, log_feedback

logger = logging.getLogger(__name__)


def _get_session_id(request):
    if 'chat_session_id' not in request.session:
        request.session['chat_session_id'] = str(uuid.uuid4())
    return request.session['chat_session_id']


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
        'message_id': str(uuid.uuid4()),
    })


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

