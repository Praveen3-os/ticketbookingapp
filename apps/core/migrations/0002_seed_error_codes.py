from django.db import migrations


ERROR_CODES = [
    ('400', 'Bad Request',
     'The server cannot process your request due to invalid data. Please check all fields and try again.',
     False),
    ('401', 'Unauthorized',
     'You need to log in to perform this action. Please sign in with your CineTix account.',
     False),
    ('403', 'Forbidden',
     'You do not have permission to access this resource. Contact support if you believe this is an error.',
     False),
    ('404', 'Not Found',
     'The page or movie you are looking for cannot be found. It may have been removed or the URL is incorrect.',
     False),
    ('429', 'Too Many Requests',
     'You have sent too many requests. Please wait a moment before trying again. This protects against bot bookings.',
     False),
    ('500', 'Internal Server Error',
     'Something went wrong on our end. Our team has been notified. Please try again later or contact support.',
     False),
    ('503', 'Service Unavailable',
     'CineTix is temporarily unavailable due to maintenance or high traffic. Please try again in a few minutes.',
     False),
    ('SEAT-001', 'Seat Already Booked',
     'The seat(s) you selected were just booked by another user. This is common during high-demand releases like Rajini and Vijay movies. Please go back, choose a different showtime or reduce the seat count.',
     True),
]


def seed_error_codes(apps, schema_editor):
    ErrorCode = apps.get_model('core', 'ErrorCode')
    for code, title, desc, site_specific in ERROR_CODES:
        ErrorCode.objects.get_or_create(
            code=code,
            defaults={'title': title, 'description': desc, 'is_site_specific': site_specific},
        )


def unseed(apps, schema_editor):
    ErrorCode = apps.get_model('core', 'ErrorCode')
    ErrorCode.objects.filter(code__in=[c[0] for c in ERROR_CODES]).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [migrations.RunPython(seed_error_codes, unseed)]
