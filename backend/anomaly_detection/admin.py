from django.contrib import admin
from .models import AnomalyRecord

@admin.register(AnomalyRecord)
class AnomalyRecordAdmin(admin.ModelAdmin):
    list_display = ['data_record', 'algorithm', 'severity', 'anomaly_score', 'is_acknowledged', 'detected_at']
    list_filter = ['severity', 'algorithm', 'is_acknowledged']
