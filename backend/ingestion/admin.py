from django.contrib import admin
from .models import OperationalData, SystemMetric


@admin.register(OperationalData)
class OperationalDataAdmin(admin.ModelAdmin):
    list_display = ['source_name', 'source_type', 'timestamp', 'cpu_usage', 'temperature', 'is_validated']
    list_filter = ['source_type', 'is_validated']
    search_fields = ['source_name']
    date_hierarchy = 'timestamp'


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_name', 'metric_value', 'unit', 'source', 'timestamp']
    list_filter = ['metric_name', 'source']
