from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    """A Tamil movie that can be booked."""
    LANGUAGE_CHOICES = [
        ('tamil', 'Tamil'),
        ('tamil_dubbed', 'Tamil Dubbed'),
    ]
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('drama', 'Drama'),
        ('comedy', 'Comedy'),
        ('thriller', 'Thriller'),
        ('romance', 'Romance'),
        ('horror', 'Horror'),
        ('sci_fi', 'Sci-Fi'),
        ('family', 'Family'),
    ]
    CERT_CHOICES = [
        ('U', 'U'),
        ('UA', 'U/A'),
        ('A', 'A'),
    ]
    title = models.CharField(max_length=200)
    title_tamil = models.CharField(max_length=200, blank=True, help_text='Title in Tamil script')
    description = models.TextField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='action')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='tamil')
    certificate = models.CharField(max_length=5, choices=CERT_CHOICES, default='UA')
    director = models.CharField(max_length=150)
    cast = models.CharField(max_length=500, help_text='Comma-separated cast names')
    duration_mins = models.PositiveIntegerField(default=150, help_text='Runtime in minutes')
    release_date = models.DateField()
    poster_emoji = models.CharField(max_length=10, default='🎬', help_text='Emoji fallback')
    poster_image = models.CharField(max_length=100, blank=True, default='', help_text='File in static/img/posters/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_date']
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'

    def __str__(self):
        return f"{self.title} ({self.release_date.year})"

    @property
    def duration_display(self):
        h, m = divmod(self.duration_mins, 60)
        return f"{h}h {m}m"

    @property
    def poster_static_path(self):
        if self.poster_image:
            return f"img/posters/{self.poster_image}"
        return ""


class Theater(models.Model):
    """A cinema theater / screen."""
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100, default='Coimbatore')
    total_seats = models.PositiveIntegerField(default=150)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['city', 'name']

    def __str__(self):
        return f"{self.name}, {self.location}"


class ShowTime(models.Model):
    """A specific show of a movie at a theater."""
    SHOW_CHOICES = [
        ('morning', '10:00 AM (FDFS)'),
        ('matinee', '01:30 PM'),
        ('first_show', '04:30 PM'),
        ('second_show', '07:30 PM'),
        ('night', '10:30 PM'),
    ]
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='showtimes')
    show_date = models.DateField()
    show_label = models.CharField(max_length=20, choices=SHOW_CHOICES)
    show_time = models.TimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=150.00)
    available_seats = models.PositiveIntegerField(default=150)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['show_date', 'show_time']
        unique_together = ('movie', 'theater', 'show_date', 'show_label')

    def __str__(self):
        return f"{self.movie.title} @ {self.theater.name} – {self.show_date} {self.get_show_label_display()}"

    @property
    def is_sold_out(self):
        return self.available_seats == 0

    @property
    def is_filling_fast(self):
        return 0 < self.available_seats <= 20


class Booking(models.Model):
    """A ticket booking linking a user to a showtime."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('upi_gpay', 'Google Pay (UPI)'),
        ('upi_phonepe', 'PhonePe (UPI)'),
        ('upi_paytm', 'Paytm (UPI)'),
        ('card', 'Credit / Debit Card'),
        ('netbanking', 'Net Banking'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE, related_name='bookings')
    seats = models.PositiveIntegerField(default=1)
    seat_numbers = models.CharField(max_length=150, default='', help_text='e.g. A3, A4, B6')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='Google Pay (UPI)')
    payment_id = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    booking_ref = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.booking_ref} – {self.user} – {self.showtime.movie.title}"

    def save(self, *args, **kwargs):
        if not self.booking_ref:
            import uuid
            self.booking_ref = 'TIX-' + str(uuid.uuid4()).replace('-', '').upper()[:8]
        if not self.payment_id:
            import uuid
            self.payment_id = 'PAY-' + str(uuid.uuid4()).replace('-', '').upper()[:10]
        if not self.total_price:
            self.total_price = self.showtime.price * self.seats
        super().save(*args, **kwargs)


class SupportTicket(models.Model):
    """Created by AI assistant when it cannot answer a question."""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    description = models.TextField()
    original_question = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    ticket_ref = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.ticket_ref}] {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_ref:
            import uuid
            self.ticket_ref = 'SUP-' + str(uuid.uuid4()).replace('-', '').upper()[:8]
        super().save(*args, **kwargs)
