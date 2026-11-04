"""
URL configuration for ticketsite project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('tickets/', include('apps.tickets.urls')),
    path('assistant/', include('apps.assistant.urls')),
    path('faq/', include('apps.faqs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.core.views.custom_404'
handler500 = 'apps.core.views.custom_500'

