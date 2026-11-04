from django.shortcuts import render
from .models import FAQ


def faq_list(request):
    """Public FAQ page grouped by category."""
    faqs = FAQ.objects.filter(is_active=True)
    # Group by category for display
    grouped = {}
    category_labels = dict(FAQ.CATEGORY_CHOICES)
    for faq in faqs:
        label = category_labels.get(faq.category, faq.category)
        grouped.setdefault(label, []).append(faq)
    return render(request, 'faqs/faq_list.html', {'grouped': grouped})

