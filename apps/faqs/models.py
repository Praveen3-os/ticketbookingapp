from django.db import models


class FAQ(models.Model):
    """Frequently Asked Question stored in SQL, used by AI assistant."""
    CATEGORY_CHOICES = [
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('account', 'Account'),
        ('events', 'Events'),
        ('errors', 'Error Codes'),
        ('general', 'General'),
    ]
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question[:80]

