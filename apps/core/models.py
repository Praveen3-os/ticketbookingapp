from django.db import models


class RequestLog(models.Model):
    """Stores every HTTP request for auditing."""
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=512)
    status_code = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    response_time_ms = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Request Log'
        verbose_name_plural = 'Request Logs'

    def __str__(self):
        return f"{self.method} {self.path} [{self.status_code}] @ {self.created_at:%Y-%m-%d %H:%M}"


class ErrorCode(models.Model):
    """HTTP & site-specific error codes with explanations."""
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_site_specific = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Error Code'
        verbose_name_plural = 'Error Codes'

    def __str__(self):
        return f"{self.code} – {self.title}"

