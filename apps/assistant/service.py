"""
AI Assistant service layer for CineTix Tamil Movie Ticket Booking.
- Searches FAQ database for matching answers.
- Searches Tamil Movies & Error codes.
- Falls back to OpenAI if no FAQ match found.
- Creates a SupportTicket in SQL when it cannot answer.
- Logs every chat exchange + feedback in MongoDB.
"""
import logging
import difflib
from datetime import datetime

from django.conf import settings

logger = logging.getLogger(__name__)


# ── MongoDB helper ──────────────────────────────────────────────────────────

def _get_mongo_collection(collection_name: str):
    try:
        from pymongo import MongoClient
        client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
        db = client[settings.MONGO_DB_NAME]
        return db[collection_name]
    except Exception as exc:
        logger.warning("MongoDB unavailable: %s", exc)
        return None


def log_chat(session_id: str, user_message: str, assistant_reply: str, source: str):
    col = _get_mongo_collection('chat_logs')
    if col is None:
        return
    try:
        col.insert_one({
            'session_id': session_id,
            'user_message': user_message,
            'assistant_reply': assistant_reply,
            'source': source,
            'timestamp': datetime.utcnow(),
        })
    except Exception as exc:
        logger.warning("Failed to log chat to MongoDB: %s", exc)


def log_feedback(session_id: str, message_id: str, rating: str, comment: str):
    col = _get_mongo_collection('feedback')
    if col is None:
        return
    try:
        col.insert_one({
            'session_id': session_id,
            'message_id': message_id,
            'rating': rating,
            'comment': comment,
            'timestamp': datetime.utcnow(),
        })
    except Exception as exc:
        logger.warning("Failed to log feedback to MongoDB: %s", exc)


# ── FAQ and Movie search ───────────────────────────────────────────────────

def _search_faqs_and_movies(user_question: str, threshold: float = 0.45):
    """Return matching answer from Error Codes, Movie DB, or FAQs."""
    from apps.faqs.models import FAQ
    from apps.core.models import ErrorCode
    from apps.tickets.models import Movie, Theater

    q_lower = user_question.lower()

    # 1. Check error codes by keyword first (e.g. 404, 500, SEAT-001)
    for ec in ErrorCode.objects.all():
        if ec.code.lower() in q_lower or ec.title.lower() in q_lower:
            return (
                f"**Error {ec.code} – {ec.title}**\n\n{ec.description}",
                'error_code',
            )

    # 2. Check movie title queries (e.g. "is Leo playing?", "Jailer director")
    for m in Movie.objects.filter(is_active=True):
        if m.title.lower() in q_lower or (m.title_tamil and m.title_tamil in user_question):
            return (
                f"🎬 **{m.title}** ({m.title_tamil or ''})\n\n"
                f"• **Genre:** {m.get_genre_display()} | **Cert:** {m.certificate} | **Runtime:** {m.duration_display}\n"
                f"• **Director:** {m.director}\n"
                f"• **Cast:** {m.cast}\n\n"
                f"{m.description}\n\n"
                f"👉 You can book tickets now from the 'Now Showing' section!",
                'movie_db',
            )

    # 3. Check theater queries
    for t in Theater.objects.filter(is_active=True):
        if t.name.lower() in q_lower:
            return (
                f"🏛️ **{t.name}** is located at **{t.location}, {t.city}** with {t.total_seats} seats capacity. "
                "Check the movie detail page to pick showtimes for this theater!",
                'theater_db',
            )

    # 4. Fuzzy-match against FAQ questions
    faqs = list(FAQ.objects.filter(is_active=True))
    if faqs:
        questions = [f.question for f in faqs]
        matches = difflib.get_close_matches(user_question, questions, n=1, cutoff=threshold)
        if matches:
            faq = next(f for f in faqs if f.question == matches[0])
            return faq.answer, 'faq'

        # Substring / keyword match in FAQs
        words = [w for w in q_lower.split() if len(w) > 3]
        for faq in faqs:
            if any(w in faq.question.lower() or w in faq.answer.lower() for w in words):
                return faq.answer, 'faq_substring'

    return None, None


# ── OpenAI fallback ─────────────────────────────────────────────────────────

def _ask_openai(user_question: str, faq_context: str) -> str:
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        return None

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        system_prompt = (
            "You are CineBot, the smart AI assistant for CineTix, a premier Tamil movie ticket booking platform in Chennai, India. "
            "You help users with Tamil movie info, showtimes, Chennai theaters (Rohini, Sathyam, AGS, Kamala, etc.), "
            "ticket bookings, cancellations, UPI/card payments, and explaining error codes like SEAT-001. "
            "You understand both English and Tanglish / Tamil queries. Be concise, enthusiastic, and polite.\n\n"
            f"Here are our FAQs and context:\n{faq_context}"
        )
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_question},
            ],
            max_tokens=300,
            timeout=10,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("OpenAI call failed: %s", exc)
        return None


# ── Support ticket creation ─────────────────────────────────────────────────

def _create_support_ticket(name: str, email: str, question: str) -> str:
    from apps.tickets.models import SupportTicket
    ticket = SupportTicket.objects.create(
        name=name or 'Cinema Fan',
        email=email or 'user@cinetix.example',
        subject=f"Customer query: {question[:100]}",
        description=question,
        original_question=question,
        priority='medium',
    )
    return ticket.ticket_ref


# ── Main chat handler ───────────────────────────────────────────────────────

def handle_chat(user_message: str, session_id: str,
                user_name: str = '', user_email: str = '') -> dict:
    answer, source = _search_faqs_and_movies(user_message)

    if answer:
        log_chat(session_id, user_message, answer, source)
        return {'reply': answer, 'source': source}

    # Context build
    from apps.faqs.models import FAQ
    faqs = FAQ.objects.filter(is_active=True).values('question', 'answer')
    faq_context = '\n'.join(f"Q: {f['question']}\nA: {f['answer']}" for f in faqs)

    ai_answer = _ask_openai(user_message, faq_context)
    if ai_answer:
        log_chat(session_id, user_message, ai_answer, 'openai')
        return {'reply': ai_answer, 'source': 'openai'}

    # Support ticket creation fallback
    ticket_ref = _create_support_ticket(user_name, user_email, user_message)
    reply = (
        "I'm sorry, I couldn't find an answer to your question. "
        f"I have automatically created a support ticket **{ticket_ref}** for our CineTix team. "
        "We'll review your question and get back to you shortly!"
    )
    log_chat(session_id, user_message, reply, 'ticket')
    return {'reply': reply, 'source': 'ticket', 'ticket_ref': ticket_ref}
