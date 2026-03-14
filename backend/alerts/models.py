from django.db import models


class AlertLog(models.Model):
    """System alert logs for anomalies and operational issues."""
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    title = models.CharField(max_length=300)
    message = models.TextField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='warning')
    source = models.CharField(max_length=100, default='system')
    related_anomaly_id = models.IntegerField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'alert_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.level.upper()}] {self.title}"
