from django.db import migrations


FAQS = [
    # Booking
    ('How do I book a Tamil movie ticket?', 'Browse movies on the "Now Showing" page, select a movie, choose your preferred theater and showtime in Chennai, pick the number of seats, and click "Book Now". You must be logged in to complete the booking.', 'booking', 1),
    ('Can I book multiple seats at once?', 'Yes, you can book up to 10 seats per transaction. For group bookings of more than 10, please contact our support team.', 'booking', 2),
    ('How do I cancel my booking?', 'Go to "My Bookings", find the booking and click "Cancel". Cancellations are allowed up to 2 hours before the showtime. A full refund will be processed within 3-5 business days.', 'booking', 3),
    ('Where can I find my booking reference?', 'Your booking reference (e.g., TIX-XXXXXXXX) is shown on the confirmation page after booking. It is also available under "My Bookings" when you log in.', 'booking', 4),
    ('Which theaters in Chennai do you support?', 'We support popular Chennai theaters including Rohini Silver Screens (Koyambedu), SPI Sathyam Cinemas (Royapettah), AGS Cinemas (T. Nagar), Kamala Cinemas (Vadapalani), Kasi Theatre, PVR SKLS Galaxy Mall, INOX National, Vetri Theatre, Udhayam Theatre, and Devi Theatre Complex.', 'booking', 5),
    # Payment
    ('What payment methods do you accept?', 'We accept all major credit/debit cards (Visa, Mastercard, RuPay), UPI (GPay, PhonePe, Paytm), and net banking from all Indian banks.', 'payment', 1),
    ('Is my payment information secure?', 'Yes. All payments are processed through PCI-DSS compliant gateways. We never store your card details on our servers. UPI transactions are secured by NPCI standards.', 'payment', 2),
    ('Will I get a refund if I cancel?', 'Yes, refunds are processed within 3-5 business days to your original payment method, provided you cancel at least 2 hours before the showtime.', 'payment', 3),
    # Account
    ('How do I create an account?', 'Click "Login" in the top navigation, then select "Register". Fill in your name, email, and password. You can start booking immediately after registration.', 'account', 1),
    ('I forgot my password. What do I do?', 'Click "Forgot Password" on the login page and enter your email. You will receive a password reset link within a few minutes.', 'account', 2),
    # Movies
    ('How do I know which Tamil movies are showing now?', 'Visit the "Now Showing" page — it lists all currently running Tamil movies with details like director, cast, genre, duration, and certificate. You can filter by genre.', 'events', 1),
    ('What does FDFS mean?', 'FDFS stands for First Day First Show — typically the earliest morning show (10:00 AM) on a movie\'s release day. These are extremely popular for Rajini, Vijay, and Ajith releases and tend to sell out fast!', 'events', 2),
    # Errors
    ('What does error SEAT-001 mean?', 'SEAT-001 means the seats you selected were just booked by another user. This often happens during high-demand releases. Please go back and choose a different showtime or reduce seat count.', 'errors', 1),
    ('What does error 404 mean?', 'A 404 error means the page you requested could not be found. The movie may have been removed from listings or the URL is incorrect. Use the navigation menu to browse current movies.', 'errors', 2),
]


def seed_faqs(apps, schema_editor):
    FAQ = apps.get_model('faqs', 'FAQ')
    for question, answer, cat, order in FAQS:
        FAQ.objects.get_or_create(
            question=question,
            defaults={'answer': answer, 'category': cat, 'order': order, 'is_active': True},
        )


def unseed(apps, schema_editor):
    FAQ = apps.get_model('faqs', 'FAQ')
    FAQ.objects.filter(question__in=[f[0] for f in FAQS]).delete()


class Migration(migrations.Migration):
    dependencies = [('faqs', '0001_initial')]
    operations = [migrations.RunPython(seed_faqs, unseed)]
