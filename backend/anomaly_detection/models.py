from django.db import models
from ingestion.models import OperationalData


class AnomalyRecord(models.Model):
    """Records anomalies detected by the ML pipeline."""
    ALGORITHM_CHOICES = [
        ('isolation_forest', 'Isolation Forest'),
        ('zscore', 'Z-Score'),
        ('combined', 'Combined'),
    ]
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    data_record = models.ForeignKey(
        OperationalData,
        on_delete=models.CASCADE,
        related_name='anomalies',
    )
    algorithm = models.CharField(max_length=30, choices=ALGORITHM_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    anomaly_score = models.FloatField(help_text="Score from the detection algorithm")
    affected_fields = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True, default='')
    is_acknowledged = models.BooleanField(default=False)
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'anomaly_records'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['severity']),
            models.Index(fields=['algorithm']),
        ]

    def __str__(self):
        return f"Anomaly [{self.severity}] on record {self.data_record_id}"
