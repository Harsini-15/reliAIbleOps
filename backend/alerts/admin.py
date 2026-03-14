from django.contrib import admin
from .models import AlertLog

@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'source', 'is_resolved', 'created_at']
    list_filter = ['level', 'is_resolved']
    search_fields = ['title', 'message']
