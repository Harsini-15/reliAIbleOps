from django.contrib import admin
from .models import ReliabilityScore

@admin.register(ReliabilityScore)
class ReliabilityScoreAdmin(admin.ModelAdmin):
    list_display = ['data_record', 'overall_score', 'completeness_score', 'consistency_score', 'calculated_at']
    list_filter = ['overall_score']
