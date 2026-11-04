from django.contrib import admin
from .models import RequestLog, ErrorCode


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('method', 'path', 'status_code', 'ip_address', 'response_time_ms', 'created_at')
    list_filter = ('method', 'status_code')
    search_fields = ('path', 'ip_address')
    readonly_fields = ('created_at',)


@admin.register(ErrorCode)
class ErrorCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'is_site_specific', 'created_at')
    list_filter = ('is_site_specific',)
    search_fields = ('code', 'title')

