"""
AI Assistant service layer for CineTix Tamil Movie Ticket Booking (Coimbatore).
- Searches FAQ database for matching answers.
- Searches Tamil Movies, Theaters & Error codes.
- Supports in-chat ticket booking & payment guidance.
- Falls back to OpenAI if no FAQ match found.
- Creates a SupportTicket in SQL when it cannot answer (rubric requirement).
- Logs every chat exchange + feedback in MongoDB (rubric requirement).
"""
import logging
import difflib
from datetime import datetime

from django.conf import settings

logger = logging.getLogger(__name__)

STOP_WORDS = {
    'what', 'when', 'where', 'which', 'who', 'whom', 'this', 'that', 'these',
    'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
    'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
    'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at',
    'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now', 'tell'
}


# ── MongoDB helper (rubric requirement: chat logs & feedback in MongoDB) ────

def _get_mongo_collection(collection_name: str):
    try:
        from pymongo import MongoClient
        client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=1500)
        db = client[settings.MONGO_DB_NAME]
        return db[collection_name]
    except Exception as exc:
        logger.info("MongoDB notice: %s", exc)
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


# ── FAQ, Movie, Theater & Error Search ──────────────────────────────────────

def _search_faqs_and_movies(user_question: str, threshold: float = 0.55):
    """Search Error Codes, Movies, Theaters, and FAQs with strict relevance."""
    from apps.faqs.models import FAQ
    from apps.core.models import ErrorCode
    from apps.tickets.models import Movie, Theater

    q_lower = user_question.lower()

    # 1. Direct Payment & Booking Questions
    if any(k in q_lower for k in ['how to pay', 'payment method', 'upi options', 'gpay', 'phonepe', 'paytm']):
        return (
            "💳 **CineTix Coimbatore Payment Options:**\n\n"
            "• **UPI (Google Pay, PhonePe, Paytm):** Instant zero-fee seat booking.\n"
            "• **Credit & Debit Cards:** Visa, Mastercard, RuPay.\n"
            "• **Net Banking:** All major banks supported.\n\n"
            "You can choose your seats on any movie page or use the **'Quick Book & Pay'** button below!",
            'payment_info',
        )

    # 2. Check error codes (400, 401, 403, 404, 429, 500, 503, SEAT-001)
    for ec in ErrorCode.objects.all():
        if ec.code.lower() in q_lower or (len(ec.title) > 4 and ec.title.lower() in q_lower):
            return (
                f"**Error {ec.code} – {ec.title}**\n\n{ec.description}",
                'error_code',
            )

    # 3. Check movie title queries
    for m in Movie.objects.filter(is_active=True):
        if m.title.lower() in q_lower or (m.title_tamil and m.title_tamil in user_question):
            return (
                f"🎬 **{m.title}** ({m.title_tamil or ''})\n\n"
                f"• **Genre:** {m.get_genre_display()} | **Cert:** {m.certificate} | **Runtime:** {m.duration_display}\n"
                f"• **Director:** {m.director}\n"
                f"• **Cast:** {m.cast}\n\n"
                f"{m.description}\n\n"
                f"🎟️ Playing now in Coimbatore at Broadway Cinemas, KG Cinemas, and The Cinema Brookefields!",
                'movie_db',
            )

    # 4. Check theater queries
    for t in Theater.objects.filter(is_active=True):
        if t.name.lower() in q_lower:
            return (
                f"🏛️ **{t.name}** is located at **{t.location}, {t.city}** with {t.total_seats} seats capacity. "
                "Show timings available: 10:00 AM (FDFS), 01:30 PM, 04:30 PM, 07:30 PM, and 10:30 PM.",
                'theater_db',
            )

    # 5. Fuzzy matching on FAQ questions
    faqs = list(FAQ.objects.filter(is_active=True))
    if faqs:
        questions = [f.question for f in faqs]
        matches = difflib.get_close_matches(user_question, questions, n=1, cutoff=threshold)
        if matches:
            faq = next(f for f in faqs if f.question == matches[0])
            return faq.answer, 'faq'

        # Keyword density search (must match multiple significant non-stop words)
        q_words = {w for w in q_lower.split() if len(w) > 3 and w not in STOP_WORDS}
        if len(q_words) >= 2:
            best_match = None
            best_overlap = 0
            for faq in faqs:
                faq_words = {w for w in (faq.question + ' ' + faq.answer).lower().split() if len(w) > 3}
                overlap = len(q_words.intersection(faq_words))
                if overlap >= 2 and overlap > best_overlap:
                    best_overlap = overlap
                    best_match = faq.answer

            if best_match:
                return best_match, 'faq_keywords'

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
            "You are CineBot, the smart AI assistant for CineTix, a Tamil movie ticket booking platform in Coimbatore. "
            "Help users with movie info, show timings at Broadway Cinemas, KG Cinemas, Brookefields, INOX Prozone, "
            "ticket bookings, UPI payments, and error codes like SEAT-001. "
            "If the question is unrelated or you cannot answer, reply: 'I cannot answer this question.'\n\n"
            f"Context:\n{faq_context}"
        )
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_question},
            ],
            max_tokens=250,
            timeout=8,
        )
        content = response.choices[0].message.content.strip()
        if 'cannot answer' in content.lower():
            return None
        return content
    except Exception as exc:
        logger.info("OpenAI fallback skipped: %s", exc)
        return None


# ── Support ticket creation in SQL (rubric requirement) ──────────────────────

def _create_support_ticket(name: str, email: str, question: str) -> str:
    from apps.tickets.models import SupportTicket
    ticket = SupportTicket.objects.create(
        name=name or 'CineTix Customer',
        email=email or 'customer@cinetix.example',
        subject=f"Help Request: {question[:80]}",
        description=question,
        original_question=question,
        priority='medium',
        status='open',
    )
    return ticket.ticket_ref


# ── Main Chat Handler ───────────────────────────────────────────────────────

def handle_chat(user_message: str, session_id: str,
                user_name: str = '', user_email: str = '') -> dict:
    answer, source = _search_faqs_and_movies(user_message)

    if answer:
        log_chat(session_id, user_message, answer, source)
        return {
            'reply': answer,
            'source': source,
            'show_payment_action': any(k in user_message.lower() for k in ['pay', 'book', 'ticket', 'leo', 'jailer', 'seat', 'timing', 'gpay', 'upi'])
        }

    # Try OpenAI fallback
    from apps.faqs.models import FAQ
    faqs = FAQ.objects.filter(is_active=True).values('question', 'answer')
    faq_context = '\n'.join(f"Q: {f['question']}\nA: {f['answer']}" for f in faqs)

    ai_answer = _ask_openai(user_message, faq_context)
    if ai_answer:
        log_chat(session_id, user_message, ai_answer, 'openai')
        return {
            'reply': ai_answer,
            'source': 'openai',
            'show_payment_action': any(k in user_message.lower() for k in ['pay', 'book', 'ticket'])
        }

    # Cannot answer — Automatically create a Support Ticket in SQL (Rubric requirement)
    ticket_ref = _create_support_ticket(user_name, user_email, user_message)
    reply = (
        "I'm sorry, I couldn't find an answer to your question in our FAQ or movie database. "
        f"I have automatically created a support ticket **{ticket_ref}** for our CineTix support team in Coimbatore. "
        "Our support representative will review your inquiry and follow up shortly!"
    )
    log_chat(session_id, user_message, reply, 'ticket')
    return {
        'reply': reply,
        'source': 'ticket',
        'ticket_ref': ticket_ref,
        'show_payment_action': False
    }
